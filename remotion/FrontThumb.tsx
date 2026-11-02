/**
 * '격전의 지도' 썸네일 표준 v3 — '선 넘는 지도' 1티어 레퍼런스 스타일 (2026-11-02 사용자 지정, EP15 낙동강·EP16 도솔산부터)
 *
 * 레이아웃 규격은 레퍼런스(1280×720) 단위로 적고, 출력은 1.5배 확대한 1920×1080.
 *  1 우측 상단 시대 뱃지 — X 1040 · Y 40, 반투명 다크 박스, 흰 굵은 글자 28px
 *  2 컬러 지형(초록·황록, 바다 남색 — public/geo/thumbc/, pipeline/thumb_color.py로 생성)
 *    · 적 공세 영역 = 붉게 달아오른 지형 + 불길·불씨·포연 + 굵은 레드 네온 돌격 화살표
 *    · 아군 방어선·거점 = 형광 블루 #00E5FF 네온 라인 + 빛나는 거점 점
 *    · 지명·좌표 라벨은 전부 숨김
 *    · 하단 40%에 강한 블랙 그라데이션
 *  3 하단 2줄 초대형 타이틀 — Black Han Sans, 하단 중앙 정렬, line-height 1.15
 *    · Line 1 68~72px 흰색 · 5px 검정 외곽선 · 강한 그림자
 *    · Line 2 78~84px 네온 옐로 #FFD000 · 6px 검정 외곽선
 *    · 오른쪽 120px은 유튜브 재생시간 배지(140×50) 자리로 비움
 * 에피소드는 FRONT 표에 한 줄 추가 → Thumbnail A안(ko)이 이 디자인으로 렌더된다.
 */
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile } from "remotion";
import "@fontsource/black-han-sans/400.css";

type LL = [number, number];
export type FrontArrow = { path: LL[]; color?: "red" | "cyan"; w?: number };
export type FrontThumbDef = {
  badge: string; // 우측 상단 시대 뱃지
  rasters: string[]; // 아래→위 순서로 깔 지형 (public/geo/thumbc/<name>.webp)
  view: { center: LL; span: number }; // span = 화면 가로 경도 폭
  front: LL[]; // 아군 방어선 = 붉은 적 영역과 초록 아군 영역의 경계 (형광 블루 네온)
  enemyClose: LL[]; // front 끝점에서 화면 밖을 돌아 시작점으로 돌아가는 점들 → [...front, ...enemyClose] = 적 공세 영역
  fires: LL[]; // 불길 중심점 (적 영역 안, 전선 가까이)
  river?: LL[]; // 강 (푸른 빛 — 방어선과 겹치는 낙동강 등)
  arrows: FrontArrow[];
  points: LL[]; // 아군 거점 (빛나는 점, 라벨 없음)
  line1: string;
  line2: string;
};

/* ===== 에피소드 표 (새 에피소드는 여기 한 줄) ===== */
// 좌표는 각 에피소드 storyboard.json과 동일(개략). 지명 라벨은 레퍼런스 규격대로 표시하지 않는다.
const NAKTONG_FRONT: LL[] = [[129.4, 36.42], [129.2, 36.4], [128.98, 36.42], [128.75, 36.38], [128.52, 36.42], [128.33, 36.4], [128.36, 36.2], [128.39, 36.05], [128.41, 35.95], [128.45, 35.84], [128.42, 35.72], [128.36, 35.68], [128.38, 35.63], [128.35, 35.57], [128.4, 35.5], [128.4, 35.44], [128.43, 35.4], [128.4, 35.33], [128.35, 35.25], [128.37, 35.17], [128.44, 35.1]];
const NAKTONG_RIVER: LL[] = [[128.3056, 36.3601], [128.2867, 36.3491], [128.2836, 36.3307], [128.2888, 36.3144], [128.3362, 36.2886], [128.3426, 36.2656], [128.3372, 36.2471], [128.3455, 36.2365], [128.3628, 36.2184], [128.3637, 36.1968], [128.377, 36.1844], [128.3824, 36.1529], [128.378, 36.1284], [128.3969, 36.1125], [128.3964, 36.0881], [128.3853, 36.074], [128.4058, 36.0374], [128.3996, 36.0225], [128.3986, 36.0154], [128.3917, 35.9819], [128.3966, 35.9419], [128.3992, 35.8935], [128.3856, 35.8689], [128.3901, 35.8534], [128.4443, 35.8472], [128.4604, 35.8404], [128.4652, 35.8363], [128.4791, 35.8192], [128.4711, 35.8092], [128.4231, 35.8087], [128.4011, 35.7843], [128.3855, 35.7596], [128.4169, 35.7341], [128.4297, 35.7259], [128.4345, 35.7085], [128.4173, 35.6937], [128.365, 35.7058], [128.3511, 35.7004], [128.3545, 35.6834], [128.3852, 35.6531], [128.402, 35.6374], [128.3858, 35.6151], [128.3604, 35.6118], [128.3525, 35.6037], [128.3561, 35.5906], [128.3503, 35.5534], [128.3506, 35.5406], [128.3912, 35.5096], [128.4244, 35.4905], [128.42, 35.4755], [128.3828, 35.4581], [128.3748, 35.4469], [128.3887, 35.4259], [128.4219, 35.416], [128.4411, 35.3885], [128.4746, 35.3808], [128.498, 35.3957], [128.5328, 35.3874], [128.5523, 35.3798], [128.5739, 35.3786], [128.5965, 35.3936], [128.6177, 35.3776], [128.6453, 35.3728], [128.6901, 35.3787], [128.7439, 35.3515], [128.7734, 35.3471], [128.7985, 35.3592], [128.8093, 35.3787], [128.8533, 35.3931], [128.8693, 35.3907], [128.879, 35.37], [128.9111, 35.3648], [128.936, 35.3448], [128.9671, 35.3299], [128.9728, 35.3132], [128.9982, 35.2889], [129.0126, 35.275], [128.9987, 35.2359], [128.9896, 35.2037], [128.9629, 35.1845], [128.961, 35.1557], [128.9532, 35.1073]];

export const FRONT: Record<string, FrontThumbDef> = {
  // EP15(사용자 지정 번호) 낙동강 방어선 — 1950년 8월 부산 교두보: 서·북쪽은 불타는 적 공세 영역, 안쪽은 초록 지형 + 형광 블루 방어선
  naktong: {
    badge: "1950년 8월",
    rasters: ["korea", "south"],
    view: { center: [128.8, 35.88], span: 3.3 },
    front: NAKTONG_FRONT,
    enemyClose: [[128.3, 34.4], [126.4, 34.4], [126.4, 37.6], [129.45, 37.6], [129.45, 36.42]],
    fires: [[128.22, 36.3], [128.62, 36.5], [129.05, 36.5], [128.29, 36.08], [128.33, 35.84], [128.27, 35.6], [128.3, 35.36], [127.85, 36.15], [127.8, 35.7], [128.88, 36.52], [128.05, 35.95], [127.6, 36.35], [128.36, 36.46], [128.06, 35.45]],
    river: NAKTONG_RIVER,
    arrows: [
      { path: [[127.15, 36.42], [127.7, 36.34], [128.27, 36.2]], color: "red" },
      { path: [[127.15, 35.98], [127.75, 35.98], [128.33, 35.9]], color: "red" },
      { path: [[127.2, 35.58], [127.75, 35.66], [128.28, 35.62]], color: "red" },
      { path: [[128.6, 36.95], [128.58, 36.72], [128.55, 36.5]], color: "red" },
      { path: [[129.15, 36.95], [129.2, 36.72], [129.24, 36.49]], color: "red" },
    ],
    points: [[128.601, 35.871], [129.04, 35.11], [128.57, 35.21], [129.343, 36.019], [128.555, 36.045], [128.938, 35.973]],
    line1: "서울도 대전도 다 밀렸는데",
    line2: "마지막 '낙동강'이 버틴 이유",
  },
  // EP16 도솔산 전투 (1951년 6월) — 북쪽 능선(북한군 요새)은 포화로 불타는 붉은 영역, 남쪽에서 한국 해병이 형광 블루 화살표로 치고 올라감
  // 좌표는 episodes/ep16-dosolsan/storyboard.json과 동일(개략: 출발선·능선·도솔산 1,148m·대암산)
  "ep16-dosolsan": {
    badge: "1951년 6월",
    rasters: ["yanggu", "dosol_zoom"],
    view: { center: [128.118, 38.205], span: 0.2 },
    front: [[127.98, 38.212], [128.02, 38.216], [128.05, 38.214], [128.075, 38.209], [128.095, 38.212], [128.112, 38.207], [128.128, 38.202], [128.145, 38.207], [128.165, 38.214], [128.19, 38.219], [128.24, 38.224]],
    enemyClose: [[128.4, 38.224], [128.4, 38.4], [127.9, 38.4], [127.9, 38.212]],
    fires: [[128.1, 38.238], [128.135, 38.222], [128.12, 38.228], [128.08, 38.244], [128.155, 38.232], [128.06, 38.232], [128.18, 38.24], [128.11, 38.252], [128.035, 38.226], [128.2, 38.23], [128.088, 38.222]],
    arrows: [
      { path: [[128.06, 38.165], [128.07, 38.19], [128.085, 38.222]], color: "cyan" },
      { path: [[128.118, 38.162], [128.12, 38.185], [128.125, 38.214]], color: "cyan" },
      { path: [[128.18, 38.168], [128.17, 38.195], [128.152, 38.222]], color: "cyan" },
    ],
    points: [],
    line1: "미 해병대도 결국 물러섰는데",
    line2: "한국 해병이 '바위산' 뚫은 비결",
  },
};

/* ===== 렌더 ===== */
const W = 1280; // 레퍼런스 단위
const H = 720;
const S = 1.5; // 1920×1080 출력
const CYAN = "#00E5FF";
const NEON_RED = "#FF2A1A";
const YELLOW = "#FFD000";
const HEAD = "'Black Han Sans', 'Pretendard', sans-serif";
const merc = (lat: number) => Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));

type RasterMeta = { name: string; file: string; west: number; east: number; north: number; south: number };
let RASTERS: RasterMeta[] | null = null;

/** 결정적 의사난수 (렌더마다 같은 불씨 배치) */
const rand = (seed: number) => {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
};

/** 글꼴을 불러온 뒤 100px 기준 폭(em)을 잰다 */
const useMeasured = (texts: string[]): number[] => {
  const [w, setW] = useState<number[]>([]);
  const [hd] = useState(() => delayRender("front-measure"));
  useEffect(() => {
    Promise.all([document.fonts.load(`400 100px 'Black Han Sans'`, texts.join("")), document.fonts.ready])
      .then(() => {
        const ctx = document.createElement("canvas").getContext("2d")!;
        ctx.font = `400 100px ${HEAD}`;
        setW(texts.map((t) => ctx.measureText(t).width / 100));
      })
      .catch(() => setW([]))
      .finally(() => continueRender(hd));
  }, [texts.join("|")]);
  return w;
};

export const FrontThumb: React.FC<{ d: FrontThumbDef }> = ({ d }) => {
  const [meta, setMeta] = useState<RasterMeta[] | null>(RASTERS);
  const [h] = useState(() => (RASTERS ? null : delayRender("front-rasters")));
  useEffect(() => {
    if (RASTERS) return;
    fetch(staticFile("geo/rasters.json"))
      .then((r) => r.json())
      .then((j) => {
        RASTERS = j;
        setMeta(j);
      })
      .finally(() => h !== null && continueRender(h));
  }, [h]);

  const { center, span } = d.view;
  const ppr = W / ((span * Math.PI) / 180);
  const X = (lon: number) => ((lon - (center[0] - span / 2)) / span) * W;
  const Y = (lat: number) => H / 2 - (merc(lat) - merc(center[1])) * ppr;
  const P = ([lon, lat]: LL) => `${X(lon).toFixed(1)},${Y(lat).toFixed(1)}`;
  const rs = d.rasters.map((n) => meta?.find((m) => m.name === n)).filter(Boolean) as RasterMeta[];
  const terrain = (filter?: string) =>
    rs.map((r) => (
      <Img
        key={r.name}
        src={staticFile(`geo/thumbc/${r.name}.webp`)}
        style={{ position: "absolute", left: X(r.west), top: Y(r.north), width: X(r.east) - X(r.west), height: Y(r.south) - Y(r.north), filter }}
      />
    ));
  const enemy = [...d.front, ...d.enemyClose];
  const enemyClip = `polygon(${enemy.map(([lo, la]) => `${X(lo).toFixed(1)}px ${Y(la).toFixed(1)}px`).join(",")})`;

  // ----- 타이틀 크기: 규격 범위(68~72 / 78~84)에서 최대, 가로(좌 40 ~ 우 120 여백)를 넘으면 줄임 -----
  const [m1, m2] = useMeasured([d.line1, d.line2]);
  const BOX = W - 40 - 120;
  let l1 = 72;
  let l2 = 84;
  if (m1) l1 = Math.min(72, Math.floor(BOX / m1));
  if (m2) l2 = Math.min(84, Math.floor(BOX / m2));
  if (l2 < l1 * 1.1) l1 = Math.floor(l2 / 1.1); // Line 2가 항상 더 크게

  // ----- 불씨 -----
  const rnd = rand(d.fires.length * 7919 + Math.round(center[0] * 1000));
  const embers = d.fires.flatMap(([lo, la]) =>
    Array.from({ length: 34 }, () => {
      const a = rnd() * Math.PI * 2;
      const rr = Math.sqrt(rnd()) * 70;
      return { x: X(lo) + Math.cos(a) * rr, y: Y(la) + Math.sin(a) * rr * 0.75 - rnd() * 30, r: 0.7 + rnd() * 2.1, o: 0.55 + rnd() * 0.45 };
    }),
  );

  const arrow = (a: FrontArrow, i: number) => {
    const pts = a.path.map(([lo, la]) => [X(lo), Y(la)] as [number, number]);
    const w = a.w ?? 18;
    const [x2, y2] = pts[pts.length - 1];
    const [x1, y1] = pts[pts.length - 2];
    const len = Math.hypot(x2 - x1, y2 - y1) || 1;
    const ux = (x2 - x1) / len;
    const uy = (y2 - y1) / len;
    const hl = w * 2.1; // 화살촉 길이
    const hw = w * 1.45; // 화살촉 반폭
    const bx = x2 - ux * hl;
    const by = y2 - uy * hl;
    const body = [...pts.slice(0, -1), [bx + ux * 2, by + uy * 2]].map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
    const head = `${x2},${y2} ${bx - uy * hw},${by + ux * hw} ${bx + uy * hw},${by - ux * hw}`;
    const c = a.color === "cyan" ? CYAN : NEON_RED;
    const core = a.color === "cyan" ? "#C8FAFF" : "#FF9A8A";
    return (
      <g key={i}>
        <g filter="url(#ft-glow-big)" opacity={0.9}>
          <polyline points={body} fill="none" stroke={c} strokeWidth={w + 8} strokeLinecap="round" strokeLinejoin="round" />
          <polygon points={head} fill={c} />
        </g>
        <polyline points={body} fill="none" stroke="#120000" strokeWidth={w + 6} strokeLinecap="round" strokeLinejoin="round" opacity={0.85} />
        <polygon points={head} fill="#120000" stroke="#120000" strokeWidth={6} strokeLinejoin="round" opacity={0.85} />
        <polyline points={body} fill="none" stroke={c} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" />
        <polygon points={head} fill={c} />
        <polyline points={body} fill="none" stroke={core} strokeWidth={w * 0.28} strokeLinecap="round" strokeLinejoin="round" opacity={0.85} />
      </g>
    );
  };

  const L1H = l1 * 1.15;
  const L2H = l2 * 1.15;

  return (
    <AbsoluteFill style={{ background: "#0a1e3a", overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: W, height: H, transform: `scale(${S})`, transformOrigin: "0 0", overflow: "hidden", background: "#0a1e3a" }}>
        {/* 2-1 컬러 지형 (아군 쪽 초록·황록) */}
        <div style={{ position: "absolute", inset: 0, filter: "saturate(1.15) contrast(1.08)" }}>{terrain()}</div>
        {/* 2-2 적 공세 영역 — 같은 지형을 붉게 달군 판으로 잘라 얹음 */}
        <div style={{ position: "absolute", inset: 0, clipPath: enemyClip }}>
          {terrain("grayscale(1) brightness(1.05) contrast(1.4) sepia(1) saturate(10) hue-rotate(-38deg) brightness(0.8)")}
          <div style={{ position: "absolute", inset: 0, background: "rgba(170,0,0,.35)", mixBlendMode: "multiply" }} />
        </div>
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          <defs>
            <filter id="ft-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.2" /></filter>
            <filter id="ft-glow-big" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7" /></filter>
            <filter id="ft-smoke" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16" /></filter>
            <radialGradient id="ft-fire">
              <stop offset="0" stopColor="#FFE9A0" stopOpacity="0.95" />
              <stop offset="0.25" stopColor="#FFB13B" stopOpacity="0.8" />
              <stop offset="0.6" stopColor="#FF3D00" stopOpacity="0.45" />
              <stop offset="1" stopColor="#FF0000" stopOpacity="0" />
            </radialGradient>
            <clipPath id="ft-enemy"><polygon points={enemy.map(P).join(" ")} /></clipPath>
          </defs>
          {/* 포연 (적 영역 안, 불길 위쪽으로 짙게) */}
          <g clipPath="url(#ft-enemy)" filter="url(#ft-smoke)">
            {d.fires.map((f, i) => (
              <ellipse key={i} cx={X(f[0]) + 14} cy={Y(f[1]) - 34} rx={60} ry={30} fill="#1a0604" opacity={0.55} />
            ))}
          </g>
          {/* 전선을 따라 타오르는 불띠 (적 쪽만) */}
          <g clipPath="url(#ft-enemy)" style={{ mixBlendMode: "screen" }}>
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke="#FF3A00" strokeWidth={90} strokeLinejoin="round" opacity={0.55} filter="url(#ft-smoke)" />
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke="#FF9A2E" strokeWidth={28} strokeLinejoin="round" opacity={0.6} filter="url(#ft-glow-big)" />
          </g>
          {/* 불길 */}
          <g clipPath="url(#ft-enemy)" style={{ mixBlendMode: "screen" }}>
            {d.fires.map((f, i) => (
              <ellipse key={i} cx={X(f[0])} cy={Y(f[1])} rx={i % 3 === 0 ? 92 : 68} ry={i % 3 === 0 ? 62 : 46} fill="url(#ft-fire)" />
            ))}
          </g>
          {/* 불씨 */}
          <g clipPath="url(#ft-enemy)" style={{ mixBlendMode: "screen" }}>
            {embers.map((e, i) => (
              <circle key={i} cx={e.x} cy={e.y} r={e.r} fill={i % 4 ? "#FFB347" : "#FFF1B0"} opacity={e.o} />
            ))}
          </g>
          {/* 강 (푸른 빛) */}
          {d.river && (
            <g>
              <polyline points={d.river.map(P).join(" ")} fill="none" stroke="#2F7DFF" strokeWidth={10} strokeLinejoin="round" strokeLinecap="round" opacity={0.75} filter="url(#ft-glow)" />
              <polyline points={d.river.map(P).join(" ")} fill="none" stroke="#5FB0FF" strokeWidth={3.2} strokeLinejoin="round" strokeLinecap="round" />
            </g>
          )}
          {/* 아군 방어선 — 형광 블루 네온 */}
          {[d.front].map((ln, i) => (
            <g key={i}>
              <polyline points={ln.map(P).join(" ")} fill="none" stroke={CYAN} strokeWidth={16} strokeLinejoin="round" strokeLinecap="round" opacity={0.75} filter="url(#ft-glow-big)" />
              <polyline points={ln.map(P).join(" ")} fill="none" stroke="#002a33" strokeWidth={9} strokeLinejoin="round" strokeLinecap="round" opacity={0.6} />
              <polyline points={ln.map(P).join(" ")} fill="none" stroke={CYAN} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round" />
              <polyline points={ln.map(P).join(" ")} fill="none" stroke="#E6FDFF" strokeWidth={1.8} strokeLinejoin="round" strokeLinecap="round" />
            </g>
          ))}
          {/* 돌격 화살표 */}
          {d.arrows.map(arrow)}
          {/* 아군 거점 */}
          {d.points.map((p, i) => (
            <g key={i} transform={`translate(${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)})`}>
              <circle r={15} fill={CYAN} opacity={0.6} filter="url(#ft-glow)" />
              <circle r={7.5} fill="#001418" stroke={CYAN} strokeWidth={3} />
              <circle r={3} fill="#E6FDFF" />
            </g>
          ))}
        </svg>
        {/* 상단 살짝 어둡게 (뱃지 가독성) + 하단 40% 강한 블랙 그라데이션 */}
        <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 120, background: "linear-gradient(to bottom, rgba(0,0,0,.35), rgba(0,0,0,0))" }} />
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: H * 0.4, background: "linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,.72) 38%, rgba(0,0,0,.93) 70%, #000 100%)" }} />
        {/* 1 우측 상단 시대 뱃지 */}
        <div style={{ position: "absolute", left: 1040, top: 40, background: "rgba(8,10,14,.74)", border: "1.5px solid rgba(255,255,255,.4)", borderRadius: 6, padding: "6px 14px 5px", color: "#fff", fontFamily: "'Pretendard', sans-serif", fontWeight: 900, fontSize: 28, lineHeight: 1.1, whiteSpace: "nowrap", letterSpacing: "-0.01em", boxShadow: "0 4px 14px rgba(0,0,0,.55)" }}>
          {d.badge}
        </div>
        {/* 3 하단 2줄 초대형 타이틀 (중앙 정렬 · 우측 120px 재생시간 배지 여백) */}
        <div style={{ position: "absolute", left: 40, right: 120, bottom: 30, display: "flex", flexDirection: "column", alignItems: "center", fontFamily: HEAD, fontWeight: 400, letterSpacing: "-0.01em", wordSpacing: "-0.12em", whiteSpace: "nowrap" }}>
          <div style={{ fontSize: l1, lineHeight: `${L1H}px`, height: L1H, color: "#FFFFFF", WebkitTextStroke: "10px #000", paintOrder: "stroke fill", textShadow: "0 5px 0 #000, 0 8px 18px rgba(0,0,0,.95)" }}>{d.line1}</div>
          <div style={{ fontSize: l2, lineHeight: `${L2H}px`, height: L2H, color: YELLOW, WebkitTextStroke: "12px #000", paintOrder: "stroke fill", textShadow: "0 6px 0 #000, 0 10px 22px rgba(0,0,0,.95), 0 0 26px rgba(255,208,0,.25)" }}>{d.line2}</div>
        </div>
      </div>
      <style>{`@font-face{font-family:'Pretendard';font-weight:900;font-style:normal;src:url(${staticFile("fonts/Pretendard-Black.woff2")}) format('woff2');}`}</style>
    </AbsoluteFill>
  );
};
