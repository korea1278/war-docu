/**
 * '격전의 지도' 썸네일 표준 v3.1 — 실전 전황 디테일 + 3D 입체 텍스트 (2026-11-02 사용자 지시서, EP15 낙동강·EP16 도솔산부터)
 *
 * 레이아웃 규격은 레퍼런스(1280×720) 단위로 적고, 출력은 1.5배 확대한 1920×1080.
 *  1 우측 상단 연월 뱃지 — 카피 느낌이 나서 완전 삭제 (v3.1)
 *  2 지도 위 전술 디테일
 *    · 적 공세 영역 = 붉게 달군 지형 + 불타는 전선 화염 + 폭격 연기 기둥
 *      굵은 레드 네온 화살표 3~4개, 화살표 사이로 진격하는 전차·돌격 보병 실루엣(units),
 *      함락 도시 핀(fallen: 붉은 X / 붉은 타격 원 + 검정 칩 지명)
 *    · 아군 방어선 = 형광 시안 #00E5FF 네온 6px + 다층 발광, 핵심 거점 도트 핀 + 미니 칩(pins),
 *      방어선 중심 네온 강조 뱃지(badges)
 *    · 화면 밖이나 하단 타이틀 영역에 들어가는 핀은 위쪽 지도 영역 가장자리로 끌어와 방향 화살표(▲▼◀▶)를 붙인다
 *  3 하단 45% 칠흑 그라데이션 (#000 → .98 35% → .85 65% → 투명)
 *  4 하단 2줄 초대형 타이틀 — Black Han Sans, 화면 폭 90% 점유, line-height 1.05, 자간 -3px, bottom 35
 *    · Line 1 90~94px 흰색 / Line 2 110~116px 네온 옐로 #FFD000 (길면 90% 폭 안으로 자동 축소, Line 2가 항상 더 크게)
 *    · 6px 검정 외곽선(paint-order stroke fill) + 4·8·12·16px 다중 3D 하드 섀도우
 * 에피소드는 FRONT 표에 한 줄 추가 → Thumbnail A안(ko)이 이 디자인으로 렌더된다.
 */
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile } from "remotion";
import "@fontsource/black-han-sans/400.css";

type LL = [number, number];
export type FrontArrow = { path: LL[]; color?: "red" | "cyan"; w?: number };
export type FrontUnit = { at: LL; kind: "tank" | "inf"; s?: number; flip?: boolean };
export type FrontPin = { at: LL; name: string; dx?: number; dy?: number; side?: "below" | "right" | "left" | "above" };
export type FrontFallen = { at: LL; name: string; mark: "x" | "hit"; dx?: number; dy?: number; side?: "below" | "right" | "left" | "above" };
export type FrontThumbDef = {
  rasters: string[]; // 아래→위 순서로 깔 지형 (public/geo/thumbc/<name>.webp)
  view: { center: LL; span: number }; // span = 화면 가로 경도 폭
  front: LL[]; // 아군 방어선 = 붉은 적 영역과 초록 아군 영역의 경계 (형광 블루 네온)
  enemyClose: LL[]; // front 끝점에서 화면 밖을 돌아 시작점으로 돌아가는 점들 → [...front, ...enemyClose] = 적 공세 영역
  fires: LL[]; // 불길 중심점 (적 영역 안, 전선 가까이)
  smoke?: LL[]; // 폭격 연기 기둥
  river?: LL[]; // 강 (푸른 빛 — 방어선과 겹치는 낙동강 등)
  arrows: FrontArrow[];
  units?: FrontUnit[]; // 진격하는 전차·보병 실루엣
  fallen?: FrontFallen[]; // 함락 도시 (X / 타격 원)
  pins?: FrontPin[]; // 아군 핵심 거점 (도트 + 미니 칩)
  badges?: { at: LL; text: string; dx?: number; dy?: number }[]; // 방어선 중심 네온 강조 뱃지
  points?: LL[]; // 라벨 없는 빛나는 점
  line1: string;
  line2: string;
};

/* ===== 에피소드 표 (새 에피소드는 여기 한 줄) ===== */
// 좌표는 각 에피소드 storyboard.json places와 동일(개략).
export const NAKTONG_FRONT: LL[] = [[129.4, 36.42], [129.2, 36.4], [128.98, 36.42], [128.75, 36.38], [128.52, 36.42], [128.33, 36.4], [128.36, 36.2], [128.39, 36.05], [128.41, 35.95], [128.45, 35.84], [128.42, 35.72], [128.36, 35.68], [128.38, 35.63], [128.35, 35.57], [128.4, 35.5], [128.4, 35.44], [128.43, 35.4], [128.4, 35.33], [128.35, 35.25], [128.37, 35.17], [128.44, 35.1]];
export const NAKTONG_RIVER: LL[] = [[128.3056, 36.3601], [128.2867, 36.3491], [128.2836, 36.3307], [128.2888, 36.3144], [128.3362, 36.2886], [128.3426, 36.2656], [128.3372, 36.2471], [128.3455, 36.2365], [128.3628, 36.2184], [128.3637, 36.1968], [128.377, 36.1844], [128.3824, 36.1529], [128.378, 36.1284], [128.3969, 36.1125], [128.3964, 36.0881], [128.3853, 36.074], [128.4058, 36.0374], [128.3996, 36.0225], [128.3986, 36.0154], [128.3917, 35.9819], [128.3966, 35.9419], [128.3992, 35.8935], [128.3856, 35.8689], [128.3901, 35.8534], [128.4443, 35.8472], [128.4604, 35.8404], [128.4652, 35.8363], [128.4791, 35.8192], [128.4711, 35.8092], [128.4231, 35.8087], [128.4011, 35.7843], [128.3855, 35.7596], [128.4169, 35.7341], [128.4297, 35.7259], [128.4345, 35.7085], [128.4173, 35.6937], [128.365, 35.7058], [128.3511, 35.7004], [128.3545, 35.6834], [128.3852, 35.6531], [128.402, 35.6374], [128.3858, 35.6151], [128.3604, 35.6118], [128.3525, 35.6037], [128.3561, 35.5906], [128.3503, 35.5534], [128.3506, 35.5406], [128.3912, 35.5096], [128.4244, 35.4905], [128.42, 35.4755], [128.3828, 35.4581], [128.3748, 35.4469], [128.3887, 35.4259], [128.4219, 35.416], [128.4411, 35.3885], [128.4746, 35.3808], [128.498, 35.3957], [128.5328, 35.3874], [128.5523, 35.3798], [128.5739, 35.3786], [128.5965, 35.3936], [128.6177, 35.3776], [128.6453, 35.3728], [128.6901, 35.3787], [128.7439, 35.3515], [128.7734, 35.3471], [128.7985, 35.3592], [128.8093, 35.3787], [128.8533, 35.3931], [128.8693, 35.3907], [128.879, 35.37], [128.9111, 35.3648], [128.936, 35.3448], [128.9671, 35.3299], [128.9728, 35.3132], [128.9982, 35.2889], [129.0126, 35.275], [128.9987, 35.2359], [128.9896, 35.2037], [128.9629, 35.1845], [128.961, 35.1557], [128.9532, 35.1073]];

export const FRONT: Record<string, FrontThumbDef> = {
  // EP15(사용자 지정 번호) 낙동강 방어선 — 1950년 8월 부산 교두보: 서·북쪽은 불타는 적 공세 영역, 안쪽은 초록 지형 + 형광 블루 방어선
  naktong: {
    rasters: ["korea", "south"],
    view: { center: [128.55, 35.47], span: 4.4 },
    front: NAKTONG_FRONT,
    enemyClose: [[128.3, 34.0], [125.8, 34.0], [125.8, 38.2], [129.42, 38.2], [129.42, 36.42]],
    fires: [[128.22, 36.3], [128.62, 36.5], [129.05, 36.5], [128.29, 36.08], [128.33, 35.84], [128.27, 35.6], [128.3, 35.36], [127.85, 36.15], [127.8, 35.7], [128.88, 36.52], [128.05, 35.95], [127.6, 36.35], [128.36, 36.46], [128.06, 35.45]],
    smoke: [[127.95, 36.4], [128.15, 35.72], [127.55, 35.95], [128.75, 36.62], [128.12, 35.25]],
    river: NAKTONG_RIVER,
    arrows: [
      { path: [[126.75, 36.16], [127.5, 36.2], [128.27, 36.16]], color: "red", w: 22 },
      { path: [[126.75, 35.86], [127.5, 35.92], [128.33, 35.9]], color: "red", w: 22 },
      { path: [[126.85, 35.42], [127.55, 35.56], [128.28, 35.6]], color: "red", w: 22 },
      { path: [[128.6, 37.15], [128.58, 36.8], [128.55, 36.48]], color: "red", w: 22 },
    ],
    units: [
      { at: [127.12, 35.98], kind: "tank", s: 1.25 },
      { at: [127.55, 36.04], kind: "inf" },
      { at: [127.72, 36.0], kind: "inf", s: 0.9 },
      { at: [127.15, 35.66], kind: "tank", s: 1.25 },
      { at: [127.6, 35.72], kind: "inf" },
      { at: [127.78, 35.66], kind: "inf", s: 0.9 },
      { at: [127.45, 35.3], kind: "inf" },
      { at: [128.88, 36.75], kind: "tank", s: 1.1 },
      { at: [128.25, 36.7], kind: "inf" },
    ],
    fallen: [
      { at: [126.978, 37.566], name: "서울", mark: "x", side: "right" },
      { at: [127.385, 36.35], name: "대전", mark: "hit", side: "right" },
    ],
    pins: [
      { at: [128.601, 35.871], name: "대구", side: "right" },
      { at: [129.343, 36.019], name: "포항" },
      { at: [129.04, 35.11], name: "부산" },
    ],
    badges: [{ at: [128.4, 35.76], text: "낙동강", dx: 0, dy: 0 }],
    line1: "서울도 대전도 다 밀렸는데",
    line2: "마지막 '낙동강'이 버틴 이유",
  },
  // EP16 도솔산 전투 (1951년 6월) — 북쪽 능선(북한군 요새)은 포화로 불타는 붉은 영역, 남쪽에서 한국 해병이 형광 블루 화살표로 치고 올라감
  // 붉은 화살표 = 능선에서 내리꽂는 북한군 역습, 보병 실루엣 = 능선 위 북한군. 좌표는 episodes/ep16-dosolsan/storyboard.json places 기준(개략)
  "ep16-dosolsan": {
    rasters: ["yanggu", "dosol_zoom"],
    view: { center: [128.11, 38.168], span: 0.5 },
    front: [[127.8, 38.206], [127.98, 38.212], [128.02, 38.216], [128.05, 38.214], [128.075, 38.209], [128.095, 38.212], [128.112, 38.207], [128.128, 38.202], [128.145, 38.207], [128.165, 38.214], [128.19, 38.219], [128.24, 38.224], [128.42, 38.226]],
    enemyClose: [[128.5, 38.226], [128.5, 38.45], [127.7, 38.45], [127.7, 38.206]],
    fires: [[128.1, 38.238], [128.135, 38.222], [128.12, 38.228], [128.08, 38.244], [128.155, 38.232], [128.06, 38.232], [128.18, 38.24], [128.11, 38.252], [128.035, 38.226], [128.2, 38.23], [128.088, 38.222], [127.95, 38.23], [128.27, 38.24]],
    smoke: [[128.07, 38.25], [128.16, 38.245], [127.98, 38.24], [128.24, 38.25]],
    arrows: [
      { path: [[128.0, 38.29], [128.02, 38.26], [128.045, 38.222]], color: "red", w: 20 },
      { path: [[128.215, 38.29], [128.2, 38.26], [128.18, 38.228]], color: "red", w: 20 },
      { path: [[128.03, 38.148], [128.055, 38.18], [128.088, 38.216]], color: "cyan", w: 20 },
      { path: [[128.19, 38.148], [128.165, 38.18], [128.132, 38.21]], color: "cyan", w: 20 },
    ],
    units: [
      { at: [127.96, 38.252], kind: "inf", flip: false },
      { at: [128.04, 38.258], kind: "inf", s: 0.9 },
      { at: [128.2, 38.262], kind: "inf", flip: true },
      { at: [128.28, 38.25], kind: "inf", flip: true, s: 0.9 },
    ],
    fallen: [
      { at: [128.09, 38.262], name: "북한군 12사단", mark: "hit", dy: -2 },
      { at: [128.16, 38.25], name: "북한군 32사단", mark: "hit" },
    ],
    pins: [
      { at: [127.99, 38.106], name: "양구" },
      { at: [128.14, 38.285], name: "펀치볼" },
      { at: [128.1, 38.238], name: "1,148m 주봉" },
    ],
    badges: [{ at: [128.11, 38.207], text: "도솔산", dx: 0, dy: 62 }],
    line1: "미 해병대도 결국 물러섰는데",
    line2: "한국 해병이 '바위산' 뚫은 비결",
  },
};

/* ===== 렌더 ===== */
const W = 1280; // 레퍼런스 단위
const H = 720;
const S = 1.5; // 1920×1080 출력
const MAP_BOTTOM = H * 0.55; // 하단 45%는 타이틀 영역 — 핀은 이 위에만
const CYAN = "#00E5FF";
const NEON_RED = "#FF2A1A";
const YELLOW = "#FFD000";
const HEAD = "'Black Han Sans', 'Pretendard', sans-serif";
const CHIP = "'Pretendard', 'Black Han Sans', sans-serif";
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

/** 화면 밖·타이틀 영역의 핀을 지도 영역 가장자리로 끌어오고, 원래 방향 화살표를 돌려준다 */
const clampPin = (x: number, y: number) => {
  const m = 34;
  const cx = Math.max(m + 20, Math.min(W - m - 20, x));
  const cy = Math.max(m, Math.min(MAP_BOTTOM - 26, y));
  let dir = "";
  if (y < m) dir = "▲";
  else if (y > MAP_BOTTOM - 26) dir = "▼";
  else if (x < m + 20) dir = "◀";
  else if (x > W - m - 20) dir = "▶";
  return { x: cx, y: cy, dir };
};

/** 전차 실루엣 (오른쪽을 향함, 폭 약 64) */
const Tank: React.FC<{ fill: string }> = ({ fill }) => (
  <g fill={fill}>
    <rect x={-32} y={3} width={64} height={14} rx={7} />
    <polygon points="-29,4 29,4 25,-5 -26,-5" />
    <polygon points="-13,-5 11,-5 8,-15 -9,-16" />
    <rect x={8} y={-13} width={30} height={4} rx={1.5} />
    <rect x={36} y={-14.5} width={5} height={7} rx={1} />
  </g>
);
/** 돌격 보병 실루엣 (오른쪽으로 달리며 총을 든 모습, 키 약 46) */
const Soldier: React.FC<{ fill: string; sw?: number }> = ({ fill, sw = 0 }) => (
  <g fill={fill} stroke={fill} strokeLinecap="round" strokeLinejoin="round" strokeWidth={sw}>
    <circle cx={5} cy={-39} r={5.2} />
    <path d="M-1,-44.5 Q5,-50 11,-43 L-1,-42 Z" />
    <polygon points="-1,-33 9,-32 6,-15 -5,-16" />
    <g fill="none" strokeWidth={5.4 + sw}>
      <polyline points="-3,-16 -12,-6 -18,1" />
      <polyline points="4,-15 10,-6 8,2 14,2" />
      <polyline points="6,-29 14,-23 20,-27" />
      <polyline points="1,-30 -4,-21 6,-20" />
      <line x1={-6} y1={-18} x2={27} y2={-33} strokeWidth={3.4 + sw} />
    </g>
  </g>
);

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
  // 위에 겹치는 고해상도 지형은 가장자리를 부드럽게 녹여 타일 경계(색·해상도 차이)가 안 보이게
  const FEATHER = "linear-gradient(to right, transparent 0, #000 9%, #000 91%, transparent 100%), linear-gradient(to bottom, transparent 0, #000 9%, #000 91%, transparent 100%)";
  const terrain = (filter?: string) =>
    rs.map((r, i) => (
      <Img
        key={r.name}
        src={staticFile(`geo/thumbc/${r.name}.webp`)}
        style={{
          position: "absolute", left: X(r.west), top: Y(r.north), width: X(r.east) - X(r.west), height: Y(r.south) - Y(r.north), filter,
          ...(i > 0 ? { WebkitMaskImage: FEATHER, WebkitMaskComposite: "source-in", maskComposite: "intersect" } : {}),
        }}
      />
    ));
  const enemy = [...d.front, ...d.enemyClose];
  const enemyClip = `polygon(${enemy.map(([lo, la]) => `${X(lo).toFixed(1)}px ${Y(la).toFixed(1)}px`).join(",")})`;

  // ----- 타이틀 크기: 규격(94 / 116)에서 최대, 화면 폭 90%(자간 -3px 반영)를 넘으면 줄임. Line 2는 항상 Line 1의 1.18배 이상 -----
  const [m1, m2] = useMeasured([d.line1, d.line2]);
  const BOX = W * 0.9;
  const LS = -3;
  const fit = (m: number | undefined, text: string, max: number) => (m ? Math.min(max, Math.floor((BOX - LS * [...text].length) / m)) : max);
  const l2 = fit(m2, d.line2, 116);
  let l1 = fit(m1, d.line1, 94);
  if (l1 > l2 / 1.18) l1 = Math.floor(l2 / 1.18);

  // ----- 불씨 -----
  const rnd = rand(d.fires.length * 7919 + Math.round(center[0] * 1000));
  const embers = d.fires.flatMap(([lo, la]) =>
    Array.from({ length: 34 }, () => {
      const a = rnd() * Math.PI * 2;
      const rr = Math.sqrt(rnd()) * 70;
      return { x: X(lo) + Math.cos(a) * rr, y: Y(la) + Math.sin(a) * rr * 0.75 - rnd() * 30, r: 0.7 + rnd() * 2.1, o: 0.55 + rnd() * 0.45 };
    }),
  );
  // ----- 폭격 연기 기둥 (아래 넓고 위로 퍼지며 옅어짐) -----
  const plumes = (d.smoke ?? []).map(([lo, la], i) => {
    const x = X(lo);
    const y = Y(la);
    return Array.from({ length: 7 }, (_, k) => ({ cx: x + Math.sin(i * 2.1 + k) * 9 + k * 5, cy: y - k * 17, r: 16 + k * 7, o: 0.62 - k * 0.07 }));
  });

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
    const core = a.color === "cyan" ? "#C8FAFF" : "#FFB0A0";
    return (
      <g key={i}>
        <g filter="url(#ft-glow-big)" opacity={0.95}>
          <polyline points={body} fill="none" stroke={c} strokeWidth={w + 12} strokeLinecap="round" strokeLinejoin="round" />
          <polygon points={head} fill={c} stroke={c} strokeWidth={8} strokeLinejoin="round" />
        </g>
        <polyline points={body} fill="none" stroke="#120000" strokeWidth={w + 6} strokeLinecap="round" strokeLinejoin="round" opacity={0.85} />
        <polygon points={head} fill="#120000" stroke="#120000" strokeWidth={6} strokeLinejoin="round" opacity={0.85} />
        <polyline points={body} fill="none" stroke={c} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" />
        <polygon points={head} fill={c} />
        <polyline points={body} fill="none" stroke={core} strokeWidth={w * 0.3} strokeLinecap="round" strokeLinejoin="round" opacity={0.9} />
      </g>
    );
  };

  /** 검정 칩 지명 (흰 글자) */
  const OFF: Record<string, [number, number, string]> = { below: [0, 1, "translate(-50%, 0)"], above: [0, -1, "translate(-50%, -100%)"], right: [1, 0, "translate(0, -50%)"], left: [-1, 0, "translate(-100%, -50%)"] };
  const chip = (px: number, py: number, gap: number, side: string | undefined, text: string, border: string, key: string, dir = "") => {
    const [ox, oy, tr] = OFF[side ?? "below"];
    return (
    <div
      key={key}
      style={{
        position: "absolute", left: px + ox * gap, top: py + oy * gap, transform: tr, background: "rgba(0,0,0,.86)", border: `2px solid ${border}`, borderRadius: 4,
        padding: "3px 9px 2px", color: "#fff", fontFamily: CHIP, fontWeight: 900, fontSize: 21, lineHeight: 1.1, whiteSpace: "nowrap", letterSpacing: "-0.02em",
        boxShadow: `0 3px 10px rgba(0,0,0,.7), 0 0 10px ${border}66`,
      }}
    >
      {dir === "▲" || dir === "◀" ? <span style={{ fontSize: 15, marginRight: 4, color: border }}>{dir}</span> : null}
      {text}
      {dir === "▼" || dir === "▶" ? <span style={{ fontSize: 15, marginLeft: 4, color: border }}>{dir}</span> : null}
    </div>
    );
  };

  const pins = (d.pins ?? []).map((p) => ({ ...p, ...clampPin(X(p.at[0]) + (p.dx ?? 0), Y(p.at[1]) + (p.dy ?? 0)) }));
  const fallen = (d.fallen ?? []).map((p) => ({ ...p, ...clampPin(X(p.at[0]) + (p.dx ?? 0), Y(p.at[1]) + (p.dy ?? 0)) }));

  const L1H = l1 * 1.05;
  const L2H = l2 * 1.05;
  const TITLE_SHADOW = "0px 4px 0px #000000, 0px 8px 0px #000000, 0px 12px 2px #000000, 0px 16px 25px rgba(0,0,0,0.95)";

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
            <filter id="ft-plume" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9" /></filter>
            <filter id="ft-rim" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4" /></filter>
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
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke="#FF3A00" strokeWidth={90} strokeLinejoin="round" opacity={0.6} filter="url(#ft-smoke)" />
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke="#FF9A2E" strokeWidth={30} strokeLinejoin="round" opacity={0.65} filter="url(#ft-glow-big)" />
          </g>
          {/* 불길 */}
          <g clipPath="url(#ft-enemy)" style={{ mixBlendMode: "screen" }}>
            {d.fires.map((f, i) => (
              <ellipse key={i} cx={X(f[0])} cy={Y(f[1])} rx={i % 3 === 0 ? 92 : 68} ry={i % 3 === 0 ? 62 : 46} fill="url(#ft-fire)" />
            ))}
          </g>
          {/* 폭격 연기 기둥 — 바닥은 불빛, 위로 검은 연기 */}
          {plumes.map((pl, i) => (
            <g key={i}>
              <ellipse cx={pl[0].cx} cy={pl[0].cy + 6} rx={30} ry={14} fill="#FF7A1A" opacity={0.7} filter="url(#ft-glow-big)" style={{ mixBlendMode: "screen" }} />
              <g filter="url(#ft-plume)">
                {pl.map((c, k) => (
                  <circle key={k} cx={c.cx} cy={c.cy} r={c.r} fill={k < 2 ? "#2a0d06" : "#141010"} opacity={c.o} />
                ))}
              </g>
            </g>
          ))}
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
          {/* 아군 방어선 — 형광 시안 네온 6px + 다층 발광 */}
          <g>
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke={CYAN} strokeWidth={30} strokeLinejoin="round" strokeLinecap="round" opacity={0.35} filter="url(#ft-smoke)" />
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke={CYAN} strokeWidth={16} strokeLinejoin="round" strokeLinecap="round" opacity={0.8} filter="url(#ft-glow-big)" />
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke={CYAN} strokeWidth={10} strokeLinejoin="round" strokeLinecap="round" opacity={0.9} filter="url(#ft-glow)" />
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke="#002a33" strokeWidth={9} strokeLinejoin="round" strokeLinecap="round" opacity={0.55} />
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke={CYAN} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round" />
            <polyline points={d.front.map(P).join(" ")} fill="none" stroke="#E6FDFF" strokeWidth={1.8} strokeLinejoin="round" strokeLinecap="round" />
          </g>
          {/* 진격하는 전차·보병 실루엣 (검은 몸체 + 붉은 림 라이트) */}
          {(d.units ?? []).map((u, i) => {
            const s = (u.s ?? 1) * (u.kind === "tank" ? 1 : 0.95);
            const tf = `translate(${X(u.at[0]).toFixed(1)},${Y(u.at[1]).toFixed(1)}) scale(${u.flip ? -s : s},${s})`;
            const Shape = u.kind === "tank" ? Tank : Soldier;
            return (
              <g key={i} transform={tf}>
                <g filter="url(#ft-rim)" opacity={0.95}>
                  {u.kind === "tank" ? (
                    <g transform="scale(1.12)"><Shape fill="#FF5A2A" /></g>
                  ) : (
                    <Soldier fill="#FF5A2A" sw={3.5} />
                  )}
                </g>
                <Shape fill="#0d0402" />
              </g>
            );
          })}
          {/* 돌격 화살표 */}
          {d.arrows.map(arrow)}
          {/* 라벨 없는 빛나는 점 */}
          {(d.points ?? []).map((p, i) => (
            <g key={i} transform={`translate(${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)})`}>
              <circle r={15} fill={CYAN} opacity={0.6} filter="url(#ft-glow)" />
              <circle r={7.5} fill="#001418" stroke={CYAN} strokeWidth={3} />
              <circle r={3} fill="#E6FDFF" />
            </g>
          ))}
          {/* 아군 핵심 거점 도트 핀 */}
          {pins.map((p, i) => (
            <g key={i} transform={`translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`}>
              <circle r={17} fill={CYAN} opacity={0.65} filter="url(#ft-glow)" />
              <circle r={8.5} fill="#001418" stroke={CYAN} strokeWidth={3.4} />
              <circle r={3.4} fill="#E6FDFF" />
            </g>
          ))}
          {/* 함락 도시 — 붉은 X / 타격 원 */}
          {fallen.map((p, i) => (
            <g key={i} transform={`translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`}>
              <circle r={20} fill={NEON_RED} opacity={0.7} filter="url(#ft-glow)" />
              {p.mark === "x" ? (
                <g strokeLinecap="round">
                  <path d="M-13,-13 L13,13 M13,-13 L-13,13" stroke="#000" strokeWidth={11} />
                  <path d="M-13,-13 L13,13 M13,-13 L-13,13" stroke={NEON_RED} strokeWidth={6.5} />
                </g>
              ) : (
                <g>
                  <circle r={14} fill="none" stroke="#000" strokeWidth={8} />
                  <circle r={14} fill="none" stroke={NEON_RED} strokeWidth={4} />
                  <circle r={7} fill={NEON_RED} stroke="#000" strokeWidth={2} />
                </g>
              )}
            </g>
          ))}
        </svg>
        {/* 핀 칩 (지명) */}
        {pins.map((p, i) => chip(p.x, p.y, 15, p.side, p.name, CYAN, `p${i}`, p.dir))}
        {fallen.map((p, i) => chip(p.x, p.y, 23, p.side, p.name, NEON_RED, `f${i}`, p.dir))}
        {/* 주요 방어 지점 네온 뱃지 */}
        {(d.badges ?? []).map((b, i) => (
          <div
            key={i}
            style={{
              position: "absolute", left: X(b.at[0]) + (b.dx ?? 0), top: Y(b.at[1]) + (b.dy ?? 0), transform: "translate(-50%, -50%)",
              background: "rgba(0,18,24,.88)", border: `3px solid ${CYAN}`, borderRadius: 8, padding: "5px 16px 3px", color: CYAN,
              fontFamily: HEAD, fontSize: 38, lineHeight: 1.1, whiteSpace: "nowrap", letterSpacing: "-0.01em",
              textShadow: `0 0 10px ${CYAN}, 0 0 22px ${CYAN}AA`, boxShadow: `0 0 14px ${CYAN}, 0 0 34px ${CYAN}88, inset 0 0 12px ${CYAN}66`,
            }}
          >
            {b.text}
          </div>
        ))}
        {/* 3 하단 45% 칠흑 그라데이션 */}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: H * 0.45, background: "linear-gradient(to top, #000000 0%, rgba(0,0,0,0.98) 35%, rgba(0,0,0,0.85) 65%, transparent 100%)" }} />
        {/* 4 하단 2줄 초대형 3D 입체 타이틀 (화면 폭 90%) */}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 35, display: "flex", flexDirection: "column", alignItems: "center", fontFamily: HEAD, fontWeight: 400, letterSpacing: LS, whiteSpace: "nowrap" }}>
          <div style={{ fontSize: l1, lineHeight: `${L1H}px`, height: L1H, color: "#FFFFFF", WebkitTextStroke: "6px #000000", paintOrder: "stroke fill", textShadow: TITLE_SHADOW }}>{d.line1}</div>
          <div style={{ fontSize: l2, lineHeight: `${L2H}px`, height: L2H, color: YELLOW, WebkitTextStroke: "6px #000000", paintOrder: "stroke fill", textShadow: TITLE_SHADOW }}>{d.line2}</div>
        </div>
      </div>
      <style>{`@font-face{font-family:'Pretendard';font-weight:900;font-style:normal;src:url(${staticFile("fonts/Pretendard-Black.woff2")}) format('woff2');}`}</style>
    </AbsoluteFill>
  );
};
