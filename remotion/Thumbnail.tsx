import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile } from "remotion";
import "@fontsource/black-han-sans/400.css";
import "@fontsource/bebas-neue/400.css";
import { C, F, setLang } from "./theme";
import { MAPT, MapThumb } from "./MapThumb";
import { FRONT, FrontThumb, NAKTONG_FRONT } from "./FrontThumb";

/* =====================================================================================
 * ★ 썸네일 표준 v4 — '스토리텔링 꼴라주 + 3D 몬스터 타이포' (2026-11-02 사용자 지시서, EP15 낙동강·EP16 도솔산부터)
 *   레퍼런스: 별별역사(215만 조회수) 썸네일 구조. 1920×1080 픽셀 단위 그대로.
 *   [최상단] 네온 레드 인용구 배너 (top 25, 40px, 4px 검정 외곽선)
 *   [중단 좌] 핵심 인물 고대비 흑백 누끼 (left 30, bottom 350) + 입가 말풍선 + 15도 붉은 사각 직인
 *   [중단 우] 흑백 전장 지도 + 붉은 반투명 타깃 하이라이트 + 대형 군기 + 3D 골드 돌격 화살표 3개
 *   [하단 45%] 칠흑 블랙 딤 (#000 0% → #000 65% → .9 85% → 투명)
 *   [최하단] 2줄 3D 몬스터 텍스트 — Black Han Sans, Line1 96 흰색 / Line2 114 레드 #FF2222,
 *            line-height 1.02, 자간 -4px, 두 줄 비율 그대로 가장 긴 줄이 화면 폭 95%를 채우도록 자동 배율
 *   에피소드는 COLLAGE 표에 한 줄 → 한국어 A안이 이 디자인으로 렌더 (FRONT·MAPT보다 우선)
 * ===================================================================================== */
type CLL = [number, number];
type FlagKind = "kr" | "nk" | "marine";
export type CollageDef = {
  quote: string;
  person: { src: string; h: number; w: number; pos?: string; filter?: string };
  bubble: { text: string; x: number; y: number; tail: [number, number]; size?: number };
  stamp: { text: string; x: number; y: number; rot?: number; size?: number };
  map: {
    rasters: string[];
    view: { center: CLL; span: number };
    red: CLL[]; // 타깃(적) 영역 — 붉은 반투명
    blue?: CLL[]; // 아군 방어선 (푸른 라인)
    arrows: CLL[][]; // 3D 골드 화살표 (각 경로 마지막 점이 화살촉)
    arrowW?: number;
    flags: { kind: FlagKind; at: CLL; h: number; rot?: number }[];
    outline?: boolean; // 붉은 영역 경계선 (육지 안 전선일 때)
  };
  line1: string;
  line2: string;
};

const NAK_ENEMY_CLOSE: CLL[] = [[128.3, 34.0], [125.0, 34.0], [124.0, 39.5], [124.0, 44.0], [131.5, 44.0], [129.42, 38.2], [129.42, 36.42]];

export const COLLAGE: Record<string, CollageDef> = {
  // EP15 낙동강 전선 최후의 사수 (ep15-naktong)
  naktong: {
    quote: "마지막 방어선이 뚫리면 대한민국은 영원히 끝난다",
    person: { src: "ep/naktong/ai/thumb_subject.png", h: 690, w: 560, pos: "50% 0%" },
    bubble: { text: "더 이상 물러설 곳은 없다!", x: 560, y: 150, tail: [372, 332] },
    stamp: { text: "사수", x: 470, y: 560, rot: -15 },
    map: {
      rasters: ["korea", "south"],
      view: { center: [125.39, 35.87], span: 13 },
      red: [...NAKTONG_FRONT, ...NAK_ENEMY_CLOSE],
      blue: NAKTONG_FRONT,
      arrows: [
        [[126.95, 37.5], [127.45, 36.8], [128.22, 36.24]],
        [[128.6, 37.55], [128.8, 37.05], [128.72, 36.5]],
        [[126.9, 36.3], [127.45, 35.8], [128.26, 35.68]],
      ],
      arrowW: 34,
      flags: [
        { kind: "nk", at: [128.2, 37.85], h: 84, rot: -4 },
        { kind: "kr", at: [129.15, 35.95], h: 70, rot: 3 },
      ],
    },
    line1: "서울도 대전도 다 털렸는데",
    line2: "‘낙동강’ 하나로 어떻게 버텼을까?",
  },
  // EP16 도솔산 1,148m 암벽 혈전 (ep16-dosolsan)
  "ep16-dosolsan": {
    quote: "미 해병대도 포기한 악마의 암벽 요새",
    person: { src: "ep/ep16-dosolsan/ai/thumb_cut.png", h: 640, w: 860, pos: "30% 0%" },
    bubble: { text: "야간에 착검하고 올라간다!", x: 540, y: 150, tail: [332, 405] },
    stamp: { text: "탈환", x: 640, y: 590, rot: -15 },
    map: {
      rasters: ["yanggu", "dosol_zoom"],
      view: { center: [128.036, 38.2026], span: 0.36 },
      outline: true,
      red: [[127.95, 38.21], [127.98, 38.212], [128.02, 38.216], [128.05, 38.214], [128.075, 38.209], [128.095, 38.212], [128.112, 38.207], [128.128, 38.202], [128.145, 38.207], [128.165, 38.214], [128.19, 38.219], [128.24, 38.224], [128.3, 38.226], [128.3, 38.4], [127.95, 38.4]],
      blue: [[127.9, 38.195], [128.0, 38.199], [128.06, 38.196], [128.12, 38.193], [128.18, 38.197], [128.3, 38.2]],
      arrows: [
        [[128.0435, 38.188], [128.055, 38.205], [128.0716, 38.227]],
        [[128.1, 38.186], [128.1, 38.206], [128.1, 38.229]],
        [[128.156, 38.188], [128.145, 38.205], [128.128, 38.227]],
      ],
      arrowW: 38,
      flags: [{ kind: "marine", at: [128.1, 38.2385], h: 104, rot: -3 }],
    },
    line1: "미 해병대도 피 흘리며 후퇴했는데",
    line2: "한국 해병은 ‘바위산’을 어떻게 뚫었을까?",
  },
};

const CW = 1920;
const CH = 1080;
const RED22 = "#FF2222";
const MONSTER = "'Black Han Sans', 'Pretendard', sans-serif";
const PRET = "'Pretendard', 'Black Han Sans', sans-serif";
const cMerc = (lat: number) => Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
type CRaster = { name: string; west: number; east: number; north: number; south: number };
let C_RASTERS: CRaster[] | null = null;

/** 태극기 (3:2) — 폭 w */
const FlagKR: React.FC<{ w: number }> = ({ w }) => {
  const h = (w * 2) / 3;
  const R = h / 4;
  const ang = (Math.atan2(2, 3) * 180) / Math.PI; // 대각선 각도
  const bar = R / 6; // 괘 두께 (지름의 1/12)
  const gap = bar / 2;
  const len = R; // 괘 길이
  const tri = (pattern: number[][], cx: number, cy: number, rot: number, k: string) => (
    <g key={k} transform={`translate(${cx},${cy}) rotate(${rot})`}>
      {pattern.map((seg, i) => {
        const y = (i - 1) * (bar + gap) - bar / 2;
        return seg.length === 1 ? (
          <rect key={i} x={-len / 2} y={y} width={len} height={bar} fill="#000" />
        ) : (
          <g key={i}>
            <rect x={-len / 2} y={y} width={len / 2 - gap / 2} height={bar} fill="#000" />
            <rect x={gap / 2} y={y} width={len / 2 - gap / 2} height={bar} fill="#000" />
          </g>
        );
      })}
    </g>
  );
  const d = R + R / 2 + len / 4 + R * 0.35; // 중심→괘 중심 거리
  const rad = (a: number) => (a * Math.PI) / 180;
  const pos = (a: number) => [w / 2 + Math.cos(rad(a)) * d, h / 2 + Math.sin(rad(a)) * d];
  const S = [1], B = [0, 0];
  const [p1, p2, p3, p4] = [pos(180 + ang), pos(-ang), pos(180 - ang), pos(ang)];
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <rect width={w} height={h} fill="#fff" />
      <g transform={`translate(${w / 2},${h / 2}) rotate(${ang})`}>
        <path d={`M ${-R} 0 A ${R} ${R} 0 0 1 ${R} 0 Z`} fill="#CD2E3A" />
        <path d={`M ${-R} 0 A ${R} ${R} 0 0 0 ${R} 0 Z`} fill="#0047A0" />
        <circle cx={-R / 2} cy={0} r={R / 2} fill="#0047A0" />
        <circle cx={R / 2} cy={0} r={R / 2} fill="#CD2E3A" />
      </g>
      {tri([S, S, S], p1[0], p1[1], 90 + ang, "geon")}
      {tri([B, S, B], p2[0], p2[1], 90 - ang, "gam")}
      {tri([S, B, S], p3[0], p3[1], 90 - ang, "ri")}
      {tri([B, B, B], p4[0], p4[1], 90 + ang, "gon")}
    </svg>
  );
};

/** 인공기 (2:1) — 폭 w */
const FlagNK: React.FC<{ w: number }> = ({ w }) => {
  const h = w / 2;
  const u = h / 30;
  const cx = w * 0.36;
  const r = u * 8;
  const star = Array.from({ length: 10 }, (_, i) => {
    const a = -Math.PI / 2 + (i * Math.PI) / 5;
    const rr = i % 2 ? r * 0.82 * 0.382 : r * 0.82;
    return `${(cx + Math.cos(a) * rr).toFixed(1)},${(h / 2 + Math.sin(a) * rr).toFixed(1)}`;
  }).join(" ");
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <rect width={w} height={h} fill="#024FA2" />
      <rect y={u * 5} width={w} height={u * 20} fill="#fff" />
      <rect y={u * 6} width={w} height={u * 18} fill="#ED1C27" />
      <circle cx={cx} cy={h / 2} r={r} fill="#fff" />
      <polygon points={star} fill="#ED1C27" />
    </svg>
  );
};

/** 해병대 깃발 (3:2) — 붉은 바탕 + 노란 닻·별 + '해병대' */
const FlagMarine: React.FC<{ w: number }> = ({ w }) => {
  const h = (w * 2) / 3;
  const cx = w / 2;
  const s = h / 200;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <rect width={w} height={h} fill="#C8102E" />
      <rect x={6 * s} y={6 * s} width={w - 12 * s} height={h - 12 * s} fill="none" stroke="#FFD100" strokeWidth={5 * s} />
      <g transform={`translate(${cx},${78 * s}) scale(${s})`} fill="none" stroke="#FFD100" strokeWidth={10} strokeLinecap="round">
        <circle cx={0} cy={-46} r={11} />
        <line x1={0} y1={-35} x2={0} y2={46} />
        <line x1={-26} y1={-18} x2={26} y2={-18} />
        <path d="M -44 18 Q -40 52 0 50 Q 40 52 44 18" />
        <polyline points="-52,26 -44,14 -34,26" />
        <polyline points="52,26 44,14 34,26" />
      </g>
      <polygon
        transform={`translate(${cx},${32 * s}) scale(${s})`}
        points={Array.from({ length: 10 }, (_, i) => {
          const a = -Math.PI / 2 + (i * Math.PI) / 5;
          const rr = i % 2 ? 6 : 15;
          return `${(Math.cos(a) * rr).toFixed(1)},${(Math.sin(a) * rr).toFixed(1)}`;
        }).join(" ")}
        fill="#FFD100"
        opacity={0}
      />
      <text x={cx} y={176 * s} textAnchor="middle" fill="#FFD100" fontFamily={PRET} fontWeight={900} fontSize={44 * s} letterSpacing={-1}>
        해병대
      </text>
    </svg>
  );
};

/** 깃대에 걸린 대형 군기 — at 지점에 깃대 밑동, 깃발은 오른쪽으로 펄럭 */
const BigFlag: React.FC<{ kind: FlagKind; x: number; y: number; h: number; rot?: number }> = ({ kind, x, y, h, rot = 0 }) => {
  const fw = kind === "nk" ? h * 2 : h * 1.5;
  const pole = h * 1.6;
  const inner = kind === "kr" ? <FlagKR w={fw} /> : kind === "nk" ? <FlagNK w={fw} /> : <FlagMarine w={fw} />;
  return (
    <div style={{ position: "absolute", left: x, top: y - pole, width: fw + 20, height: pole, transform: `rotate(${rot}deg)`, transformOrigin: "0 100%", filter: "drop-shadow(0 14px 18px rgba(0,0,0,.85))" }}>
      {/* 깃대 */}
      <div style={{ position: "absolute", left: -6, top: -10, width: 12, height: pole + 10, background: "linear-gradient(90deg,#5a5a5a,#f2f2f2 45%,#6a6a6a)", border: "2px solid #000", borderRadius: 6 }} />
      <div style={{ position: "absolute", left: -11, top: -24, width: 22, height: 22, borderRadius: 11, background: "radial-gradient(circle at 35% 35%,#fff3a0,#d4a000 60%,#6b4e00)", border: "2px solid #000" }} />
      {/* 깃발 — 살짝 원근 + 펄럭이는 음영 */}
      <div style={{ position: "absolute", left: 6, top: 0, width: fw, height: kind === "nk" ? fw / 2 : (fw * 2) / 3, transform: "perspective(900px) rotateY(-14deg) skewY(3deg)", transformOrigin: "0 50%", border: "3px solid #000", overflow: "hidden" }}>
        {inner}
        <div style={{ position: "absolute", inset: 0, background: "repeating-linear-gradient(90deg, rgba(0,0,0,.28) 0%, rgba(255,255,255,.12) 12%, rgba(0,0,0,.28) 25%)", mixBlendMode: "multiply" }} />
      </div>
    </div>
  );
};

/** 3D 골드 돌격 화살표 — 입체 측면(돌출) + 8px 블랙 보더 + #FFE600→#FFAA00 */
const GoldArrow: React.FC<{ pts: [number, number][]; w: number; id: string }> = ({ pts, w, id }) => {
  const [x2, y2] = pts[pts.length - 1];
  const [x1, y1] = pts[pts.length - 2];
  const len = Math.hypot(x2 - x1, y2 - y1) || 1;
  const ux = (x2 - x1) / len;
  const uy = (y2 - y1) / len;
  const hl = w * 1.9;
  const hw = w * 1.35;
  const bx = x2 - ux * hl;
  const by = y2 - uy * hl;
  const body = [...pts.slice(0, -1), [bx + ux * 4, by + uy * 4]].map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const head = `${x2},${y2} ${(bx - uy * hw).toFixed(1)},${(by + ux * hw).toFixed(1)} ${(bx + uy * hw).toFixed(1)},${(by - ux * hw).toFixed(1)}`;
  const ys = pts.map((p) => p[1]);
  const shape = (stroke: string, sw: number, fill: string, k?: string, dy = 0) => (
    <g key={k} transform={dy ? `translate(0,${dy})` : undefined}>
      <polyline points={body} fill="none" stroke={stroke} strokeWidth={w + sw} strokeLinecap="butt" strokeLinejoin="round" />
      <polygon points={head} fill={fill} stroke={stroke} strokeWidth={sw} strokeLinejoin="round" />
      {fill !== stroke && <polyline points={body} fill="none" stroke={fill} strokeWidth={w} strokeLinecap="butt" strokeLinejoin="round" />}
    </g>
  );
  const DEPTH = 16;
  return (
    <g>
      <defs>
        <linearGradient id={`g-${id}`} gradientUnits="userSpaceOnUse" x1={0} y1={Math.min(...ys) - w} x2={0} y2={Math.max(...ys) + w}>
          <stop offset="0" stopColor="#FFE600" />
          <stop offset="1" stopColor="#FFAA00" />
        </linearGradient>
      </defs>
      {/* 깊은 드롭섀도우 */}
      <g filter="url(#cg-shadow)" opacity={0.95}>{shape("#000", 16, "#000", "sh", DEPTH + 14)}</g>
      {/* 돌출 측면 (어두운 금색) */}
      {Array.from({ length: DEPTH }, (_, i) => shape("#000", 16, "#000", `ex-o${i}`, DEPTH - i))}
      {Array.from({ length: DEPTH }, (_, i) => shape("#7a4a00", 0, "#7a4a00", `ex-${i}`, DEPTH - i))}
      {/* 윗면 */}
      {shape("#000", 16, `url(#g-${id})`, "top")}
      {/* 하이라이트 */}
      <polyline points={body} fill="none" stroke="#FFF7B0" strokeWidth={w * 0.22} strokeLinecap="round" strokeLinejoin="round" opacity={0.75} transform={`translate(${-uy * w * 0.22},${ux * w * 0.22 * -1})`} />
    </g>
  );
};

const useMonsterMeasure = (texts: string[]): number[] => {
  const [w, setW] = useState<number[]>([]);
  const [hd] = useState(() => delayRender("collage-measure"));
  useEffect(() => {
    Promise.all([document.fonts.load(`400 100px 'Black Han Sans'`, texts.join("")), document.fonts.load(`900 40px 'Pretendard'`, "가"), document.fonts.ready])
      .then(() => {
        const ctx = document.createElement("canvas").getContext("2d")!;
        ctx.font = `400 100px ${MONSTER}`;
        setW(texts.map((t) => ctx.measureText(t).width / 100));
      })
      .catch(() => setW([]))
      .finally(() => continueRender(hd));
  }, [texts.join("|")]);
  return w;
};

export const CollageThumb: React.FC<{ d: CollageDef }> = ({ d }) => {
  const [meta, setMeta] = useState<CRaster[] | null>(C_RASTERS);
  const [h] = useState(() => (C_RASTERS ? null : delayRender("collage-rasters")));
  useEffect(() => {
    if (C_RASTERS) return;
    fetch(staticFile("geo/rasters.json"))
      .then((r) => r.json())
      .then((j) => {
        C_RASTERS = j;
        setMeta(j);
      })
      .finally(() => h !== null && continueRender(h));
  }, [h]);

  const m = d.map;
  const { center, span } = m.view;
  const ppr = CW / ((span * Math.PI) / 180);
  const X = (lon: number) => ((lon - (center[0] - span / 2)) / span) * CW;
  const Y = (lat: number) => CH / 2 - (cMerc(lat) - cMerc(center[1])) * ppr;
  const P = ([lo, la]: CLL) => `${X(lo).toFixed(1)},${Y(la).toFixed(1)}`;
  const rs = m.rasters.map((n) => meta?.find((r) => r.name === n)).filter(Boolean) as CRaster[];
  const FEATHER = "linear-gradient(to right, transparent 0, #000 8%, #000 92%, transparent 100%), linear-gradient(to bottom, transparent 0, #000 8%, #000 92%, transparent 100%)";
  const terrain = (filter: string) =>
    rs.map((r, i) => (
      <Img
        key={r.name}
        src={staticFile(`geo/thumbc/${r.name}.webp`)}
        style={{
          position: "absolute", left: X(r.west), top: Y(r.north), width: X(r.east) - X(r.west), height: Y(r.south) - Y(r.north), filter,
          WebkitMaskImage: FEATHER, WebkitMaskComposite: "source-in", maskComposite: "intersect",
        }}
      />
    ));
  const redClip = `polygon(${m.red.map(([lo, la]) => `${X(lo).toFixed(1)}px ${Y(la).toFixed(1)}px`).join(",")})`;

  // ----- 하단 몬스터 텍스트: 96:114 비율 유지, 가장 긴 줄이 화면 폭 95%를 채우도록 공통 배율 -----
  const [m1, m2] = useMonsterMeasure([d.line1, d.line2]);
  const LS = -4;
  const SW = 8;
  const width = (mm: number, text: string, size: number) => mm * size + LS * ([...text].length - 1) + SW;
  let k = 1;
  if (m1 && m2) k = Math.min((CW * 0.95) / width(m1, d.line1, 96), (CW * 0.95) / width(m2, d.line2, 114), 1.6);
  const s1 = Math.floor(96 * k);
  const s2 = Math.floor(114 * k);
  const MONSTER_STYLE: React.CSSProperties = {
    fontFamily: MONSTER, fontWeight: 400, lineHeight: 1.02, letterSpacing: LS, whiteSpace: "nowrap", textAlign: "center",
    WebkitTextStroke: `${SW}px #000000`, paintOrder: "stroke fill",
    textShadow: "0px 3px 0px #000000, 0px 6px 0px #000000, 0px 9px 0px #000000, 0px 12px 0px #000000, 0px 16px 20px rgba(0, 0, 0, 1)",
  };
  // 핵심 키워드(‘…’)는 레드 줄 안에서 노랑 하이라이트 없이 그대로 — 따옴표 자체가 강조

  const ps = d.person;
  const pTop = CH - 350 - ps.h;
  const bub = d.bubble;
  const bs = bub.size ?? 46;

  return (
    <AbsoluteFill style={{ background: "#111", overflow: "hidden" }}>
      <style>{`@font-face{font-family:'Pretendard';font-weight:900;font-style:normal;src:url(${staticFile("fonts/Pretendard-Black.woff2")}) format('woff2');}`}</style>
      {/* ── 지도: 흑백 전장 지도 ── */}
      <div style={{ position: "absolute", inset: 0, filter: "contrast(1.12)" }}>{terrain("grayscale(1) brightness(0.92) contrast(1.25)")}</div>
      {/* 타깃 영역: 붉은 반투명 하이라이트 */}
      <div style={{ position: "absolute", inset: 0, clipPath: redClip, opacity: 0.9 }}>
        {/* clip-path는 독립 합성 레이어라 지형을 한 번 더 깔고 그 위에 붉은 multiply (바다는 검붉게, 육지는 붉게) */}
        {terrain("grayscale(1) brightness(1.25) contrast(1.3)")}
        <div style={{ position: "absolute", inset: 0, background: "#FF1A1A", mixBlendMode: "multiply" }} />
      </div>
      {/* 왼쪽(인물 쪽)은 지도를 눌러 인물이 튀게 */}
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.45) 30%, rgba(0,0,0,0) 48%)" }} />
      <svg width={CW} height={CH} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <filter id="cg-shadow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="10" /></filter>
          <filter id="cg-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7" /></filter>
        </defs>
        {/* 붉은 영역 경계 */}
        {m.outline && <polygon points={m.red.map(P).join(" ")} fill="none" stroke="#FF2222" strokeWidth={4} strokeLinejoin="round" opacity={0.85} />}
        {/* 아군 방어선 (푸른 라인) */}
        {m.blue && (
          <g>
            <polyline points={m.blue.map(P).join(" ")} fill="none" stroke="#1E7BFF" strokeWidth={30} strokeLinejoin="round" strokeLinecap="round" opacity={0.75} filter="url(#cg-glow)" />
            <polyline points={m.blue.map(P).join(" ")} fill="none" stroke="#000" strokeWidth={17} strokeLinejoin="round" strokeLinecap="round" />
            <polyline points={m.blue.map(P).join(" ")} fill="none" stroke="#1E8BFF" strokeWidth={11} strokeLinejoin="round" strokeLinecap="round" />
            <polyline points={m.blue.map(P).join(" ")} fill="none" stroke="#BFE3FF" strokeWidth={3} strokeLinejoin="round" strokeLinecap="round" />
          </g>
        )}
        {/* 3D 골드 돌격 화살표 */}
        {m.arrows.map((a, i) => (
          <GoldArrow key={i} id={`a${i}`} w={m.arrowW ?? 40} pts={a.map(([lo, la]) => [X(lo), Y(la)] as [number, number])} />
        ))}
      </svg>
      {/* 대형 군기 */}
      {m.flags.map((f, i) => (
        <BigFlag key={i} kind={f.kind} x={X(f.at[0])} y={Y(f.at[1])} h={f.h} rot={f.rot} />
      ))}

      {/* ── 하단 45% 칠흑 블랙 딤 ── */}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: CH * 0.45, background: "linear-gradient(to top, #000000 0%, #000000 65%, rgba(0,0,0,0.9) 85%, transparent 100%)" }} />

      {/* ── 중단 좌측: 핵심 인물 고대비 흑백 누끼 ── */}
      <Img
        src={staticFile(ps.src)}
        style={{
          position: "absolute", left: 30, top: pTop, width: ps.w, height: ps.h, objectFit: "cover", objectPosition: ps.pos ?? "50% 0%",
          filter: ps.filter ?? "grayscale(1) contrast(1.45) brightness(1.08) drop-shadow(0 0 3px #fff) drop-shadow(0 0 14px rgba(0,0,0,.95))",
          WebkitMaskImage: "linear-gradient(to bottom, #000 80%, transparent 100%), linear-gradient(to right, #000 86%, transparent 100%)",
          WebkitMaskComposite: "source-in",
        }}
      />
      {/* 감정 말풍선 */}
      <div style={{ position: "absolute", left: bub.x, top: bub.y, zIndex: 3 }}>
        <svg width={1} height={1} style={{ position: "absolute", overflow: "visible", left: 0, top: 0 }}>
          <polygon points={`40,${bs * 1.1} 110,${bs * 1.1} ${bub.tail[0] - bub.x},${bub.tail[1] - bub.y}`} fill="#fff" stroke="#000" strokeWidth={6} strokeLinejoin="round" />
        </svg>
        <div style={{ position: "relative", background: "#fff", border: "6px solid #000", borderRadius: 40, padding: "16px 34px 14px", fontFamily: PRET, fontWeight: 900, fontSize: bs, lineHeight: 1.15, color: "#000", whiteSpace: "nowrap", letterSpacing: "-0.03em", boxShadow: "0 10px 0 #000, 0 16px 26px rgba(0,0,0,.7)" }}>
          {bub.text}
        </div>
      </div>
      {/* 15도 붉은 사각 직인 */}
      <div
        style={{
          position: "absolute", left: d.stamp.x, top: d.stamp.y, transform: `translate(-50%,-50%) rotate(${d.stamp.rot ?? -15}deg)`, zIndex: 4,
          background: "#D7141A", border: "7px solid #fff", outline: "6px solid #D7141A", padding: "6px 26px 4px",
          fontFamily: MONSTER, fontSize: d.stamp.size ?? 96, lineHeight: 1.05, color: "#fff", letterSpacing: 4, whiteSpace: "nowrap",
          boxShadow: "0 12px 28px rgba(0,0,0,.85)",
        }}
      >
        {d.stamp.text}
      </div>

      {/* ── 최상단 인용구 배너 ── */}
      <div style={{ position: "absolute", top: 25, left: 0, right: 0, textAlign: "center", zIndex: 5 }}>
        <span style={{ fontFamily: PRET, fontWeight: 900, fontSize: 40, color: "#FF2222", WebkitTextStroke: "4px #000", paintOrder: "stroke fill", textShadow: "0 3px 0 #000, 0 6px 14px rgba(0,0,0,.95)", letterSpacing: "-0.02em", whiteSpace: "nowrap" }}>
          “{d.quote}”
        </span>
      </div>

      {/* ── 최하단 2줄 3D 몬스터 텍스트 ── */}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 25, display: "flex", flexDirection: "column", alignItems: "center", zIndex: 6 }}>
        <div style={{ ...MONSTER_STYLE, fontSize: s1, color: "#FFFFFF" }}>{d.line1}</div>
        <div style={{ ...MONSTER_STYLE, fontSize: s2, color: RED22 }}>{d.line2}</div>
      </div>
    </AbsoluteFill>
  );
};


const big = (size: number, color: string, stroke = "#000", sw = 10): React.CSSProperties => ({
  fontFamily: F.head,
  fontSize: size,
  lineHeight: 1.02,
  color,
  WebkitTextStroke: `${sw}px ${stroke}`,
  paintOrder: "stroke fill",
  textShadow: "0 8px 24px rgba(0,0,0,.65)",
  whiteSpace: "nowrap",
});

const Tag: React.FC<{ text: string; bg?: string; fg?: string; size?: number }> = ({ text, bg = C.yellow, fg = "#111", size = 44 }) => (
  <div style={{ display: "inline-block", background: bg, color: fg, fontFamily: F.head, fontSize: size, padding: "6px 22px 2px", boxShadow: "0 6px 18px rgba(0,0,0,.5)" }}>{text}</div>
);

/** A안: 숫자 대결 — "1개 사단이 3개 사단을 무너뜨렸다" */
const ThumbA: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/rok_counter.jpg`)} style={{ position: "absolute", left: -160, top: -40, height: 800, filter: "contrast(1.1) saturate(1.1)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 30%, rgba(8,8,10,.92) 58%, #08080a 100%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 25% 60%, rgba(0,0,0,0) 40%, rgba(0,0,0,.55) 100%)" }} />
    <div style={{ position: "absolute", right: 46, top: 52, textAlign: "right" }}>
      <Tag text="1951 용문산 전투" />
      <div style={{ ...big(108, "#fff"), marginTop: 26 }}>1개 사단이</div>
      <div style={{ ...big(150, C.red, "#fff", 12), marginTop: 6 }}>3개 사단을</div>
      <div style={{ ...big(108, C.yellow), marginTop: 6 }}>무너뜨렸다</div>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
  </AbsoluteFill>
);

/** B안: 호수 미스터리 — "破虜湖 / 오랑캐를 깨뜨린 호수" */
const ThumbB: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/photos/s43_photo_0.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(.85) contrast(1.15) brightness(.62)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.15) 0%, rgba(0,0,0,.2) 45%, rgba(0,0,0,.85) 100%)" }} />
    <Img
      src={staticFile(`ep/${ep}/photos/s40_photo_0.jpg`)}
      style={{ position: "absolute", right: 40, top: 40, width: 360, height: 250, objectFit: "cover", border: "8px solid #fff", transform: "rotate(3deg)", filter: "grayscale(1) contrast(1.15)", boxShadow: "0 14px 34px rgba(0,0,0,.6)" }}
    />
    <div style={{ position: "absolute", left: 52, top: 60 }}>
      <div style={{ display: "flex", gap: 14 }}>
        {["破", "虜", "湖"].map((h, i) => (
          <div
            key={h}
            style={{
              width: 190,
              height: 190,
              background: i === 1 ? C.red : "#f3f1ea",
              color: i === 1 ? "#fff" : "#111",
              fontFamily: "'Noto Serif CJK KR','Noto Serif CJK SC', serif",
              fontWeight: 900,
              fontSize: 150,
              lineHeight: "190px",
              textAlign: "center",
              boxShadow: "0 12px 30px rgba(0,0,0,.6)",
            }}
          >
            {h}
          </div>
        ))}
      </div>
    </div>
    <div style={{ position: "absolute", left: 52, bottom: 50 }}>
      <div style={{ ...big(76, "#fff") }}>이 호수 이름이 왜</div>
      <div style={{ ...big(112, C.yellow), marginTop: 8 }}>'오랑캐를 깨뜨린'</div>
      <div style={{ ...big(76, "#fff"), marginTop: 8 }}>호수일까?</div>
    </div>
  </AbsoluteFill>
);

/** 영문 A안: "1 DIVISION vs 3 — AND IT WON" */
const ThumbA_EN: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/rok_counter.jpg`)} style={{ position: "absolute", left: -160, top: -40, height: 800, filter: "contrast(1.1) saturate(1.1)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 30%, rgba(8,8,10,.92) 56%, #08080a 100%)" }} />
    <div style={{ position: "absolute", right: 50, top: 46, textAlign: "right" }}>
      <Tag text="KOREA · MAY 1951" />
      <div style={{ ...big(120, "#fff", "#000", 8), marginTop: 22, letterSpacing: 1 }}>1 DIVISION</div>
      <div style={{ ...big(190, C.red, "#fff", 10), marginTop: -6 }}>VS 3</div>
      <div style={{ ...big(104, C.yellow, "#000", 8), marginTop: -4 }}>AND IT WON</div>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
  </AbsoluteFill>
);

/** 영문 B안: 破虜湖 — "THE LAKE THAT DEFEATED THE INVADERS" */
const ThumbB_EN: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/photos/s43_photo_0.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(.85) contrast(1.15) brightness(.62)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.15) 0%, rgba(0,0,0,.2) 40%, rgba(0,0,0,.88) 100%)" }} />
    <Img
      src={staticFile(`ep/${ep}/photos/s40_photo_0.jpg`)}
      style={{ position: "absolute", right: 40, top: 40, width: 360, height: 250, objectFit: "cover", border: "8px solid #fff", transform: "rotate(3deg)", filter: "grayscale(1) contrast(1.15)", boxShadow: "0 14px 34px rgba(0,0,0,.6)" }}
    />
    <div style={{ position: "absolute", left: 52, top: 56, display: "flex", gap: 14 }}>
      {["破", "虜", "湖"].map((h, i) => (
        <div key={h} style={{ width: 170, height: 170, background: i === 1 ? C.red : "#f3f1ea", color: i === 1 ? "#fff" : "#111", fontFamily: "'Noto Serif CJK KR','Noto Serif CJK SC', serif", fontWeight: 900, fontSize: 134, lineHeight: "170px", textAlign: "center", boxShadow: "0 12px 30px rgba(0,0,0,.6)" }}>
          {h}
        </div>
      ))}
    </div>
    <div style={{ position: "absolute", left: 52, bottom: 46 }}>
      <div style={{ ...big(84, "#fff", "#000", 7) }}>THE LAKE THAT</div>
      <div style={{ ...big(118, C.yellow, "#000", 8), marginTop: -2 }}>DEFEATED</div>
      <div style={{ ...big(84, "#fff", "#000", 7), marginTop: -2 }}>THE INVADERS</div>
    </div>
    <div style={{ position: "absolute", right: 50, bottom: 56 }}>
      <Tag text="KOREAN WAR · 1951" bg={C.red} fg="#fff" size={40} />
    </div>
  </AbsoluteFill>
);


/** EP02 다부동 — A안: 백선엽 "내가 물러서면 나를 쏴라" */
const DabuA: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/rok_paik.jpg`)} style={{ position: "absolute", left: -140, top: -40, height: 800, filter: "contrast(1.1) saturate(1.05)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 28%, rgba(8,8,10,.9) 55%, #08080a 100%)" }} />
    <div style={{ position: "absolute", right: 46, top: 50, textAlign: "right" }}>
      <Tag text={en ? "DABU-DONG · AUG 1950" : "1950 다부동 전투"} />
      {en ? (
        <>
          <div style={{ ...big(112, "#fff", "#000", 8), marginTop: 24 }}>"IF I RETREAT,</div>
          <div style={{ ...big(176, C.red, "#fff", 10), marginTop: -4 }}>SHOOT</div>
          <div style={{ ...big(112, C.yellow, "#000", 8), marginTop: -4 }}>ME."</div>
        </>
      ) : (
        <>
          <div style={{ ...big(104, "#fff"), marginTop: 26 }}>"내가 물러서면</div>
          <div style={{ ...big(170, C.red, "#fff", 12), marginTop: 6 }}>나를 쏴라"</div>
          <div style={{ ...big(76, C.yellow), marginTop: 18 }}>대구까지 남은 20km</div>
        </>
      )}
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
  </AbsoluteFill>
);

/** EP02 다부동 — B안: 볼링장 전차전 */
const DabuB: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/us_tank.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 30%", filter: "contrast(1.15) brightness(1.25) saturate(1.1)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 35%, rgba(0,0,0,.85) 100%)" }} />
    <div style={{ position: "absolute", left: 52, top: 46 }}>
      <Tag text={en ? "KOREAN WAR · 1950" : "6·25 낙동강 최후 방어선"} bg={C.red} fg="#fff" />
    </div>
    <div style={{ position: "absolute", left: 52, bottom: 48 }}>
      {en ? (
        <>
          <div style={{ ...big(84, "#fff", "#000", 7) }}>NIGHT TANK BATTLE IN</div>
          <div style={{ ...big(124, C.yellow, "#000", 9), marginTop: -2 }}>"THE BOWLING ALLEY"</div>
        </>
      ) : (
        <>
          <div style={{ ...big(84, "#fff") }}>계곡이 함정이 된 밤</div>
          <div style={{ ...big(156, C.yellow), marginTop: 6 }}>'볼링장' 전차전</div>
        </>
      )}
    </div>
  </AbsoluteFill>
);

/** EP03 백마고지 — A안: 숫자 "주인이 24번 바뀐 고지" */
const BaengmaA: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => {
  const a = ep.replace(/_en$/, "");
  return (
    <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
      <Img src={staticFile(`ep/${a}/ai/human_wave.jpg`)} style={{ position: "absolute", left: -170, top: -40, height: 800, filter: "contrast(1.1) brightness(1.3) saturate(1.1)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 26%, rgba(8,8,10,.9) 54%, #08080a 100%)" }} />
      <div style={{ position: "absolute", right: 46, top: 46, textAlign: "right" }}>
        <Tag text={en ? "WHITE HORSE HILL · 1952" : "1952 백마고지 전투"} />
        {en ? (
          <>
            <div style={{ ...big(92, "#fff", "#000", 7), marginTop: 22 }}>ONE HILL CHANGED</div>
            <div style={{ ...big(92, "#fff", "#000", 7), marginTop: 0 }}>HANDS</div>
            <div style={{ ...big(200, C.red, "#fff", 10), marginTop: -8 }}>24 TIMES</div>
          </>
        ) : (
          <>
            <div style={{ ...big(96, "#fff"), marginTop: 22 }}>고지의 주인이</div>
            <div style={{ ...big(230, C.red, "#fff", 12), marginTop: -6 }}>24번</div>
            <div style={{ ...big(96, C.yellow), marginTop: -6 }}>바뀌었다</div>
          </>
        )}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
    </AbsoluteFill>
  );
};

/** EP03 백마고지 — B안: 미스터리 "白馬 — 28만 발이 산을 흰 말로" */
const BaengmaB: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => {
  const a = ep.replace(/_en$/, "");
  return (
    <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
      <Img src={staticFile(`ep/${a}/ai/hill_dawn.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 40%", filter: "contrast(1.1) brightness(1.15)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.25) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,.88) 100%)" }} />
      <div style={{ position: "absolute", left: 52, top: 48, display: "flex", gap: 14 }}>
        {["白", "馬"].map((h, i) => (
          <div key={h} style={{ width: 180, height: 180, background: i === 1 ? C.red : "#f3f1ea", color: i === 1 ? "#fff" : "#111", fontFamily: "'Noto Serif CJK KR','Noto Serif CJK SC', serif", fontWeight: 900, fontSize: 140, lineHeight: "180px", textAlign: "center", boxShadow: "0 12px 30px rgba(0,0,0,.6)" }}>
            {h}
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", right: 46, top: 60 }}>
        <Tag text={en ? "KOREAN WAR · OCT 1952" : "6·25 철원 395고지"} bg={C.red} fg="#fff" size={40} />
      </div>
      <div style={{ position: "absolute", left: 52, bottom: 46 }}>
        {en ? (
          <>
            <div style={{ ...big(120, C.yellow, "#000", 8) }}>280,000 SHELLS</div>
            <div style={{ ...big(78, "#fff", "#000", 7), marginTop: 0 }}>TURNED A HILL INTO A WHITE HORSE</div>
          </>
        ) : (
          <>
            <div style={{ ...big(82, "#fff") }}>포탄 28만 발이</div>
            <div style={{ ...big(116, C.yellow), marginTop: 6 }}>산을 흰 말로 만들었다</div>
          </>
        )}
      </div>
    </AbsoluteFill>
  );
};

/** '격전의 지도' CTR 규칙 썸네일 (EP04~): 실사풍 전용 그림 + 한글 5~7자 1~2줄, 좌측 상단, 우측 하단 비움 */
const ctrText = (size: number, color: string): React.CSSProperties => ({
  fontFamily: "'Black Han Sans', sans-serif",
  fontSize: size,
  lineHeight: 1.0,
  color,
  WebkitTextStroke: "18px #000",
  paintOrder: "stroke fill",
  textShadow: "0 10px 30px rgba(0,0,0,.75)",
  whiteSpace: "nowrap",
  letterSpacing: -2,
});
const CtrThumb: React.FC<{ img: string; lines: [string, string?]; pos?: string; en?: boolean; right?: boolean }> = ({ img, lines, pos = "50% 40%", en, right }) => (
  <AbsoluteFill style={{ background: "#05070c", overflow: "hidden" }}>
    <Img src={staticFile(img)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos, filter: "contrast(1.18) saturate(1.3) brightness(1.08)" }} />
    {/* 좌상단 글자 가독성 + 우하단(재생시간 박스) 쪽은 어둡게 */}
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at ${right ? "82%" : "18%"} 18%, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 45%), linear-gradient(315deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 30%)` }} />
    <div style={{ position: "absolute", ...(right ? { right: 44, textAlign: "right" as const } : { left: 44 }), top: 34 }}>
      <div style={{ ...ctrText(en ? 150 : 178, C.yellow), ...(en ? { fontFamily: "'Oswald', sans-serif", WebkitTextStroke: "14px #000", letterSpacing: 0 } : {}) }}>{lines[0]}</div>
      {lines[1] && <div style={{ ...ctrText(en ? 150 : 178, "#fff"), marginTop: 6, ...(en ? { fontFamily: "'Oswald', sans-serif", WebkitTextStroke: "14px #000", letterSpacing: 0 } : {}) }}>{lines[1]}</div>}
    </div>
  </AbsoluteFill>
);

/* ===== '격전의 지도' 레퍼런스 디자인 시스템 (3단 텍스트 계층) — 한국어판 A안 ===== */
type Seg = [string, "w" | "s" | "r"];
const SEG_COLOR = { w: "#ffffff", s: "#8fd6ff", r: "#ff2a2a" };
/** 좌우 분할 레이아웃: 오른쪽 = 선명한 그림(인물 얼굴 가리지 않음), 왼쪽 = 같은 그림을 흐리게 어둡게 깐 연기 패널 위에 글자 */
type SplitDef = { imgX: string; midSize: number; keys: { text: string; style: "stone" | "yellow"; size: number }[] };
type RefDef = { ep: string; mid: Seg[][]; key: string; keyStyle: "red" | "stone" | "yellow" | "ice"; pos?: string; keySize?: number; split?: SplitDef };
/** 영문판(EN) — 압축 영문 공식: 'Battle of' 제외, 지명 + 숫자/핵심 단어만, Bebas Neue */
const REF_EN: Record<string, RefDef> = {
  yongmunsan: { ep: "01", mid: [[["1 REGIMENT", "s"], [" DESTROYED", "w"]], [["3 DIVISIONS", "r"]]], key: "YONGMUNSAN", keyStyle: "yellow" },
  dabudong: { ep: "02", mid: [[["STAND OR DIE:", "r"]], [["55 DAYS OF HELL", "s"]]], key: "TABU-DONG", keyStyle: "stone" },
  baengma: { ep: "03", mid: [[["LOST AND RETAKEN", "w"]], [["24 TIMES", "r"]]], key: "WHITE HORSE", keyStyle: "stone" },
  jipyeong: { ep: "04", mid: [[["360° SURROUNDED", "r"]], [["BY ", "w"], ["4 DIVISIONS", "s"]]], key: "CHIPYONG-NI", keyStyle: "yellow" },
  chuncheon: { ep: "05", mid: [[["THE ONLY VICTORY", "w"]], [["ON DAY 1", "r"]]], key: "CHUNCHEON", keyStyle: "yellow" },
  jangjin: { ep: "06", mid: [[["-40°F FREEZE:", "s"]], [["BREAKING ", "w"], ["120,000 ENEMY", "r"]]], key: "CHOSIN RESERVOIR", keyStyle: "ice" },
  betty: { ep: "07", mid: [[["34 MEN", "r"], [" VS", "w"]], [["A BATTALION", "s"]]], key: "OUTPOST BETTY", keyStyle: "stone" },
  yeongcheon: { ep: "08", mid: [[["THE LAST LINE:", "r"]], [["SAVING THE", "w"]], [["PUSAN PERIMETER", "s"]]], key: "BATTLE OF YEONGCHEON", keyStyle: "stone",
    split: { imgX: "22%", midSize: 78, keys: [{ text: "BATTLE OF", style: "stone", size: 100 }, { text: "YEONGCHEON", style: "yellow", size: 160 }] } },
  bloodyridge: { ep: "09", mid: [[["THE MEATGRINDER:", "r"]], [["3 WEEKS OF HELL", "s"]]], key: "BLOODY RIDGE", keyStyle: "stone",
    split: { imgX: "22%", midSize: 78, keys: [{ text: "BATTLE OF", style: "stone", size: 100 }, { text: "BLOODY RIDGE", style: "yellow", size: 136 }] } },
};
const REF: Record<string, RefDef> = {
  yongmunsan: { ep: "01", mid: [[["중공군 ", "w"], ["3개 사단", "r"], [" 격멸,", "w"]], [["1개 연대의 기적", "s"]]], key: "용문산 전투", keyStyle: "yellow" },
  dabudong: { ep: "02", mid: [[["대구 함락 직전", "r"], [",", "w"]], [["55일간의 결사항전", "s"]]], key: "다부동 전투", keyStyle: "stone" },
  baengma: { ep: "03", mid: [[["주인이 ", "w"], ["24번", "r"], [" 바뀐", "w"]], [["지옥의 능선", "s"]]], key: "백마고지", keyStyle: "stone" },
  jipyeong: { ep: "04", mid: [[["중공군 4개 사단", "r"], [" 완전 포위,", "w"]], [["퇴로는 없다", "s"]]], key: "지평리 전투", keyStyle: "yellow" },
  chuncheon: { ep: "05", mid: [[["개전 첫날 유일한 승리", "r"], [",", "w"]], [["3일간의 기적", "s"]]], key: "춘천 전투", keyStyle: "yellow" },
  jangjin: { ep: "06", mid: [[["영하 40도", "s"], [" 고립,", "w"]], [["12만 포위망", "r"], ["을 찢다", "w"]]], key: "장진호 전투", keyStyle: "stone" },
  betty: { ep: "07", mid: [[["소대원 ", "w"], ["34명", "r"], [" vs ", "w"], ["중공군 대대", "r"]], [["휴전 12일 전의 혈전", "s"]]], key: "베티고지 전투", keyStyle: "yellow" },
  yeongcheon: { ep: "08", mid: [[["영천이 ", "w"], ["뚫리면", "r"], [",", "w"]], [["부산이 ", "s"], ["끝장난다", "r"]]], key: "영천 대역전", keyStyle: "yellow",
    split: { imgX: "22%", midSize: 72, keys: [{ text: "영천", style: "stone", size: 128 }, { text: "대역전", style: "yellow", size: 205 }] } },
  bloodyridge: { ep: "09", mid: [[["능선이 피로 물든,", "r"]], [["3주간의 고지 지옥", "s"]]], key: "피의 능선", keyStyle: "yellow",
    split: { imgX: "22%", midSize: 72, keys: [{ text: "피의", style: "stone", size: 128 }, { text: "능선", style: "yellow", size: 205 }] } },
};
const CrackDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <defs>
      {/* 갈라진 돌 질감: 거친 노이즈로 글자 면을 부분적으로 깎아 균열·얼룩을 만든다 */}
      <filter id="crack" x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
        {/* 가는 균열선: turbulence 값이 0에 가까운 주름만 투명하게 */}
        <feTurbulence type="turbulence" baseFrequency="0.018 0.03" numOctaves={2} seed={7} result="t" />
        <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  14 0 0 0 -0.35" result="veins" />
        {/* 잔 점박이 마모 */}
        <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={3} result="g" />
        <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  9 0 0 0 -2.2" result="speck" />
        <feComposite in="veins" in2="speck" operator="in" result="mask" />
        <feComposite in="SourceGraphic" in2="mask" operator="in" result="cut" />
        {/* 돌 표면 얼룩 */}
        <feTurbulence type="fractalNoise" baseFrequency="0.12" numOctaves={3} seed={11} result="shade" />
        <feColorMatrix in="shade" type="matrix" values="0.3 0 0 0 0.7  0.3 0 0 0 0.7  0.3 0 0 0 0.7  0 0 0 0 1" result="shadeC" />
        <feBlend in="cut" in2="shadeC" mode="multiply" result="sh" />
        <feComposite in="sh" in2="cut" operator="in" />
      </filter>
    </defs>
  </svg>
);
const KeyWord: React.FC<{ text: string; style: "red" | "stone" | "yellow" | "ice"; size: number; en?: boolean; soft?: boolean }> = ({ text, style, size, en, soft }) => {
  const base: React.CSSProperties = { fontFamily: en ? "'Bebas Neue', 'Oswald', sans-serif" : "'Black Han Sans', sans-serif", fontSize: size, lineHeight: 1, whiteSpace: "nowrap", letterSpacing: en ? 1 : -3 };
  const parts = style === "yellow" ? (en ? text.replace("-", " -").split(" ") : text.split(" ")) : [text];
  const fill = (i: number) => (style === "red" ? "#e3161d" : style === "stone" ? "#ffffff" : style === "ice" ? "#cdeeff" : i === 0 ? "#ffd000" : "#ffffff");
  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      {/* 1층: 두꺼운 검은 외곽선 + 그림자 (균열 사이로 비치는 바탕) */}
      <div style={{ ...base, color: "#0a0a0a", WebkitTextStroke: "22px #000", paintOrder: "stroke fill", textShadow: "0 12px 34px rgba(0,0,0,.9), 0 0 3px #000" }}>
        {parts.map((p, i) => (
          <span key={i}>{i && !p.startsWith("-") ? " " : ""}{p}</span>
        ))}
      </div>
      {/* (soft) 균열 틈을 검정 대신 흐린 같은 색으로 채워 가독성 유지 */}
      {soft && (
        <div style={{ ...base, position: "absolute", left: 0, top: 0, opacity: 0.62 }}>
          {parts.map((p, i) => (
            <span key={i} style={{ color: fill(i) }}>{i && !p.startsWith("-") ? " " : ""}{p}</span>
          ))}
        </div>
      )}
      {/* 2층: 색 면 + 크랙/스톤 질감 */}
      <div style={{ ...base, position: "absolute", left: 0, top: 0, filter: "url(#crack)" }}>
        {parts.map((p, i) => (
          <span key={i} style={{ color: fill(i) }}>{i && !p.startsWith("-") ? " " : ""}{p}</span>
        ))}
      </div>
    </div>
  );
};
const RefThumb: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => {
  const a = ep.replace(/_en$/, "");
  const d = (en ? REF_EN : REF)[a];
  const keySize = d.keySize || (en ? Math.min(230, Math.floor(900 / (d.key.length * 0.46))) : d.key.length <= 4 ? 200 : 168);
  const head = en ? "'Bebas Neue', 'Oswald', sans-serif" : "'Black Han Sans', sans-serif";
  return (
    <AbsoluteFill style={{ background: "#050505", overflow: "hidden" }}>
      <CrackDefs />
      <Img src={staticFile(`ep/${a}/ai/thumb_ref.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: d.pos || "50% 45%", filter: "brightness(1.2) contrast(1.2) saturate(1.2)" }} />
      {/* 순흑 제거: 포연·안개 톤으로 암부를 들어올림 (screen) */}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(120,128,140,.30) 0%, rgba(95,100,110,.22) 55%, rgba(80,84,92,.18) 100%)", mixBlendMode: "screen" }} />
      {/* 가벼운 비네트 + 글자 쪽만 살짝 어둡게 (블랙 크러시 없이) */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 45%, rgba(0,0,0,0) 45%, rgba(10,12,16,.32) 100%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(10,12,16,.42) 0%, rgba(10,12,16,.12) 45%, rgba(0,0,0,0) 70%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(315deg, rgba(10,12,16,.3) 0%, rgba(0,0,0,0) 26%)" }} />
      <div style={{ position: "absolute", left: 40, top: 30, right: 360 }}>
        {/* 상단: 회색 박스 태그 */}
        <div style={{ display: "inline-block", background: "rgba(225,225,225,.92)", color: "#111", fontFamily: head, fontSize: en ? 40 : 34, padding: "6px 18px 2px", border: "3px solid #fff", boxShadow: "0 6px 16px rgba(0,0,0,.6)", letterSpacing: 1 }}>
          {en ? `MAP OF WAR EP ${d.ep}` : `격전의 지도 EP ${d.ep}`}
        </div>
        {/* 중단: 2색 분할 위기 카피 */}
        <div style={{ marginTop: 18 }}>
          {d.mid.map((line, i) => (
            <div key={i} style={{ fontFamily: head, fontSize: en ? 84 : 66, lineHeight: en ? 1.0 : 1.12, letterSpacing: en ? 1 : 0, whiteSpace: "nowrap", WebkitTextStroke: "12px #000", paintOrder: "stroke fill", textShadow: "0 6px 18px rgba(0,0,0,.85)" }}>
              {line.map(([t, c], j) => (
                <span key={j} style={{ color: SEG_COLOR[c] }}>{t}</span>
              ))}
            </div>
          ))}
        </div>
      </div>
      {/* 하단: 초대형 메인 키워드 (좌측, 우하단 25% 비움) */}
      <div style={{ position: "absolute", left: 30, bottom: 34 }}>
        <KeyWord text={d.key} style={d.keyStyle} size={keySize} en={en} />
      </div>
    </AbsoluteFill>
  );
};

const SplitThumb: React.FC<{ a: string; d: RefDef; en?: boolean }> = ({ a, d, en }) => {
  const sp = d.split!;
  const src = staticFile(`ep/${a}/ai/thumb_ref.jpg`);
  const head = en ? "'Bebas Neue', 'Oswald', sans-serif" : "'Black Han Sans', sans-serif";
  const PANEL = 540; // 왼쪽 글자 패널 폭
  return (
    <AbsoluteFill style={{ background: "#1b1d22", overflow: "hidden" }}>
      <CrackDefs />
      {/* 왼쪽: 같은 그림을 크게 흐리고 어둡게 → 순흑이 아닌 포연 질감 */}
      <Img src={src} style={{ position: "absolute", left: -80, top: -60, width: 1440, height: 840, objectFit: "cover", filter: "blur(22px) brightness(.42) contrast(1.1) saturate(1.1)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 15% 85%, rgba(200,60,30,.22) 0%, rgba(0,0,0,0) 45%)" }} />
      {/* 오른쪽: 선명한 그림, 왼쪽 가장자리만 부드럽게 녹임 */}
      <div style={{ position: "absolute", left: PANEL - 120, top: 0, width: 1280 - PANEL + 120, height: 720, WebkitMaskImage: "linear-gradient(90deg, transparent 0px, #000 170px)", maskImage: "linear-gradient(90deg, transparent 0px, #000 170px)" }}>
        <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: `${sp.imgX} 50%`, filter: "brightness(1.2) contrast(1.2) saturate(1.25)" }} />
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(120,128,140,.16) 0%, rgba(80,84,92,.10) 100%)", mixBlendMode: "screen" }} />
      </div>
      {/* 왼쪽 글자 */}
      <div style={{ position: "absolute", left: 40, top: 28, width: PANEL - 30 }}>
        <div style={{ display: "inline-block", background: "rgba(225,225,225,.94)", color: "#111", fontFamily: head, fontSize: en ? 38 : 32, padding: "6px 16px 2px", border: "3px solid #fff", boxShadow: "0 6px 16px rgba(0,0,0,.6)", letterSpacing: 1 }}>
          {en ? `MAP OF WAR EP ${d.ep}` : `격전의 지도 EP ${d.ep}`}
        </div>
        <div style={{ marginTop: 14 }}>
          {d.mid.map((line, i) => (
            <div key={i} style={{ fontFamily: head, fontSize: sp.midSize, lineHeight: en ? 0.98 : 1.14, letterSpacing: en ? 1 : -1, whiteSpace: "nowrap", WebkitTextStroke: "10px #000", paintOrder: "stroke fill", textShadow: "0 6px 18px rgba(0,0,0,.85)" }}>
              {line.map(([t, c], j) => (
                <span key={j} style={{ color: SEG_COLOR[c] }}>{t}</span>
              ))}
            </div>
          ))}
        </div>
      </div>
      <div style={{ position: "absolute", left: 30, bottom: 26, display: "flex", flexDirection: "column", alignItems: "flex-start", gap: en ? 0 : 2 }}>
        {sp.keys.map((k, i) => (
          <KeyWord key={i} text={k.text} style={k.style} size={k.size} en={en} soft />
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const Thumbnail: React.FC<{ ep: string; variant: "A" | "A2" | "A3" | "B"; lang?: string }> = ({ ep, variant, lang }) => {
  setLang(lang);
  const refKey = ep.replace(/_en$/, "");
  const refD = (lang === "en" ? REF_EN : REF)[refKey];
  // ★★ 썸네일 표준 v4 (스토리텔링 꼴라주 + 3D 몬스터 타이포, 2026-11-02~): COLLAGE 표에 있는 에피소드는 한국어 A안을 이 디자인으로
  if (variant === "A" && lang !== "en" && COLLAGE[refKey]) return <CollageThumb d={COLLAGE[refKey]} />;
  // ★ 썸네일 표준 v3 ('선 넘는 지도' 스타일, 2026-11-02~): FRONT 표에 있는 에피소드는 한국어 A안을 이 디자인으로
  if (variant === "A" && lang !== "en" && FRONT[refKey]) return <FrontThumb d={FRONT[refKey]} />;
  // 공통 썸네일 표준(MAPT, 1920×1080)이 있는 에피소드는 A안을 이 표준으로
  if (variant === "A" && MAPT[refKey]) return <MapThumb a={refKey} d={MAPT[refKey]} en={lang === "en"} />;
  // EP16: 카피 시안 2·3 (같은 배경·인물, 한국어 문구만 교체)
  if ((variant === "A2" || variant === "A3") && MAPT[refKey]?.alts) {
    const d = MAPT[refKey];
    const alt = d.alts![variant === "A2" ? 0 : 1];
    if (alt) return <MapThumb a={refKey} d={{ ...d, ko: alt }} en={false} />;
  }
  if (variant === "A" && refD?.split) return <SplitThumb a={refKey} d={refD} en={lang === "en"} />;
  if (variant === "A" && (lang === "en" ? REF_EN : REF)[refKey]) return <RefThumb ep={ep} en={lang === "en"} />;
  if (ep.startsWith("jipyeong")) {
    const a = ep.replace(/_en$/, "");
    const en = lang === "en";
    return variant === "A" ? (
      <CtrThumb img={`ep/${a}/ai/thumb_a.jpg`} lines={en ? ["NO WAY", "OUT"] : ["퇴로는", "없었다"]} pos="35% 35%" en={en} right />
    ) : (
      <CtrThumb img={`ep/${a}/ai/thumb_b.jpg`} lines={en ? ["SURROUNDED", "ON ALL SIDES"] : ["사방이", "적이었다"]} en={en} />
    );
  }
  if (ep.startsWith("baengma")) return variant === "A" ? <BaengmaA ep={ep} en={lang === "en"} /> : <BaengmaB ep={ep} en={lang === "en"} />;
  if (ep.startsWith("dabudong")) return variant === "A" ? <DabuA ep={ep} en={lang === "en"} /> : <DabuB ep={ep} en={lang === "en"} />;
  if (lang === "en") return variant === "A" ? <ThumbA_EN ep={ep} /> : <ThumbB_EN ep={ep} />;
  return variant === "A" ? <ThumbA ep={ep} /> : <ThumbB ep={ep} />;
};
