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


def main(ep):
    key = env("ELEVENLABS_API_KEY", required=True)
    voice = env("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE
    model = env("ELEVENLABS_MODEL") or "eleven_multilingual_v2"
    settings = {
        "stability": float(env("TTS_STABILITY", "0.55")),
        "similarity_boost": float(env("TTS_SIMILARITY", "0.8")),
        "style": float(env("TTS_STYLE", "0.15")),
        "use_speaker_boost": True,
        "speed": float(env("TTS_SPEED", "1.0")),
    }
    board = load_board(ep)
    _, out = ep_dirs(ep)
    adir = out / "tts"
    adir.mkdir(exist_ok=True)
    s = session()
    scenes = board["scenes"]
    for i, sc in enumerate(scenes):
        text = scene_tts_text(sc)
        sig = hashlib.sha1(json.dumps([text, voice, model, settings], ensure_ascii=False).encode()).hexdigest()[:12]
        meta_p = adir / f"{sc['id']}.json"
        mp3_p = adir / f"{sc['id']}.mp3"
        meta = read_json(meta_p, {})
        if meta.get("sig") == sig and mp3_p.exists():
            continue
        prev_t = scene_tts_text(scenes[i - 1]) if i > 0 else None
        next_t = scene_tts_text(scenes[i + 1]) if i + 1 < len(scenes) else None
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
