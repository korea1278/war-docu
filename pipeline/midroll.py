"""20분 장편용: 챕터 시작 시각(설명글 목차)과 미드롤 광고 위치를 timeline.json에서 계산.

python pipeline/midroll.py incheon
 - 목차: 각 PART 첫 장면의 실제 시작 시각 (SRT와 같은 기준)
 - 미드롤: 스토리보드 "midrolls"에 적은 장면 id의 '시작 직전 장면 간격' 시각 (장면이 바뀌는 무음 구간)
   → 유튜브 스튜디오 > 수익 창출 > 광고 시점에 그대로 입력
결과: logs/midroll_<ep>.txt
"""
import sys

from common import ROOT, ep_dirs, load_board, read_json


def mmss(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}" if t < 3600 else f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}"


def main(ep):
    board = load_board(ep)
    _, out = ep_dirs(ep)
    tl = read_json(out / "timeline.json")
    sc = {s["id"]: s for s in tl["scenes"]}
    rows = [f"{ep} · 러닝타임 {mmss(tl['duration'])}", "", "[목차 — 설명글용]", "0:00 오프닝"]
    for s in tl["scenes"]:
        if s.get("chapter"):
            rows.append(f"{mmss(s['start'])} {s['chapter']['num']} · {s['chapter']['title']}")
    rows += ["", "[미드롤 광고 위치 — 장면 전환 무음 구간]"]
    for mid in board.get("midrolls", []):
        s = sc[mid]
        prev = tl["scenes"][tl["scenes"].index(s) - 1]
        last = prev["lines"][-1]["end"] if prev["lines"] else 0
        gap_at = prev["start"] + last + 0.15  # 앞 장면 마지막 대사가 끝난 직후
        rows.append(f"{mmss(gap_at)}  ({mid} 앞 · {s.get('chapter', {}).get('title', '')})")
    txt = "\n".join(rows)
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / f"midroll_{ep}.txt").write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main(sys.argv[1])
