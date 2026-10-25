/**
 * '격전의 지도' 공통 썸네일 표준 (2026-10-25 확정, EP09부터 모든 새 에피소드 A안 기본)
 * 1920×1080 · 6개 레이어:
 *  1 흑백 3D 지형(채도 0 · 대비 +25% · 밝기 -20%)  2 작전선(전선 점선·거점 핀·진격 화살표)
 *  3 인물 흑백 누끼(우측 40~45%, 화이트/오렌지 림 라이트)  4 붉은 사각 스탬프(-6~-8deg, 4px #D32F2F)
 *  5 하단 40% 블랙 그라데이션  6 하단 좌측 2줄 질문형 카피(Line1 흰 72~76px / Line2 #FFD000 88~94px)
 * 에피소드는 MAPT 표에 한 줄 추가 → `mode=thumb`가 _ko_A / _en_A를 렌더.
 */
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile } from "remotion";
import "@fontsource/anton/400.css";

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
    view: { center: [128.07, 38.238], span: 0.2 },
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
    stampPos: { x: 985, y: 545, rot: -7 },
    // ※ 사용자 제안 '포탄 36만 발'은 사료 확인 불가 → 확인된 결정적 요인으로 대체 (출처 확인 시 아래 3줄만 교체)
    ko: { stamp: "땅속 벙커", line1: "압도적 포격을 쏟아붓고도 왜", line2: "3주 동안 뚫지 못했을까?" },
    en: { stamp: "UNDERGROUND BUNKERS", line1: "WHY COULDN'T THEY BREACH IT", line2: "AFTER 3 WEEKS OF SHELLING?" },
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
  const head = en ? "'Anton', 'Bebas Neue', sans-serif" : "'Black Han Sans', sans-serif";
  const l1 = fit(c.line1, !!en, 76, 60, 1180);
  const l2 = fit(c.line2, !!en, 94, 72, 1240);
  const st = d.stampPos || { x: 760, y: 120, rot: -7 };
  const sx = d.subjectX ?? 1500;
  const col = (k?: string) => (k === "blue" ? "#4f8cff" : "#ff3b30");
  return (
    <AbsoluteFill style={{ background: "#2a2c30", overflow: "hidden" }}>
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
            filter: "grayscale(1) contrast(1.25) brightness(0.8)",
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
            <div style={{ background: col(it.color), color: "#fff", fontFamily: head, fontSize: en ? 34 : 32, padding: "4px 14px 2px", whiteSpace: "nowrap", boxShadow: "0 4px 12px rgba(0,0,0,.6)", letterSpacing: en ? 1 : 0 }}>{en ? it.text.en : it.text.ko}</div>
            <div style={{ width: 4, height: 26 + (it.lift || 0), background: "#fff", margin: "0 auto" }} />
            <div style={{ width: 22, height: 22, borderRadius: 11, background: col(it.color), border: "4px solid #fff", margin: "-4px auto 0", transform: "translateY(11px)" }} />
          </div>
        ) : null,
      )}
      {/* Layer 3: 인물 흑백 누끼 (우측 40~45%) + 림 라이트 */}
      <Img
        src={staticFile(`ep/${a}/ai/thumb_subject.png`)}
        style={{
          position: "absolute",
          height: 1080,
          top: 20,
          left: sx,
          transform: "translateX(-50%)",
          filter:
            "grayscale(1) contrast(1.2) brightness(1.05) drop-shadow(0 0 3px rgba(255,255,255,.95)) drop-shadow(0 0 10px rgba(255,255,255,.55)) drop-shadow(0 0 26px rgba(255,140,40,.85))",
        }}
      />
      {/* Layer 4: 붉은 사각 스탬프 */}
      <div
        style={{
          position: "absolute",
          left: st.x,
          top: st.y,
          transform: `translate(-50%,-50%) rotate(${st.rot ?? -7}deg)`,
          border: `4px solid ${STAMP_RED}`,
          outline: `2px solid ${STAMP_RED}`,
          outlineOffset: 6,
          background: "rgba(10,10,12,.55)",
          padding: "10px 26px 6px",
          color: STAMP_RED,
          fontFamily: head,
          fontWeight: 900,
          fontSize: en ? 52 : 50,
          letterSpacing: en ? 3 : 2,
          whiteSpace: "nowrap",
          textShadow: "0 2px 6px rgba(0,0,0,.7)",
        }}
      >
        {c.stamp}
      </div>
      {/* Layer 5: 하단 40% 블랙 그라데이션 */}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: H * 0.4, background: "linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.7) 60%, transparent 100%)" }} />
      {/* Layer 6: 하단 좌측 2줄 질문형 카피 */}
      <div style={{ position: "absolute", left: 80, bottom: 70 }}>
        <div style={{ fontFamily: head, fontSize: l1, lineHeight: 1.12, color: "#FFFFFF", whiteSpace: "nowrap", letterSpacing: en ? 1 : -1, textShadow: "0 4px 12px rgba(0,0,0,0.8)" }}>{c.line1}</div>
        <div
          style={{
            fontFamily: head,
            fontSize: l2,
            lineHeight: 1.12,
            marginTop: 8,
            color: YELLOW,
            whiteSpace: "nowrap",
            letterSpacing: en ? 1 : -1,
            WebkitTextStroke: "3px #000000",
            paintOrder: "stroke fill",
            textShadow: "0 6px 18px rgba(0,0,0,0.95), 0 2px 4px rgba(0,0,0,0.9)",
          }}
        >
          {c.line2}
        </div>
      </div>
    </AbsoluteFill>
  );
};
