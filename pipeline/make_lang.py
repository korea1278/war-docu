"""한국어 스토리보드 + 번역 맵 → 다른 언어판 스토리보드 생성.

python pipeline/make_lang.py yongmunsan yongmunsan_en en
입력 : episodes/<src>/storyboard.json, episodes/<dst>/translation.json
출력 : episodes/<dst>/storyboard.json  (사진·그림·음악은 원본 에피소드 것을 재사용)
"""
import copy
import json
import sys

from common import ROOT


def main(src, dst, lang):
    kr = json.loads((ROOT / "episodes" / src / "storyboard.json").read_text(encoding="utf-8"))
    tr = json.loads((ROOT / "episodes" / dst / "translation.json").read_text(encoding="utf-8"))
    b = copy.deepcopy(kr)
    b["lang"] = lang
    b["assets_ep"] = src
    b["title"] = tr["title"]
    b["subtitle"] = tr.get("subtitle", "")
    if tr.get("voice"):
        b["voice"] = tr["voice"]
    if tr.get("tempo"):
        b["tempo"] = tr["tempo"]
    for k, name in tr.get("places", {}).items():
        if k in b["places"]:
            b["places"][k][2] = name
    tmap = tr.get("text", {})
    missing = []

    def T(s):
        if s in tmap:
            return tmap[s]
        missing.append(s)
        return s

    for sc in b["scenes"]:
        t = tr["scenes"].get(sc["id"])
        if not t:
            raise SystemExit(f"번역 없음: {sc['id']}")
        if len(t["lines"]) != len(sc["lines"]):
            raise SystemExit(f"{sc['id']}: 줄 수 불일치 (원본 {len(sc['lines'])}, 번역 {len(t['lines'])})")
        sc["lines"] = list(t["lines"])
        sc.pop("tts", None)
        if "label" in sc or "label" in t:
            sc["label"] = t.get("label")
        for i, c in enumerate(sc.get("callouts", [])):
            c["text"] = t["callouts"][i]
            if sc["id"] in tr.get("callout_pos", {}):
                c["pos"] = tr["callout_pos"][sc["id"]]
            if sc["id"] in tr.get("callout_until", {}):
                c["until"] = tr["callout_until"][sc["id"]]
        if sc.get("chapter"):
            sc["chapter"]["num"], sc["chapter"]["title"] = t["chapter"]
        for v in [sc["visual"], *sc.get("visuals", [])]:
            ty = v["type"]
            for i, bub in enumerate(v.get("bubbles", [])):
                bub["text"] = t["bubbles"][i]
            if ty == "map":
                for it in v.get("items", []):
                    if "text" in it:
                        it["text"] = T(it["text"])
            elif ty == "versus":
                v["left"]["label"], v["right"]["label"] = t["left"], t["right"]
            elif ty == "text":
                v["big"] = t["big"]
                if "sub" in v:
                    v["sub"] = t["sub"]
            elif ty == "black":
                v["text"] = t["text"]
                if "accent" in v:
                    v["accent"] = t["accent"]
            elif ty == "titlecard":
                v["title"], v["sub"] = t["title"], t["sub"]
            elif ty == "timeline":
                for it, (d, x) in zip(v["items"], t["items"]):
                    it["date"], it["text"] = d, x
            elif ty == "person":
                v["name"], v["role"] = t["name"], t["role"]
            elif ty == "document":
                for k in ("head", "org", "rows", "note"):
                    v[k] = t[k]
                v["stamp"] = "DECLASSIFIED"
            elif ty == "gauges":
                v["big"] = t["big"]
                for it, x in zip(v["items"], t["items"]):
                    it["label"] = x
            elif ty == "hanja":
                for it, x in zip(v["items"], t["hanja"]):
                    it["r"] = x
            elif ty == "factors":
                v["items"] = t["items"]
                v["head"] = t.get("head", "1 Division vs 3 — Why?")
            elif ty == "chapterbig":
                v["num"], v["title"] = t["num"], t["title"]
            elif ty == "compare":
                v["left"]["title"], v["left"]["big"] = t["left"]
                v["right"]["title"], v["right"]["big"] = t["right"]
            elif ty == "bars":
                v["note"] = t["note"]
                for it, (lab, disp) in zip(v["items"], t["bars"]):
                    it["label"], it["display"] = lab, disp
            elif ty == "weekbar":
                for k in ("title", "markText", "holdText", "days"):
                    v[k] = t[k]
            elif ty == "quotes":
                for it, x in zip(v["items"], t["quotes"]):
                    it["text"] = x
                v["title"] = t.get("quoteTitle")
            elif ty == "profile":
                for k in ("title", "note", "left", "right"):
                    if k in v:
                        v[k] = t[k]
                for it, x in zip(v.get("marks", []), t.get("marks", [])):
                    it["text"] = x
                if v.get("tide") and t.get("tide"):  # EP11 조수 단면 라벨
                    v["tide"]["hiText"], v["tide"]["loText"] = t["tide"]
            elif ty == "endcard":
                v["title"] = t["title"]
    if missing:
        raise SystemExit(f"text 매핑 누락: {sorted(set(missing))}")
    out = ROOT / "episodes" / dst / "storyboard.json"
    out.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{dst}: {len(b['scenes'])}장면 생성 ({lang})")


if __name__ == "__main__":
    main(*sys.argv[1:4])
