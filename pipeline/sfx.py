"""ElevenLabs 효과음(sound-generation) + 배경음악(music) 생성.

python pipeline/sfx.py yongmunsan sfx     # 효과음 (스토리보드에서 쓰는 것만)
python pipeline/sfx.py yongmunsan music   # 배경음악 (timeline.json 필요)
효과음은 public/sfx 에 공용 캐시되어 다른 에피소드에서도 재사용됩니다.
"""
import json
import sys

from common import ROOT, ep_dirs, env, load_board, read_json, retry, session

SFX = {
    "wind": ("cold mountain wind howling at night, eerie ambient, no music", 7),
    "bugle": ("distant military bugle call echoing across dark mountains at night, 1950s Korean War, eerie", 5),
    "heartbeat": ("slow heavy tense heartbeat, cinematic, low", 6),
    "hit": ("deep cinematic impact hit, trailer boom, short", 2),
    "boom": ("massive cinematic braam impact with long reverb tail", 4),
    "water": ("calm lake water gently lapping on a pebble shore, quiet ambience", 8),
    "drum": ("single deep war drum hit with short reverb", 1.5),
    "artillery_far": ("distant artillery barrage rumbling at night, war ambience, muffled explosions", 8),
    "artillery": ("howitzer cannon firing nearby, loud boom with echo in mountains", 3),
    "charge": ("crowd of soldiers shouting battle cry while charging, distant, war", 5),
    "mg": ("machine gun bursts firing in a mountain battle, 1950s, with echoes", 4),
    "typewriter": ("old mechanical typewriter typing quickly, bell at end", 4),
    "clock": ("ticking clock, tense, close", 6),
    "tank": ("tank engine rumble and metal tracks moving, 1950s", 6),
    "birds": ("morning birds chirping by a quiet misty lake, peaceful", 8),
    "whoosh": ("fast cinematic whoosh transition", 1.2),
    "pop": ("soft short UI pop, subtle", 0.5),
}

MUSIC = {
    "drone": "Dark ambient cinematic drone, low sustained strings and sub bass, tense and mysterious, sparse, no percussion, war documentary underscore, instrumental",
    "theme": "Solemn cinematic war documentary main theme, cello melody over soft piano and strings, slow tempo, emotional and dignified, instrumental",
    "tension": "Tense war documentary underscore, low pulsing strings ostinato, deep taiko drums slowly building, dark, instrumental, no vocals",
    "march": "Rising determined orchestral underscore, military snare drum pattern, low brass and strings, counterattack momentum, documentary, instrumental",
    "analysis": "Calm analytical documentary underscore, soft felt piano with subtle ticking pulse and light strings, minimal, thoughtful, instrumental",
    "somber": "Melancholic elegy, slow solo piano with warm strings, reflective and sorrowful, documentary ending, instrumental",
}


def used_sfx(board):
    ids = {"whoosh", "pop"}
    for sc in board["scenes"]:
        for x in sc.get("sfx", []):
            ids.add(x["id"])
    return ids


def gen_sfx(ep):
    key = env("ELEVENLABS_API_KEY", required=True)
    board = load_board(ep)
    d = ROOT / "public" / "sfx"
    d.mkdir(parents=True, exist_ok=True)
    s = session()
    for sid in sorted(used_sfx(board)):
        p = d / f"{sid}.mp3"
        if p.exists():
            continue
        prompt, dur = SFX[sid]
        print(f"SFX {sid}")

        def call():
            r = s.post(
                "https://api.elevenlabs.io/v1/sound-generation",
                headers={"xi-api-key": key},
                json={"text": prompt, "duration_seconds": dur, "prompt_influence": 0.45},
                timeout=120,
            )
            if r.status_code >= 400:
                raise RuntimeError(f"{r.status_code} {r.text[:300]}")
            return r.content

        try:
            p.write_bytes(retry(call, tries=3, label=f"sfx {sid}"))
        except Exception as e:  # 효과음 실패는 치명적이지 않음
            print(f"  ! 효과음 {sid} 건너뜀: {e}")


def gen_music(ep):
    key = env("ELEVENLABS_API_KEY", required=True)
    _, out = ep_dirs(ep)
    tl = read_json(out / "timeline.json")
    if not tl:
        sys.exit("timeline.json 먼저 생성하세요 (timeline.py)")
    d = out / "music"
    d.mkdir(exist_ok=True)
    s = session()
    no_api = env("NO_MUSIC_API", "1") == "1"  # 기본: 기존 음원만 재사용 (API 호출 금지)
    for cue in tl["music"]:
        p = d / f"{cue['id']}.mp3"
        if p.exists():
            continue
        if no_api:
            print(f"  · 음악 {cue['id']} 파일 없음 — NO_MUSIC_API=1 이므로 생성하지 않음")
            continue
        length = int(min(max(cue["dur"] + 6, 15), 290) * 1000)
        print(f"MUSIC {cue['id']} {length / 1000:.0f}s")

        def call():
            r = s.post(
                "https://api.elevenlabs.io/v1/music",
                headers={"xi-api-key": key},
                json={"prompt": MUSIC[cue["id"]], "music_length_ms": length, "model_id": "music_v1"},
                timeout=600,
            )
            if r.status_code >= 400:
                raise RuntimeError(f"{r.status_code} {r.text[:300]}")
            return r.content

        try:
            p.write_bytes(retry(call, tries=2, label=f"music {cue['id']}"))
        except Exception as e:
            print(f"  ! 배경음악 {cue['id']} 생성 실패 → 음악 없이 진행: {e}")


if __name__ == "__main__":
    ep, what = sys.argv[1], sys.argv[2]
    gen_sfx(ep) if what == "sfx" else gen_music(ep)
