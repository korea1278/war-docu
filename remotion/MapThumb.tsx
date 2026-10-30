/**
 * '격전의 지도' 공통 썸네일 표준 (2026-10-25 확정, EP09부터 모든 새 에피소드 A안 기본)
 * 1920×1080 · 6개 레이어:
 *  1 흑백 3D 지형(채도 0 · brightness 0.45 · contrast 1.2)  2 작전선(전선 점선·거점 핀·진격 화살표)
 *  3 인물 흑백 누끼(우측 40~45%, 흰 림 라이트, 하단은 블랙 판 속으로 마스킹)  4 붉은 사각 스탬프(-6~-8deg, 4px #D32F2F)
 *  5 맨 아래 솔리드 블랙 바(Line 2 전용) + Line 1 뒤 어두운 띠  6 2줄 질문형 카피 — Line1 흰색은 사진 위(굵은 검정 외곽선),
 *    Line2 #FFD000은 블랙 바 위. 글꼴 한 Pretendard Black / 영 Montserrat Black, 실측 폭으로 가로를 꽉 채움 (레퍼런스 '역사 사랑방')
 * 에피소드는 MAPT 표에 한 줄 추가 → `mode=thumb`가 _ko_A / _en_A를 렌더.
 */
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile } from "remotion";
import "@fontsource/anton/400.css";
import "@fontsource/montserrat/900.css";

type LL = [number, number];
type Item =
  | { k: "front"; path: LL[] }
  | { k: "ridge"; path: LL[] }
  | { k: "pin"; p: LL; text: { ko: string; en: string }; color?: "red" | "blue"; lift?: number }
  | { k: "arrow"; path: LL[]; color?: "red" | "blue" }
  | { k: "ring"; p: LL; r?: number }; // EP13: 빨간 타깃 원형 링 (포위·차단 지점)
type Copy = { stamp: string; line1: string; line2: string; hook?: string };
export type MapThumbDef = {
  raster: string; // public/geo/rasters.json 의 name
  rasterFallback?: string; // raster가 아직 없을 때(새 권역 생성 전) 대신 쓸 래스터
  lakes?: boolean; // water.json 호수를 짙은 청회색으로 칠함 (흑백 DEM에서 호수가 안 보이는 문제 · EP13 파로호)
  /** EP13 레퍼런스 변형: 하단 floor 비율(예 0.38)의 솔리드 블랙 바닥판 위에 2줄 모두, 상단 서브 훅(따옴표), Line 2 색 지정 */
  floor?: number;
  line2Color?: string;
  view: { center: LL; span: number }; // span = 화면 가로 경도 폭
  items: Item[];
  subjectX?: number; // 인물 이미지 가로 중심(px, 기본 1500)
  stampPos?: { x: number; y: number; rot?: number };
  ko: Copy;
  en: Copy;
};

/* ===== 에피소드 표 (새 에피소드는 여기 한 줄) ===== */
export const MAPT: Record<string, MapThumbDef> = {
  bloodyridge: {
    raster: "bloody_zoom",
    view: { center: [128.08, 38.236], span: 0.21 },
    items: [
      { k: "front", path: [[127.97, 38.214], [128.0, 38.221], [128.03, 38.224], [128.06, 38.226], [128.1, 38.232], [128.14, 38.238]] },
      { k: "ridge", path: [[128.012, 38.249], [128.022, 38.252], [128.031, 38.254], [128.04, 38.255], [128.046, 38.253], [128.051, 38.252], [128.058, 38.25]] },
      { k: "arrow", path: [[127.995, 38.226], [127.993, 38.25], [128.003, 38.266], [128.018, 38.264]], color: "blue" },
      { k: "arrow", path: [[128.04, 38.229], [128.04, 38.239], [128.04, 38.248]], color: "blue" },
      { k: "arrow", path: [[128.08, 38.231], [128.083, 38.252], [128.07, 38.266], [128.056, 38.262]], color: "blue" },
      { k: "pin", p: [128.022, 38.252], text: { ko: "983고지", en: "HILL 983" }, color: "red" },
      { k: "pin", p: [128.04, 38.255], text: { ko: "940고지", en: "HILL 940" }, color: "red", lift: 70 },
      { k: "pin", p: [128.051, 38.252], text: { ko: "773고지", en: "HILL 773" }, color: "red" },
    ],
    stampPos: { x: 790, y: 520, rot: -7 },
    // ※ 사용자 제안 '포탄 36만 발'은 사료 확인 불가 → 확인된 결정적 요인으로 대체 (출처 확인 시 아래 3줄만 교체)
    ko: { stamp: "땅속 벙커", line1: "압도적 포격을 쏟아붓고도 왜", line2: "3주 동안 뚫지 못했을까?" },
    en: { stamp: "UNDERGROUND BUNKERS", line1: "WHY COULDN'T THEY BREACH IT", line2: "AFTER 3 WEEKS OF SHELLING?" },
  },
  // EP10 금성 전투 (1953) — 좌표는 episodes/kumsong/storyboard.json과 동일 (개략)
  kumsong: {
    raster: "kumsong_zoom",
    view: { center: [127.65, 38.39], span: 0.42 },
    items: [
      { k: "front", path: [[127.38, 38.27], [127.42, 38.29], [127.47, 38.34], [127.51, 38.39], [127.56, 38.425], [127.62, 38.43], [127.68, 38.415], [127.74, 38.38], [127.8, 38.33], [127.86, 38.3]] },
      { k: "arrow", path: [[127.465, 38.47], [127.483, 38.435], [127.5, 38.405]], color: "red" },
      { k: "arrow", path: [[127.54, 38.49], [127.543, 38.455], [127.546, 38.42]], color: "red" },
      { k: "arrow", path: [[127.745, 38.43], [127.725, 38.4], [127.71, 38.375]], color: "red" },
      { k: "pin", p: [127.585, 38.445], text: { ko: "금성", en: "KUMSONG" }, color: "red" },
      { k: "pin", p: [127.611, 38.399], text: { ko: "금성천", en: "KUMSONG RIVER" }, color: "blue", lift: 40 },
    ],
    stampPos: { x: 540, y: 640, rot: -7 },
    ko: { stamp: "24만 대공세", line1: "휴전 14일 전 24만 대군을 쏟아붓고도 왜", line2: "끝내 돌파하지 못했을까?" },
    en: { stamp: "240,000 TROOPS", line1: "WHY COULDN'T 240,000 TROOPS BREAK THROUGH", line2: "JUST 14 DAYS BEFORE THE ARMISTICE?" },
  },
  // EP11 인천상륙작전과 서울 수복 (1950) — 좌표는 episodes/incheon/storyboard.json과 동일 (개략), 인물은 맥아더 공개 사진 누끼(thumb_photo)
  incheon: {
    raster: "incheon_sea",
    view: { center: [126.914, 37.53], span: 0.75 },
    items: [
      { k: "arrow", path: [[126.6, 37.476], [126.67, 37.492], [126.75, 37.505], [126.83, 37.512], [126.9, 37.517]], color: "blue" },
      { k: "arrow", path: [[126.66, 37.488], [126.73, 37.53], [126.79, 37.56], [126.84, 37.586], [126.93, 37.575]], color: "blue" },
      { k: "pin", p: [126.598, 37.476], text: { ko: "월미도", en: "WOLMI-DO" }, color: "blue" },
      { k: "pin", p: [126.975, 37.566], text: { ko: "서울", en: "SEOUL" }, color: "red", lift: 30 },
    ],
    subjectX: 1500,
    stampPos: { x: 600, y: 190, rot: -7 },
    ko: { stamp: "5,000대 1 도박", line1: "5,000대 1의 상륙을 성공하고도 왜", line2: "서울 탈환에 13일이나 걸렸을까?" },
    en: { stamp: "5,000 TO 1 GAMBLE", line1: "AFTER WINNING A 5,000 TO 1 GAMBLE", line2: "WHY DID IT TAKE 13 DAYS TO RETAKE SEOUL?" },
  },
  // EP12 단장의 능선 전투 (1951) — 좌표는 episodes/heartbreak/storyboard.json과 동일 (개략). 인물은 AI 상징 병사(thumb_subject)
  // 카피는 사용자 지정 (포탄 '수십만 발' = 미 2사단 포병 기록 56만 발 이상 · Hermes 『Truce Tent and Fighting Front』로 확인)
  heartbreak: {
    raster: "bloody_zoom",
    view: { center: [128.03, 38.296], span: 0.2 },
    items: [
      { k: "ridge", path: [[128.029, 38.278], [128.026, 38.287], [128.024, 38.293], [128.023, 38.298], [128.021, 38.305], [128.019, 38.315], [128.018, 38.324]] },
      { k: "arrow", path: [[128.0, 38.262], [128.002, 38.28], [128.004, 38.3], [128.006, 38.318]], color: "blue" },
      { k: "arrow", path: [[128.036, 38.258], [128.032, 38.271], [128.028, 38.282]], color: "blue" },
      { k: "pin", p: [128.026, 38.287], text: { ko: "894고지", en: "HILL 894" }, color: "red" },
      { k: "pin", p: [128.023, 38.298], text: { ko: "931고지", en: "HILL 931" }, color: "red", lift: 60 },
      { k: "pin", p: [128.019, 38.315], text: { ko: "851고지", en: "HILL 851" }, color: "red" },
    ],
    stampPos: { x: 470, y: 470, rot: -7 },
    ko: { stamp: "30일 능선 지옥", line1: "포탄 수십만 발을 퍼붓고도 왜", line2: "창자가 끊어질 때까지 못 뚫었을까?" },
    en: { stamp: "30 DAYS IN HELL", line1: "AFTER 30 DAYS OF CONTINUOUS ARTILLERY", line2: "WHY DID THEY CALL IT HEARTBREAK RIDGE?" },
  },
  // EP13 파로호(화천) 전투 (1951) — 사용자 지정 레퍼런스 변형(2026-10-30): 하단 38% 솔리드 블랙 + 2줄(흰/임팩트 레드 #FF2B2B), 상단 따옴표 서브 훅, 화천댐 차단 지점 빨간 타깃 링
  // 좌표는 episodes/paroho/storyboard.json과 동일 (개략). 스탬프 없음(사용자 레이아웃). 인물은 AI 국군 돌격병(thumb_subject)
  paroho: {
    raster: "paroho_zoom",
    rasterFallback: "yanggu",
    lakes: true,
    floor: 0.38,
    line2Color: "#FF2B2B",
    view: { center: [127.8305, 38.085], span: 0.3 },
    items: [
      { k: "arrow", path: [[127.92, 38.01], [127.862, 38.045], [127.83, 38.062], [127.8, 38.077], [127.782, 38.096], [127.772, 38.106]], color: "red" },
      { k: "arrow", path: [[127.73, 37.99], [127.744, 38.03], [127.755, 38.07], [127.76, 38.088]], color: "blue" },
      { k: "arrow", path: [[127.712, 37.99], [127.71, 38.05], [127.708, 38.095]], color: "blue" },
      { k: "ring", p: [127.768, 38.108], r: 70 },
      { k: "pin", p: [127.768, 38.111], text: { ko: "화천댐", en: "HWACHON DAM" }, color: "red", lift: 70 },
      { k: "pin", p: [127.84, 38.106], text: { ko: "파로호", en: "PARO LAKE" }, color: "blue", lift: 40 },
    ],
    subjectX: 1500,
    ko: { stamp: "", hook: "“호수 전체가 시체로 뒤덮였다”", line1: "사흘 밤낮 60km를 쫓아가", line2: "3만 대군이 몰살당한 이유" },
    en: { stamp: "", hook: "“The entire lake turned red”", line1: "CHASED FOR 3 DAYS AND NIGHTS", line2: "HOW 30,000 TROOPS WERE\nTRAPPED & DESTROYED" },
  },
};

type Lake = number[][];
let LAKES: Lake[] | null = null;

const W = 1920;
const H = 1080;
const STAMP_RED = "#D32F2F";
const YELLOW = "#FFD000";
const merc = (lat: number) => Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));

/** 글자 폭 대략 추정 → 패널 폭을 넘으면 글자 크기를 줄인다 (시니어 가독성: 지정 범위 안에서 최대) */
const estW = (t: string, en: boolean) =>
  [...t].reduce((a, ch) => {
    if (/[가-힣]/.test(ch)) return a + 0.98;
    if (ch === " ") return a + (en ? 0.24 : 0.3);
    if (/[0-9]/.test(ch)) return a + (en ? 0.5 : 0.56);
    if (/[A-Z]/.test(ch)) return a + 0.5;
    return a + 0.3;
  }, 0);
const fit = (t: string, en: boolean, max: number, min: number, width: number) =>
  Math.max(min, Math.min(max, Math.floor(width / Math.max(1, estW(t, en)))));

/** 글꼴을 실제로 불러온 뒤 canvas로 100px 기준 폭을 잰다 → 화면 폭에 맞는 글자 크기 계산용 (em 단위 폭 반환) */
const useMeasured = (texts: string[], font: string): number[] => {
  const [w, setW] = useState<number[]>([]);
  const [hd] = useState(() => delayRender("measure-text"));
  useEffect(() => {
    const fam = font.split(",")[0];
    Promise.all([document.fonts.load(`900 100px ${fam}`, texts.join("")), document.fonts.ready])
      .then(() => {
        const ctx = document.createElement("canvas").getContext("2d")!;
        ctx.font = `900 100px ${font}`;
        (ctx as any).letterSpacing = "-2px"; // 화면 자간(-0.02em)과 같게
        setW(texts.map((t) => ctx.measureText(t).width / 100));
      })
      .catch(() => setW([]))
      .finally(() => continueRender(hd));
  }, [texts.join("|"), font]);
  return w;
};

type RasterMeta = { name: string; file: string; west: number; east: number; north: number; south: number };
let RASTERS: RasterMeta[] | null = null;

export const MapThumb: React.FC<{ a: string; d: MapThumbDef; en?: boolean }> = ({ a, d, en }) => {
  const [meta, setMeta] = useState<RasterMeta[] | null>(RASTERS);
  const [h] = useState(() => (RASTERS ? null : delayRender("rasters")));
  useEffect(() => {
    if (RASTERS) return;
    fetch(staticFile("geo/rasters.json"))
      .then((r) => r.json())
      .then((j) => {
        RASTERS = j;
        setMeta(j);
        if (h !== null) continueRender(h);
      });
  }, [h]);
  const c = en ? d.en : d.ko;
  const { center, span } = d.view;
  const ppr = W / ((span * Math.PI) / 180); // 경도 1라디안당 픽셀
  const X = (lon: number) => ((lon - (center[0] - span / 2)) / span) * W;
  const Y = (lat: number) => H / 2 - (merc(lat) - merc(center[1])) * ppr;
  const P = ([lon, lat]: LL) => `${X(lon).toFixed(1)},${Y(lat).toFixed(1)}`;
  const r = meta?.find((m) => m.name === d.raster) || (d.rasterFallback ? meta?.find((m) => m.name === d.rasterFallback) : undefined);
  const [lakes, setLakes] = useState<Lake[] | null>(LAKES);
  const [hl] = useState(() => (d.lakes && !LAKES ? delayRender("lakes") : null));
  useEffect(() => {
    if (!d.lakes || LAKES) return;
    fetch(staticFile("geo/water.json"))
      .then((x) => x.json())
      .then((j) => {
        const [w0, e0] = [center[0] - span, center[0] + span];
        LAKES = (j.lakes as Lake[]).filter((ring) => ring.some((q) => q[0] > w0 && q[0] < e0 && Math.abs(q[1] - center[1]) < span));
        setLakes(LAKES);
      })
      .catch(() => setLakes([]))
      .finally(() => hl !== null && continueRender(hl));
  }, [hl]);
  const FL = d.floor; // EP13 레퍼런스 변형
  const L2C = d.line2Color || YELLOW;
  // 글꼴: 한국어 Pretendard Black(900) / 영문 Montserrat Black(900) — 실제 900 굵기 파일이라 가짜 볼드 없음
  const head = en ? "'Montserrat', 'Anton', sans-serif" : "'Pretendard', 'Black Han Sans', sans-serif";
  // 2줄은 실제 글꼴 폭을 재서 가로를 꽉 채운다 (레퍼런스 '역사 사랑방': 글자가 화면 폭의 약 90%)
  // Line 2는 "\n"으로 두 줄 가능 (EP13 영문처럼 긴 문구) — 가장 긴 줄 기준으로 크기 계산
  const rows2 = c.line2.split("\n");
  const [m1, ...mr] = useMeasured([c.line1, ...rows2], head);
  const m2 = mr.length ? Math.max(...mr) : 0;
  let l2 = Math.min(d.floor ? 190 : 170, Math.floor((W * 0.92) / m2));
  let l1 = Math.min(d.floor ? 176 : 150, Math.floor((W * 0.9) / m1));
  if (l1 > l2 / 1.08) l1 = Math.floor(l2 / 1.08); // Line 2가 항상 더 크게
  if (!m1 || !m2) { l1 = fit(c.line1, !!en, 110, 64, W * 0.9); l2 = fit(c.line2, !!en, 130, 80, W * 0.92); }
  // 레퍼런스 구조: Line 2만 솔리드 블랙 바 위, Line 1은 바로 위 사진 위(어두운 띠 + 굵은 검정 외곽선)
  const PAD = 18;
  let panelTop = Math.round(H - (PAD * 2 + l2 * 1.02)); // 솔리드 블랙 바 시작
  let line1Top = Math.round(panelTop - l1 * 1.12 - 6); // Line 1 위치 (사진 위)
  let line2Top = panelTop;
  if (FL) {
    // 하단 FL 비율 솔리드 블랙 바닥판 안에 2줄을 세로 가운데 정렬 (레퍼런스: 2줄 모두 검은 바닥 위)
    panelTop = Math.round(H * (1 - FL));
    const gap = Math.round(l2 * 0.1);
    // 바닥판 높이를 넘으면 함께 줄임
    const avail = H - panelTop - 24;
    let block = l1 * 1.08 + gap + l2 * 1.04 * rows2.length;
    if (block > avail) { const k = avail / block; l1 = Math.floor(l1 * k); l2 = Math.floor(l2 * k); block = avail; }
    line1Top = Math.round(panelTop + (H - panelTop - block) / 2 + 6);
    line2Top = Math.round(line1Top + l1 * 1.08 + gap);
  }
  const st = d.stampPos || { x: 760, y: 120, rot: -7 };
  const sx = d.subjectX ?? 1460;
  const col = (k?: string) => (k === "blue" ? "#4f8cff" : "#ff3b30");
  return (
    <AbsoluteFill style={{ background: "#2a2c30", overflow: "hidden" }}>
      <style>{`@font-face{font-family:'Pretendard';font-weight:900;font-style:normal;src:url(${staticFile("fonts/Pretendard-Black.woff2")}) format('woff2');}`}</style>
      {/* Layer 1: 흑백 3D 지형 */}
      {r && (
        <Img
          src={staticFile(r.file)}
          style={{
            position: "absolute",
            left: X(r.west),
            top: Y(r.north),
            width: X(r.east) - X(r.west),
            height: Y(r.south) - Y(r.north),
            filter: "grayscale(1) brightness(0.45) contrast(1.2)",
          }}
        />
      )}
      {/* Layer 1-2: 호수 (EP13) — 흑백 지형 위에 짙은 청회색 수면 */}
      {d.lakes && lakes && (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          {lakes.map((ring, i) => (
            <path key={i} d={"M" + ring.map((q) => P(q as LL)).join(" L") + " Z"} fill="#26394d" stroke="#8fb3d9" strokeWidth={2.5} strokeOpacity={0.55} opacity={0.95} />
          ))}
        </svg>
      )}
      {/* Layer 2: 작전선 */}
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <defs>
          {["red", "blue"].map((k) => (
            <marker key={k} id={`ah-${k}`} viewBox="0 0 10 10" refX="5" refY="5" markerWidth="3.2" markerHeight="3.2" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill={col(k)} />
            </marker>
          ))}
        </defs>
        {d.items.map((it, i) => {
          if (it.k === "front")
            return <polyline key={i} points={it.path.map(P).join(" ")} fill="none" stroke="#fff" strokeWidth={6} strokeDasharray="22 14" opacity={0.9} />;
          if (it.k === "ridge")
            return (
              <g key={i}>
                <polyline points={it.path.map(P).join(" ")} fill="none" stroke="#000" strokeWidth={18} strokeLinecap="round" opacity={0.35} />
                <polyline points={it.path.map(P).join(" ")} fill="none" stroke="#ff3b30" strokeWidth={10} strokeLinecap="round" />
              </g>
            );
          if (it.k === "arrow")
            return (
              <g key={i}>
                <polyline points={it.path.map(P).join(" ")} fill="none" stroke="#000" strokeWidth={20} strokeLinejoin="round" strokeLinecap="round" opacity={0.3} />
                <polyline points={it.path.map(P).join(" ")} fill="none" stroke={col(it.color)} strokeWidth={13} strokeLinejoin="round" strokeLinecap="round" markerEnd={`url(#ah-${it.color || "red"})`} />
              </g>
            );
          if (it.k === "ring") {
            const rr = it.r || 70;
            return (
              <g key={i} transform={`translate(${X(it.p[0]).toFixed(1)},${Y(it.p[1]).toFixed(1)})`}>
                <circle r={rr + 8} fill="none" stroke="#000" strokeWidth={18} opacity={0.35} />
                <circle r={rr} fill="rgba(255,43,43,.12)" stroke="#FF2B2B" strokeWidth={11} />
                <circle r={rr + 30} fill="none" stroke="#FF2B2B" strokeWidth={5} strokeDasharray="16 12" />
                {[0, 90, 180, 270].map((a) => (
                  <line key={a} x1={0} y1={-(rr + 46)} x2={0} y2={-(rr - 14)} stroke="#FF2B2B" strokeWidth={8} strokeLinecap="round" transform={`rotate(${a})`} />
                ))}
              </g>
            );
          }
          return null;
        })}
      </svg>
      {d.items.map((it, i) =>
        it.k === "pin" ? (
          <div key={i} style={{ position: "absolute", left: X(it.p[0]), top: Y(it.p[1]), transform: "translate(-50%,-100%)", textAlign: "center" }}>
            <div style={{ background: "#0b0b0b", color: "#fff", fontFamily: head, fontWeight: 900, fontSize: en ? 32 : 36, padding: "6px 16px 5px", whiteSpace: "nowrap", border: "2px solid rgba(255,255,255,.85)", borderRadius: 8, boxShadow: "0 4px 12px rgba(0,0,0,.6)", letterSpacing: "-0.01em" }}>{en ? it.text.en : it.text.ko}</div>
            <div style={{ width: 4, height: 26 + (it.lift || 0), background: "#fff", margin: "0 auto" }} />
            <div style={{ width: 22, height: 22, borderRadius: 11, background: col(it.color), border: "4px solid #fff", margin: "-4px auto 0", transform: "translateY(11px)" }} />
          </div>
        ) : null,
      )}
      {/* Layer 3: 인물 흑백 누끼 (우측 40~45%) — 흰 림 라이트만(주황 글로우 없음), 하단은 블랙 판 속으로 마스킹 */}
      <Img
        src={staticFile(`ep/${a}/ai/thumb_subject.png`)}
        style={{
          position: "absolute",
          height: 1100,
          top: -20,
          left: sx,
          transform: "translateX(-50%)",
          WebkitMaskImage: FL ? `linear-gradient(to bottom, black ${(((panelTop - 200 + 20) / 1100) * 100).toFixed(1)}%, transparent ${(((panelTop + 10 + 20) / 1100) * 100).toFixed(1)}%)` : "linear-gradient(to bottom, black 72%, transparent 96%)",
          maskImage: FL ? `linear-gradient(to bottom, black ${(((panelTop - 200 + 20) / 1100) * 100).toFixed(1)}%, transparent ${(((panelTop + 10 + 20) / 1100) * 100).toFixed(1)}%)` : "linear-gradient(to bottom, black 72%, transparent 96%)",
          filter: "grayscale(1) contrast(1.2) brightness(1.05) drop-shadow(0 0 3px rgba(255,255,255,.9)) drop-shadow(0 0 10px rgba(255,255,255,.4))",
        }}
      />
      {/* Layer 4: 붉은 사각 스탬프 (EP13처럼 stamp가 빈 문자열이면 생략) */}
      {c.stamp && <div
        style={{
          position: "absolute",
          left: st.x,
          top: Math.min(st.y, line1Top - 70),
          transform: `translate(-50%,-50%) rotate(${st.rot ?? -7}deg)`,
          border: `6px solid ${STAMP_RED}`,
          outline: `3px solid ${STAMP_RED}`,
          outlineOffset: 8,
          background: "rgba(10,10,12,.6)",
          padding: "8px 30px 4px",
          color: STAMP_RED,
          fontFamily: head,
          fontWeight: 900,
          fontSize: en ? 56 : 84,
          letterSpacing: en ? 1 : "-0.02em",
          whiteSpace: "nowrap",
          textShadow: "0 2px 6px rgba(0,0,0,.7)",
        }}
      >
        {c.stamp}
      </div>}
      {/* Layer 5: 레퍼런스 구조 — Line 1 뒤만 어두운 띠(사진이 살짝 비침) + 맨 아래 Line 2용 솔리드 블랙 바(불투명 100%) */}
      {FL ? (
        // EP13: 경계만 36px 페이드 + 불투명 100% 블랙 바닥판
        <div style={{ position: "absolute", left: 0, right: 0, top: panelTop - 36, height: 36, background: "linear-gradient(to bottom, rgba(0,0,0,0), #000)" }} />
      ) : (
        <div style={{ position: "absolute", left: 0, right: 0, top: line1Top - 90, height: panelTop - line1Top + 90, background: "linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,.72) 45%, rgba(0,0,0,.88) 100%)" }} />
      )}
      <div style={{ position: "absolute", left: 0, right: 0, top: panelTop, bottom: 0, background: "#000000" }} />
      {/* EP13: 상단 서브 훅 (따옴표 · 임팩트 레드 + 굵은 검정 외곽선) */}
      {c.hook && (
        <div style={{ position: "absolute", left: 56, top: 34, fontFamily: head, fontWeight: 900, fontSize: en ? 66 : 76, color: L2C, whiteSpace: "nowrap", letterSpacing: "-0.02em", WebkitTextStroke: "10px #000", paintOrder: "stroke fill", textShadow: "0 4px 14px rgba(0,0,0,.85)" }}>{c.hook}</div>
      )}
      {/* Layer 6-1: Line 1 (흰색, 사진 위, 굵은 검정 외곽선) */}
      <div style={{ position: "absolute", left: 56, top: line1Top, fontFamily: head, fontWeight: 900, fontSize: l1, lineHeight: 1.1, color: "#FFFFFF", whiteSpace: "nowrap", letterSpacing: "-0.02em", WebkitTextStroke: `${Math.round(l1 * 0.09)}px #000000`, paintOrder: "stroke fill", textShadow: "0 6px 16px rgba(0,0,0,0.9)" }}>{c.line1}</div>
      {/* Layer 6-2: Line 2 (머스터드 옐로, 솔리드 블랙 바 위, 가장 크게) */}
      {FL ? (
        <div style={{ position: "absolute", left: 56, top: line2Top, fontFamily: head, fontWeight: 900, fontSize: l2, lineHeight: 1.04, color: L2C, whiteSpace: "pre", letterSpacing: "-0.02em" }}>{c.line2}</div>
      ) : (
        <div style={{ position: "absolute", left: 56, top: panelTop, height: H - panelTop, display: "flex", alignItems: "center", fontFamily: head, fontWeight: 900, fontSize: l2, lineHeight: 1, color: L2C, whiteSpace: "nowrap", letterSpacing: "-0.02em" }}>{c.line2}</div>
      )}
    </AbsoluteFill>
  );
};
