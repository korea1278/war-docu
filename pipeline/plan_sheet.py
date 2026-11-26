"""비트 시트 + 자료 체크리스트 (2026-11-26 '다큐 설명 영상 스킬' 튜토리얼 분석에서 가져옴 · war-docu·map-of-war 공통)

스토리보드를 사람이 한눈에 검토할 수 있게 두 장의 표로 뽑는다. 렌더·API 호출 없음(0원), 세션에서 바로 돌린다.
  1. episodes/<ep>/beats.md  — 장면마다 [시각 | 나레이션(자막) | 화면 | 출처 번호]
     · 숫자가 들어간 문장인데 출처(src)가 없으면 ⚠️ · research.md에 없는 출처 번호면 ⚠️
  2. episodes/<ep>/assets.md — 장면마다 필요한 자료(사료 사진·재연 그림·사용자 제공 자료)와 '필수/선택 · 없으면 무엇으로 대체'
     · 사진 장면에 핀(photo_pins.json)이 없으면 ⚠️ (자동 검색으로 엉뚱한 사진이 들어옴)

스토리보드 장면 필드 (선택):
  "src": [1, 3]                       → research.md 의 [1]·[3] 출처
  "need": {"what": "1982. 5. 4 더 선 1면 캡처", "required": false, "fallback": "document 카드로 요점만"}
                                       → 사용자가 구해 줘야 하는 자료 (기사 캡처·영상 클립 등)
research.md 형식은 docs/DOCU_SKILL_STANDARD.md 참고 ([번호] 제목 — URL 줄을 출처로 읽음)

사용: python3 plan_sheet.py <ep>
"""
import json
import re
import sys

from common import ROOT, ep_dirs, line_say, line_text, load_board, read_json

CPS = 7.6  # 승현 v3 실측 공백 포함 초당 글자 (EP34) — timeline.json이 없을 때 시각 추정용


def vis_summary(sc) -> str:
    v = sc.get("visual", {})
    t = v.get("type", "?")
    bits = [t]
    if t == "map":
        if v.get("flight"):
            bits.append("비행 " + "→".join(v["flight"]))
        elif v.get("from"):
            bits.append(f"{v.get('from')}→{v.get('to', v.get('from'))}")
        ks = [it.get("k") for it in v.get("items", [])]
        if ks:
            bits.append("·".join(dict.fromkeys(ks)))
    elif t in ("photo",):
        bits.append(v.get("q", ""))
    elif t == "ai":
        bits.append(v.get("img", ""))
    elif t == "globe":
        bits.append(f"항로 {len(v.get('route', []))}점")
        if v.get("counter"):
            c = v["counter"]
            bits.append(f"{c.get('to')}{c.get('unit', '')}")
    elif t == "weapon":
        bits.append("·".join(u.get("kind", "?") for u in v.get("units", [])))
    elif t == "punch":
        bits.append(f"「{v.get('text', '')}」")
    elif v.get("title"):
        bits.append(str(v["title"])[:20])
    if v.get("counters") or v.get("counter") and t != "globe":
        bits.append("+카운터")
    if isinstance(v.get("stamp"), dict):
        bits.append(f"+도장「{v['stamp'].get('text')}」")
    if sc.get("clip"):
        bits.append("+인용카드" + ("(재구성)" if sc["clip"].get("recreated") else ""))
    if sc.get("hook"):
        bits.append("+후킹")
    return " ".join(b for b in bits if b)


def main(ep):
    board = load_board(ep)
    src_dir, out = ep_dirs(ep)
    res = (src_dir / "research.md").read_text(encoding="utf-8") if (src_dir / "research.md").exists() else ""
    known = set(re.findall(r"^\s*[-*]?\s*\[(\d+)\]", res, re.M))
    conflicts = 0
    m = re.search(r"^##\s*숫자 충돌.*?$(.*?)(^##|\Z)", res, re.M | re.S)
    if m:
        conflicts = len([l for l in m.group(1).splitlines() if l.strip().startswith(("-", "*"))])
    tl = read_json(out / "timeline.json", None)
    real = {s["id"]: s["start"] for s in tl["scenes"]} if tl else {}
    pins = read_json(src_dir / "photo_pins.json", {})
    ai_prompts = board.get("ai_images", {})
    ai_have = read_json(out / "ai.json", {})

    beats, assets, warn = [], [], []
    t = 0.0
    for sc in board["scenes"]:
        sid = sc["id"]
        disp = " ".join(line_text(l) for l in sc.get("lines", []))
        say = " ".join(line_say(l) for l in sc.get("lines", []))
        st = real.get(sid, t)
        t = st + len(say) / CPS + 0.5
        srcs = sc.get("src") or []
        if isinstance(srcs, (int, str)):
            srcs = [srcs]
        mark = ""
        if re.search(r"\d", disp) and not srcs:
            mark = " ⚠️출처없음"
            warn.append(f"{sid}: 숫자가 있는데 출처(src) 없음 — 「{disp[:40]}」")
        bad = [str(x) for x in srcs if known and str(x) not in known]
        if bad:
            mark += " ⚠️research.md에 없음:" + ",".join(bad)
            warn.append(f"{sid}: 출처 번호 {','.join(bad)}가 research.md에 없음")
        src_txt = ",".join(f"[{x}]" for x in srcs)
        beats.append(f"| {sid} | {int(st // 60)}:{st % 60:04.1f} | {disp.replace('|', '/')} | {vis_summary(sc).replace('|', '/')} | {src_txt}{mark} |")

        # 자료 체크리스트
        vlist = [sc.get("visual", {})] + list(sc.get("visuals", []))
        for v in vlist:
            if v.get("type") == "photo":
                q = v.get("q", "")
                pin = pins.get(f"{q}#0") or pins.get(q)
                ok = "✅ 핀" if pin else "⚠️ 핀 없음(자동 검색 — 엉뚱한 사진 위험)"
                if not pin:
                    warn.append(f"{sid}: 사진 핀 없음 ({q})")
                assets.append(f"| {sid} | 사료 사진 | 필수 | {pin or q} | {ok} | 지도·문서 카드로 대체 |")
            elif v.get("type") == "ai":
                img = v.get("img", "")
                have = "✅ 있음(재사용 0원)" if img in ai_have else ("🆕 새로 그림(무료 Cloudflare 한도 확인)" if img in ai_prompts else "⚠️ 프롬프트 없음")
                assets.append(f"| {sid} | 재연 그림 | 필수 | {img} | {have} | 무료 대체 → 자리 표시 그림 |")
        need = sc.get("need")
        if need:
            req = "필수" if need.get("required") else "선택"
            assets.append(f"| {sid} | 사용자 제공 | {req} | {need.get('what', '')} | ⏳ 받을 것 | {need.get('fallback', '없으면 이 장면은 지도·카드로')} |")

    head = f"# {ep} 비트 시트 — {board.get('title', '')}\n\n출처 {len(known)}개 · 숫자 충돌 {conflicts}건 · 경고 {len(warn)}개 · 시각은 {'실제 timeline' if tl else f'추정(초당 {CPS}자)'}\n\n"
    head += "| 장면 | 시각 | 나레이션(자막) | 화면 | 출처 |\n|---|---|---|---|---|\n"
    (src_dir / "beats.md").write_text(head + "\n".join(beats) + "\n", encoding="utf-8")
    ah = f"# {ep} 자료 체크리스트\n\n| 장면 | 종류 | 필수/선택 | 자료 | 상태 | 없을 때 대체 |\n|---|---|---|---|---|---|\n"
    (src_dir / "assets.md").write_text(ah + "\n".join(assets) + "\n", encoding="utf-8")
    print(f"beats.md {len(beats)}장면 · assets.md {len(assets)}항목 · 출처 {len(known)}개 · 숫자 충돌 {conflicts}건")
    if not res:
        print("⚠️ research.md 없음 — 대본 전에 리서치 브리프부터 (docs/DOCU_SKILL_STANDARD.md)")
    for w in warn[:60]:
        print("⚠️", w)
    if len(warn) > 60:
        print(f"... 외 {len(warn) - 60}개")


if __name__ == "__main__":
    main(sys.argv[1])
