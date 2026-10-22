"""API 연결 점검 → logs/api_check.txt (비용 거의 0)."""
import os

from common import ROOT, session

s = session()
out = []
ek = os.environ.get("ELEVENLABS_API_KEY", "")
vid = os.environ.get("ELEVENLABS_VOICE_ID", "")
out.append(f"ELEVENLABS_API_KEY 등록: {'예' if ek else '아니오'} (길이 {len(ek)})")
out.append(f"OPENAI_API_KEY 등록: {'예' if os.environ.get('OPENAI_API_KEY') else '아니오'}")
out.append(f"VOICE_ID: {vid}")
if ek:
    r = s.get("https://api.elevenlabs.io/v1/user/subscription", headers={"xi-api-key": ek}, timeout=30)
    if r.ok:
        j = r.json()
        out.append(f"구독: {j.get('tier')} / 사용 {j.get('character_count')} / 한도 {j.get('character_limit')} / 상태 {j.get('status')}")
    else:
        out.append(f"구독 조회 실패 {r.status_code}: {r.text[:300]}")
    r = s.get(f"https://api.elevenlabs.io/v1/voices/{vid}", headers={"xi-api-key": ek}, timeout=30)
    out.append(f"목소리 조회 {r.status_code}: {r.json().get('name') if r.ok else r.text[:300]}")
    r = s.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps",
               headers={"xi-api-key": ek}, json={"text": "점검입니다.", "model_id": "eleven_multilingual_v2"}, timeout=60)
    out.append(f"TTS 시험 {r.status_code}: {'OK' if r.ok else r.text[:400]}")
ok_ = os.environ.get("OPENAI_API_KEY", "")
if ok_:
    h = {"Authorization": f"Bearer {ok_}"}
    r = s.get("https://api.openai.com/v1/me", headers=h, timeout=30)
    if r.ok:
        j = r.json()
        orgs = [f"{o.get('title') or o.get('name')}({o.get('id')})" for o in j.get("orgs", {}).get("data", [])]
        out.append(f"OpenAI 키 계정: {j.get('email', '?')} / 조직: {', '.join(orgs) or '?'}")
    r = s.post("https://api.openai.com/v1/chat/completions", headers=h, timeout=60,
               json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "ok"}], "max_tokens": 1})
    out.append(f"OpenAI 과금 시험(약 0.0001원) {r.status_code}: {'OK — 크레딧 있음' if r.ok else r.text[:300]}")
gk = os.environ.get("GEMINI_API_KEY", "")
out.append(f"GEMINI_API_KEY 등록: {'예' if gk else '아니오'} (길이 {len(gk)})")
if gk:
    import sys as _s
    _s.path.insert(0, str(ROOT / "pipeline"))
    try:
        from ai_images import gen_gemini
        img = gen_gemini(s, "A small watercolor of a snowy mountain pass at dawn, no text")
        out.append(f"Gemini 그림 시험: OK — {img.size[0]}x{img.size[1]} (약 50원)")
    except Exception as e:  # noqa
        out.append(f"Gemini 그림 시험 실패: {str(e)[:400]}")
(ROOT / "logs").mkdir(exist_ok=True)
(ROOT / "logs" / "api_check.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
