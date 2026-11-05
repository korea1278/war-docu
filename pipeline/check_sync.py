"""음성–자막 싱크 검증 (EP19~ 사용자 지시: 마지막 단어 발음 시점과 자막 종료 시간 오차 ±1.0초 이내)

python pipeline/check_sync.py <ep>
- 장면마다 나레이션 MP3에서 실제 목소리가 끝나는 시점(ffmpeg silencedetect로 끝부분 무음 제외)과
  그 장면 마지막 자막(chunk)의 종료 시간을 비교한다.
- 영상 전체의 마지막 자막 종료 시간(SRT와 같은 값)과 마지막 목소리 시점도 따로 비교한다.
- 하나라도 1.0초를 넘으면 exit 1 (Actions가 MP4 렌더 전에 멈춤). 결과는 logs/sync_check_<ep>.txt
"""
import re
import subprocess
import sys

from common import ROOT, ep_dirs, read_json

LIMIT = 1.0


def voice_end(mp3):
    """MP3 안에서 목소리가 끝나는 시점(초): 끝부분 무음 구간을 빼고 계산."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp3), "-af", "silencedetect=noise=-38dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    h, mi, se = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    dur = int(h) * 3600 + int(mi) * 60 + float(se)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    # 마지막 무음이 파일 끝까지 이어지면(끝 무음) 그 시작점이 목소리 끝
    if starts and (len(ends) < len(starts) or ends[-1] >= dur - 0.05):
        return starts[-1], dur
    return dur, dur


def main(ep):
    _, out = ep_dirs(ep)
    tl = read_json(out / "timeline.json")
    rows, bad = [], []
    last_voice_abs = last_sub_abs = 0.0
    for sc in tl["scenes"]:
        if not sc.get("audio") or not sc["lines"]:
            continue
        mp3 = ROOT / "public" / sc["audio"]
        ve, dur = voice_end(mp3)
        ve_rel = sc["audioAt"] + ve
        sub_end = max(c["end"] for l in sc["lines"] for c in l["chunks"])
        diff = sub_end - ve_rel
        last_voice_abs = sc["start"] + ve_rel
        last_sub_abs = sc["start"] + sub_end
        flag = "" if abs(diff) <= LIMIT else "  ← 초과"
        rows.append(f"{sc['id']:>5}  목소리 끝 {ve_rel:7.2f}s  자막 끝 {sub_end:7.2f}s  오차 {diff:+.2f}s{flag}")
        if flag:
            bad.append(sc["id"])
    # 영상 전체 마지막 자막(SRT는 +0.15초 여유)과 마지막 목소리
    srt_end = last_sub_abs + 0.15
    fd = srt_end - last_voice_abs
    rows.append(f"\n[전체] 마지막 목소리 {last_voice_abs:.2f}s · 마지막 자막(SRT) 종료 {srt_end:.2f}s · 오차 {fd:+.2f}s"
                f" · 영상 끝 {tl['duration']:.2f}s")
    if abs(fd) > LIMIT:
        bad.append("마지막 자막")
    head = f"{ep} 음성–자막 싱크 검사 (허용 ±{LIMIT:.1f}초): {'통과' if not bad else '실패 — ' + ', '.join(bad)}"
    (ROOT / "logs" / f"sync_check_{ep}.txt").write_text(head + "\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print(head)
    if bad:
        from common import log_error
        log_error(f"{ep}: 음성–자막 싱크 오차 1초 초과 — {', '.join(bad)} (logs/sync_check_{ep}.txt)")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
