"""ElevenLabs 나레이션 생성 (장면별 mp3 + 글자 단위 타임스탬프).

python pipeline/tts.py yongmunsan
환경변수: ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL
"""
import base64
import hashlib
import json
import sys

from common import ep_dirs, env, line_say, load_board, read_json, retry, session, write_json

DEFAULT_VOICE = "pNInz6obpgDQGcFmaJgB"  # Adam (multilingual). 원하는 목소리 ID로 교체 권장


def scene_tts_text(sc):
    if sc.get("tts"):
        return sc["tts"]
    return " ".join(line_say(l).strip() for l in sc["lines"])


def cut_mp3(src, dst, a, b):
    import subprocess
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ss", f"{a:.3f}"]
    if b is not None:
        cmd += ["-to", f"{b:.3f}"]
    subprocess.run(cmd + ["-c:a", "libmp3lame", "-b:a", "192k", str(dst)], check=True)


def main_acts(ep, board, key, voice, model, settings, s, adir):
    """막(act) 단위 생성 (2026-11-12 ep08-chosin 지시서: 문장 단위 쪼개기 금지, 1막 = 통 MP3 1개).
    장면마다 "act": n 을 달면 같은 막 장면들을 이어 붙여 일레븐랩스 1회 호출 → tts/acts/act<n>.mp3 (원본 보존)
    → 글자 타임스탬프로 장면 경계(앞 장면 마지막 글자 끝 ~ 다음 장면 첫 글자 시작의 가운데)를 잘라 장면별 mp3·json을 만든다.
    그래서 tighten·timeline·자막은 기존 그대로 동작하고, 목소리의 호흡·억양은 막 전체로 한 번에 이어진다."""
    acts = {}
    for sc in board["scenes"]:
        if sc["lines"]:
            acts.setdefault(sc["act"], []).append(sc)
    ddir = adir / "acts"
    ddir.mkdir(exist_ok=True)
    order = sorted(acts)
    for n in order:
        group = acts[n]
        texts = [scene_tts_text(sc) for sc in group]
        text = " ".join(texts)
        sig = hashlib.sha1(json.dumps([text, voice, model, settings, "act"], ensure_ascii=False).encode()).hexdigest()[:12]
        mp3_p, meta_p = ddir / f"act{n}.mp3", ddir / f"act{n}.json"
        meta = read_json(meta_p, {})
        if not (meta.get("sig") == sig and mp3_p.exists()):
            body = {"text": text, "model_id": model, "voice_settings": settings}
            i = order.index(n)
            if i > 0:
                body["previous_text"] = " ".join(scene_tts_text(x) for x in acts[order[i - 1]])[-1000:]
            if i + 1 < len(order):
                body["next_text"] = " ".join(scene_tts_text(x) for x in acts[order[i + 1]])[:1000]

            def call():
                r = s.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps",
                    params={"output_format": "mp3_44100_128"},
                    headers={"xi-api-key": key, "Content-Type": "application/json"},
                    json=body,
                    timeout=600,
                )
                if r.status_code >= 400:
                    raise RuntimeError(f"{r.status_code} {r.text[:300]}")
                return r.json()

            print(f"TTS act{n}: {len(group)}장면 · {len(text)}자 (1회 호출)")
            data = retry(call, label=f"tts act{n}")
            mp3_p.write_bytes(base64.b64decode(data["audio_base64"]))
            al = data.get("alignment") or data.get("normalized_alignment")
            meta = {"sig": sig, "text": text, "chars": al["characters"],
                    "starts": al["character_start_times_seconds"], "ends": al["character_end_times_seconds"]}
            write_json(meta_p, meta)
        chars, st, en = meta["chars"], meta["starts"], meta["ends"]
        joined = "".join(chars)
        # 장면별 글자 범위 (정렬 글자열에서 순서대로 찾기 — 보통은 입력 텍스트와 1:1)
        spans, pos = [], 0
        for t in texts:
            j = joined.find(t, pos)
            if j < 0:
                j = pos
            spans.append((j, j + len(t)))
            pos = j + len(t)
        cuts = [0.0]
        for (a0, a1), (b0, _) in zip(spans, spans[1:]):
            end_prev = max(en[a0:a1]) if a1 > a0 else st[a0]
            start_next = st[b0]
            cuts.append((end_prev + start_next) / 2)
        cuts.append(None)
        for k, sc in enumerate(group):
            a, b = cuts[k], cuts[k + 1]
            (c0, c1) = spans[k]
            ssig = hashlib.sha1(f"{sig}|{sc['id']}|{a}|{b}".encode()).hexdigest()[:12]
            sm, sj = adir / f"{sc['id']}.mp3", adir / f"{sc['id']}.json"
            if read_json(sj, {}).get("sig") == ssig and sm.exists():
                continue
            cut_mp3(mp3_p, sm, a, b)
            write_json(sj, {
                "sig": ssig, "text": texts[k], "act": n,
                "chars": chars[c0:c1],
                "starts": [max(0.0, x - a) for x in st[c0:c1]],
                "ends": [max(0.0, x - a) for x in en[c0:c1]],
            })
        print(f"  act{n} → 장면 {len(group)}개로 분할 (원본 tts/acts/act{n}.mp3)")
    print("TTS 완료 (막 단위)")


def main(ep):
    key = env("ELEVENLABS_API_KEY", required=True)
    board = load_board(ep)
    voice = board.get("voice") or env("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE
    model = env("ELEVENLABS_MODEL") or "eleven_multilingual_v2"
    print(f"목소리: {voice} / 모델: {model}")
    settings = {
        "stability": float(env("TTS_STABILITY", "0.55")),
        "similarity_boost": float(env("TTS_SIMILARITY", "0.8")),
        "style": float(env("TTS_STYLE", "0.15")),
        "use_speaker_boost": True,
        "speed": float(env("TTS_SPEED", "1.0")),
    }
    _, out = ep_dirs(ep)
    adir = out / "tts"
    adir.mkdir(exist_ok=True)
    s = session()
    if board.get("tts_mode") == "act":
        return main_acts(ep, board, key, voice, model, settings, s, adir)
    scenes = board["scenes"]
    for i, sc in enumerate(scenes):
        if not sc["lines"]:
            continue
        text = scene_tts_text(sc)
        sig = hashlib.sha1(json.dumps([text, voice, model, settings], ensure_ascii=False).encode()).hexdigest()[:12]
        meta_p = adir / f"{sc['id']}.json"
        mp3_p = adir / f"{sc['id']}.mp3"
        meta = read_json(meta_p, {})
        if meta.get("sig") == sig and mp3_p.exists():
            continue
        prev_t = scene_tts_text(scenes[i - 1]) if i > 0 and scenes[i - 1]["lines"] else None
        next_t = scene_tts_text(scenes[i + 1]) if i + 1 < len(scenes) and scenes[i + 1]["lines"] else None
        body = {"text": text, "model_id": model, "voice_settings": settings}
        if prev_t:
            body["previous_text"] = prev_t
        if next_t:
            body["next_text"] = next_t

        def call():
            r = s.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps",
                params={"output_format": "mp3_44100_128"},
                headers={"xi-api-key": key, "Content-Type": "application/json"},
                json=body,
                timeout=180,
            )
            if r.status_code >= 400:
                raise RuntimeError(f"{r.status_code} {r.text[:300]}")
            return r.json()

        print(f"TTS {sc['id']}: {text[:40]}…")
        data = retry(call, label=f"tts {sc['id']}")
        mp3_p.write_bytes(base64.b64decode(data["audio_base64"]))
        al = data.get("alignment") or data.get("normalized_alignment")
        write_json(meta_p, {
            "sig": sig,
            "text": text,
            "chars": al["characters"],
            "starts": al["character_start_times_seconds"],
            "ends": al["character_end_times_seconds"],
        })
    print("TTS 완료")


if __name__ == "__main__":
    main(sys.argv[1])
