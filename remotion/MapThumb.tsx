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
  | { k: "arrow"; path: LL[]; color?: "red" | "blue" };
type Copy = { stamp: string; line1: string; line2: string };
export type MapThumbDef = {
  raster: string; // public/geo/rasters.json 의 name
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
    raster: "incheon",
    view: { center: [126.83, 37.47], span: 0.62 },
    items: [
      { k: "arrow", path: [[126.6, 37.476], [126.66, 37.49], [126.72, 37.505], [126.8, 37.51], [126.88, 37.516]], color: "blue" },
      { k: "arrow", path: [[126.66, 37.485], [126.73, 37.53], [126.79, 37.56], [126.835, 37.588]], color: "blue" },
      { k: "front", path: [[126.946, 37.586], [126.944, 37.577], [126.937, 37.571], [126.932, 37.566], [126.929, 37.559], [126.928, 37.551], [126.931, 37.543]] },
      { k: "pin", p: [126.598, 37.476], text: { ko: "월미도", en: "WOLMI-DO" }, color: "blue" },
      { k: "pin", p: [126.905, 37.517], text: { ko: "영등포", en: "YONGDUNGPO" }, color: "red", lift: 40 },
    ],
    subjectX: 1500,
    stampPos: { x: 560, y: 330, rot: -7 },
    ko: { stamp: "5,000대 1 도박", line1: "5,000대 1의 상륙을 성공하고도 왜", line2: "서울 탈환에 13일이나 걸렸을까?" },
    en: { stamp: "5,000 TO 1 GAMBLE", line1: "AFTER WINNING A 5,000 TO 1 GAMBLE", line2: "WHY DID IT TAKE 13 DAYS TO RETAKE SEOUL?" },
  },
};

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
  const r = meta?.find((m) => m.name === d.raster);
  // 글꼴: 한국어 Pretendard Black(900) / 영문 Montserrat Black(900) — 실제 900 굵기 파일이라 가짜 볼드 없음
  const head = en ? "'Montserrat', 'Anton', sans-serif" : "'Pretendard', 'Black Han Sans', sans-serif";
  // 2줄은 실제 글꼴 폭을 재서 가로를 꽉 채운다 (레퍼런스 '역사 사랑방': 글자가 화면 폭의 약 90%)
  const [m1, m2] = useMeasured([c.line1, c.line2], head);
  let l2 = Math.min(170, Math.floor((W * 0.92) / m2));
  let l1 = Math.min(150, Math.floor((W * 0.9) / m1));
  if (l1 > l2 / 1.08) l1 = Math.floor(l2 / 1.08); // Line 2가 항상 더 크게
  if (!m1 || !m2) { l1 = fit(c.line1, !!en, 110, 64, W * 0.9); l2 = fit(c.line2, !!en, 130, 80, W * 0.92); }
  // 레퍼런스 구조: Line 2만 솔리드 블랙 바 위, Line 1은 바로 위 사진 위(어두운 띠 + 굵은 검정 외곽선)
  const PAD = 18;
  const panelTop = Math.round(H - (PAD * 2 + l2 * 1.02)); // 솔리드 블랙 바 시작
  const line1Top = Math.round(panelTop - l1 * 1.12 - 6); // Line 1 위치 (사진 위)
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
          WebkitMaskImage: "linear-gradient(to bottom, black 72%, transparent 96%)",
          maskImage: "linear-gradient(to bottom, black 72%, transparent 96%)",
          filter: "grayscale(1) contrast(1.2) brightness(1.05) drop-shadow(0 0 3px rgba(255,255,255,.9)) drop-shadow(0 0 10px rgba(255,255,255,.4))",
        }}
      />
      {/* Layer 4: 붉은 사각 스탬프 */}
      <div
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
      </div>
      {/* Layer 5: 레퍼런스 구조 — Line 1 뒤만 어두운 띠(사진이 살짝 비침) + 맨 아래 Line 2용 솔리드 블랙 바(불투명 100%) */}
      <div style={{ position: "absolute", left: 0, right: 0, top: line1Top - 90, height: panelTop - line1Top + 90, background: "linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,.72) 45%, rgba(0,0,0,.88) 100%)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: panelTop, bottom: 0, background: "#000000" }} />
      {/* Layer 6-1: Line 1 (흰색, 사진 위, 굵은 검정 외곽선) */}
      <div style={{ position: "absolute", left: 56, top: line1Top, fontFamily: head, fontWeight: 900, fontSize: l1, lineHeight: 1.1, color: "#FFFFFF", whiteSpace: "nowrap", letterSpacing: "-0.02em", WebkitTextStroke: `${Math.round(l1 * 0.09)}px #000000`, paintOrder: "stroke fill", textShadow: "0 6px 16px rgba(0,0,0,0.9)" }}>{c.line1}</div>
      {/* Layer 6-2: Line 2 (머스터드 옐로, 솔리드 블랙 바 위, 가장 크게) */}
      <div style={{ position: "absolute", left: 56, top: panelTop, height: H - panelTop, display: "flex", alignItems: "center", fontFamily: head, fontWeight: 900, fontSize: l2, lineHeight: 1, color: YELLOW, whiteSpace: "nowrap", letterSpacing: "-0.02em" }}>{c.line2}</div>
    </AbsoluteFill>
  );
};
