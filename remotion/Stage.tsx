/**
 * 화면 업그레이드 2단계 (2026-11-12 사용자 확정 · 레퍼런스 '강뉴부대' 영상 수준 디자인 통일)
 *  - stage    : 구겨진 흰 종이 무대 + 볼 캐릭터 1~3명 + 말풍선·?·!·라벨 팝업 (on 단어 타이밍)
 *  - flatmap  : 플랫 지도 (바다 청록·땅 베이지·국가 단색) + 거리 곡선 + 국기 핀
 *  - flaggrid : 국기 줄 세우기 (이름 부를 때 하나씩 강조, "?" 칸)
 *  - checklist: 노란 체크가 하나씩
 *  - reasons  : 이유 1·2·3 번호 카드 + 붉은 X로 지우기
 * 카드 3종은 어두운 석판(Slate) 배경. 캐릭터 그림은 public/chars/<나라>_<포즈>.png (없으면 SVG 볼로 대체)
 */
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { geoMercator, geoPath } from "d3-geo";
import { feature } from "topojson-client";
// @ts-ignore
import countries50m from "world-atlas/countries-50m.json";
import { atSec, C, clamp, easeInOut, easeOut, F, fitFont, NOBREAK, popIn, Timeline } from "./theme";
import { Bubble, CalloutBox, Slate, useScene, useSince, useT } from "./ui";

/* ================= 국기 (SVG) ================= */
export type FlagKind = "kr" | "us" | "cn" | "nk" | "uk" | "su" | "un" | "et" | "jp" | "?";

const star5 = (cx: number, cy: number, r: number, rot = 0, inner = 0.382) =>
  Array.from({ length: 10 }, (_, i) => {
    const a = -Math.PI / 2 + rot + (i * Math.PI) / 5;
    const rr = i % 2 ? r * inner : r;
    return `${(cx + Math.cos(a) * rr).toFixed(2)},${(cy + Math.sin(a) * rr).toFixed(2)}`;
  }).join(" ");

/** viewBox 60×40 (3:2) 공통 좌표로 그리는 국기 내용 */
const FlagBody: React.FC<{ kind: FlagKind; uid: string }> = ({ kind, uid }) => {
  switch (kind) {
    case "kr": {
      const R = 10, ang = (Math.atan2(2, 3) * 180) / Math.PI;
      const bar = R / 6, gap = bar / 2, len = R;
      const tri = (pat: number[][], cx: number, cy: number, rot: number) => (
        <g transform={`translate(${cx},${cy}) rotate(${rot})`}>
          {pat.map((seg, i) => {
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
      const d = R * 1.5 + len / 4 + R * 0.35;
      const pos = (a: number) => [30 + Math.cos((a * Math.PI) / 180) * d, 20 + Math.sin((a * Math.PI) / 180) * d];
      const S = [1], B = [0, 0];
      const [p1, p2, p3, p4] = [pos(180 + ang), pos(-ang), pos(180 - ang), pos(ang)];
      return (
        <>
          <rect width={60} height={40} fill="#fff" />
          <g transform={`translate(30,20) rotate(${ang})`}>
            <path d={`M ${-R} 0 A ${R} ${R} 0 0 1 ${R} 0 Z`} fill="#CD2E3A" />
            <path d={`M ${-R} 0 A ${R} ${R} 0 0 0 ${R} 0 Z`} fill="#0047A0" />
            <circle cx={-R / 2} cy={0} r={R / 2} fill="#0047A0" />
            <circle cx={R / 2} cy={0} r={R / 2} fill="#CD2E3A" />
          </g>
          {tri([S, S, S], p1[0], p1[1], 90 + ang)}
          {tri([B, S, B], p2[0], p2[1], 90 - ang)}
          {tri([S, B, S], p3[0], p3[1], 90 - ang)}
          {tri([B, B, B], p4[0], p4[1], 90 + ang)}
        </>
      );
    }
    case "us":
      return (
        <>
          {Array.from({ length: 13 }, (_, i) => (
            <rect key={i} y={(i * 40) / 13} width={60} height={40 / 13 + 0.05} fill={i % 2 ? "#fff" : "#B22234"} />
          ))}
          <rect width={24} height={(40 * 7) / 13} fill="#3C3B6E" />
          {Array.from({ length: 30 }, (_, i) => {
            const r = Math.floor(i / 6), c = i % 6;
            return <polygon key={i} points={star5(2.2 + c * 3.9 + (r % 2) * 1.9, 2.2 + r * 3.9, 1.05)} fill="#fff" />;
          })}
        </>
      );
    case "cn":
      return (
        <>
          <rect width={60} height={40} fill="#DE2910" />
          <polygon points={star5(10, 10, 6)} fill="#FFDE00" />
          {([[20, 4], [24, 8], [24, 14], [20, 18]] as [number, number][]).map(([x, y], i) => (
            <polygon key={i} points={star5(x, y, 2, Math.atan2(10 - y, 10 - x) + Math.PI / 2)} fill="#FFDE00" />
          ))}
        </>
      );
    case "nk":
      return (
        <>
          <rect width={60} height={40} fill="#024FA2" />
          <rect y={6.7} width={60} height={26.6} fill="#fff" />
          <rect y={8} width={60} height={24} fill="#ED1C27" />
          <circle cx={21} cy={20} r={9} fill="#fff" />
          <polygon points={star5(21, 20, 8.6)} fill="#ED1C27" />
        </>
      );
    case "uk":
      return (
        <>
          <defs>
            <clipPath id={`ukT${uid}`}>
              <path d="M30,20 h30 v20 z v20 h-30 z h-30 v-20 z v-20 h30 z" />
            </clipPath>
          </defs>
          <rect width={60} height={40} fill="#012169" />
          <path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" strokeWidth={7} />
          <path d="M0,0 L60,40 M60,0 L0,40" clipPath={`url(#ukT${uid})`} stroke="#C8102E" strokeWidth={4.5} />
          <path d="M30,0 v40 M0,20 h60" stroke="#fff" strokeWidth={12} />
          <path d="M30,0 v40 M0,20 h60" stroke="#C8102E" strokeWidth={7} />
        </>
      );
    case "su":
      return (
        <>
          <rect width={60} height={40} fill="#CC0000" />
          <polygon points={star5(9, 5, 2.2)} fill="none" stroke="#FFD700" strokeWidth={0.7} />
          <path d="M5 13 Q9 17 13 12 M6 15 L11 10" stroke="#FFD700" strokeWidth={1.6} fill="none" strokeLinecap="round" />
        </>
      );
    case "un":
      return (
        <>
          <rect width={60} height={40} fill="#4B92DB" />
          <circle cx={30} cy={19} r={9} fill="none" stroke="#fff" strokeWidth={1.2} />
          <circle cx={30} cy={19} r={5.5} fill="none" stroke="#fff" strokeWidth={0.9} />
          <path d="M21 19 h18 M30 10 v18" stroke="#fff" strokeWidth={0.9} />
          <path d="M19 22 Q21 31 30 33 Q39 31 41 22" stroke="#fff" strokeWidth={1.6} fill="none" />
        </>
      );
    case "et":
      return (
        <>
          <rect width={60} height={13.4} fill="#078930" />
          <rect y={13.3} width={60} height={13.4} fill="#FCDD09" />
          <rect y={26.6} width={60} height={13.4} fill="#DA121A" />
          <circle cx={30} cy={20} r={8} fill="#0F47AF" />
          <polygon points={star5(30, 20, 6, 0, 0.42)} fill="none" stroke="#FCDD09" strokeWidth={1} />
        </>
      );
    case "jp":
      return (
        <>
          <rect width={60} height={40} fill="#fff" />
          <circle cx={30} cy={20} r={12} fill="#BC002D" />
        </>
      );
    default:
      return (
        <>
          <rect width={60} height={40} fill="#3a3d42" />
          <text x={30} y={31} textAnchor="middle" fontSize={30} fontFamily={F.head} fill="#f4c430">?</text>
        </>
      );
  }
};

let UID = 0;
export const Flag: React.FC<{ kind: FlagKind; w: number; border?: boolean }> = ({ kind, w, border = true }) => {
  const uid = React.useMemo(() => `f${UID++}`, []);
  return (
    <svg width={w} height={(w * 2) / 3} viewBox="0 0 60 40" preserveAspectRatio="none" style={{ display: "block", boxShadow: border ? "0 4px 12px rgba(0,0,0,.45)" : undefined, outline: border ? "2px solid rgba(0,0,0,.65)" : undefined }}>
      <FlagBody kind={kind} uid={uid} />
    </svg>
  );
};

/* ================= 캐릭터 ================= */
/** 그림이 없을 때 대체: SVG 볼 캐릭터 (국기 몸통 + 흰 눈) */
export const SvgBall: React.FC<{ kind: FlagKind; size: number; pose?: string }> = ({ kind, size, pose }) => {
  const uid = React.useMemo(() => `b${UID++}`, []);
  const shock = pose === "shock";
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ overflow: "visible" }}>
      <defs>
        <clipPath id={`bc${uid}`}>
          <circle cx={50} cy={50} r={46} />
        </clipPath>
      </defs>
      <g clipPath={`url(#bc${uid})`}>
        <svg x={-14} y={4} width={128} height={92} viewBox="0 0 60 40" preserveAspectRatio="none">
          <FlagBody kind={kind} uid={uid} />
        </svg>
        <ellipse cx={42} cy={88} rx={60} ry={14} fill="rgba(0,0,0,.12)" />
      </g>
      <circle cx={50} cy={50} r={46} fill="none" stroke="#111" strokeWidth={4} />
      <ellipse cx={37} cy={42} rx={shock ? 9 : 8} ry={shock ? 12 : 9} fill="#fff" stroke="#111" strokeWidth={2.5} />
      <ellipse cx={63} cy={42} rx={shock ? 9 : 8} ry={shock ? 12 : 9} fill="#fff" stroke="#111" strokeWidth={2.5} />
      {shock && <ellipse cx={50} cy={66} rx={6} ry={7} fill="#111" />}
    </svg>
  );
};

type CharSpec = { c: string; x: number; y: number; h?: number; at?: number; flip?: boolean; until?: number };

const Character: React.FC<{ tl: Timeline; ch: CharSpec; i: number }> = ({ tl, ch, i }) => {
  const sc = useScene();
  const t = useT();
  const s0 = atSec(sc, ch.at);
  const k = (t - s0) / 0.5;
  if (k < 0) return null;
  if (ch.until !== undefined && t > atSec(sc, ch.until) + 0.3) return null;
  const out = ch.until !== undefined ? clamp((t - atSec(sc, ch.until)) / 0.3) : 0;
  const h = ch.h ?? 520;
  const e = popIn(k);
  // 살짝 흔들리는 대기 동작 (캐릭터마다 위상 다르게)
  const ph = i * 1.9;
  const sway = Math.sin(t * 2.1 + ph) * 2.2 * clamp(k);
  const bob = Math.abs(Math.sin(t * 2.1 + ph)) * -6 * clamp(k);
  const has = (tl.chars || []).includes(ch.c);
  const [country, pose] = ch.c.split("_");
  return (
    <div
      style={{
        position: "absolute",
        left: ch.x * 1920,
        top: ch.y * 1080,
        transform: `translate(-50%,-100%) translateY(${(1 - easeOut(k)) * 120 + bob}px) scale(${(0.55 + 0.45 * e) * (1 - out * 0.4)}) rotate(${sway}deg)`,
        transformOrigin: "50% 100%",
        opacity: clamp(k * 3) * (1 - out),
      }}
    >
      {/* 바닥 그림자 */}
      <div style={{ position: "absolute", left: "50%", bottom: -14, width: h * 0.62, height: h * 0.07, marginLeft: -h * 0.31, borderRadius: "50%", background: "rgba(40,30,20,.22)", filter: "blur(6px)" }} />
      {has ? (
        <Img src={staticFile(`chars/${ch.c}.png`)} style={{ height: h, display: "block", transform: ch.flip ? "scaleX(-1)" : undefined, filter: "drop-shadow(0 6px 0 rgba(0,0,0,.12))" }} />
      ) : (
        <SvgBall kind={country as FlagKind} size={h * 0.8} pose={pose} />
      )}
    </div>
  );
};

/** ? ! 기호 팝업 */
const Mark: React.FC<{ text: string; x: number; y: number; at?: number; color?: string; size?: number }> = ({ text, x, y, at, color = C.red, size = 170 }) => {
  const k = useSince(at, 0.1) / 0.3;
  const t = useT();
  if (k < 0) return null;
  const wob = Math.sin(t * 5) * 6;
  return (
    <div style={{ position: "absolute", left: x * 1920, top: y * 1080, transform: `translate(-50%,-50%) scale(${0.3 + 0.7 * popIn(k)}) rotate(${wob}deg)`, opacity: clamp(k * 3) }}>
      <div style={{ fontFamily: F.head, fontSize: size, color, lineHeight: 1, WebkitTextStroke: "10px #111", paintOrder: "stroke fill", textShadow: "0 8px 0 rgba(0,0,0,.18)" }}>{text}</div>
    </div>
  );
};

/** 종이 위 라벨 (노랑/빨강/검정 박스) */
const PaperLabel: React.FC<{ text: string; x: number; y: number; at?: number; color?: "yellow" | "red" | "dark" | "blue"; size?: number; rot?: number }> = ({ text, x, y, at, color = "yellow", size = 64, rot = -2 }) => {
  const k = useSince(at, 0.1) / 0.35;
  if (k < 0) return null;
  return (
    <div style={{ position: "absolute", left: x * 1920, top: y * 1080, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${0.5 + 0.5 * popIn(k)})`, opacity: clamp(k * 3) }}>
      <CalloutBox text={text} style={color} size={size} />
    </div>
  );
};

/** 국기 팝업 (stage 위) */
const FlagPop: React.FC<{ flag: FlagKind; x: number; y: number; at?: number; w?: number }> = ({ flag, x, y, at, w = 220 }) => {
  const k = useSince(at, 0.1) / 0.35;
  const t = useT();
  if (k < 0) return null;
  return (
    <div style={{ position: "absolute", left: x * 1920, top: y * 1080, transform: `translate(-50%,-50%) scale(${0.4 + 0.6 * popIn(k)}) rotate(${Math.sin(t * 1.7) * 2}deg)`, opacity: clamp(k * 3) }}>
      <Flag kind={flag} w={w} />
    </div>
  );
};

type Pop = { kind: "bubble" | "q" | "ex" | "label" | "flag" | "text"; text?: string; x: number; y: number; at?: number; color?: any; size?: number; flag?: FlagKind; w?: number; rot?: number };

export const Pops: React.FC<{ pops?: Pop[] }> = ({ pops }) => (
  <>
    {(pops || []).map((p, i) => {
      switch (p.kind) {
        case "bubble":
          return <Bubble key={i} text={p.text || ""} x={p.x} y={p.y} at={p.at ?? 0} />;
        case "q":
          return <Mark key={i} text="?" x={p.x} y={p.y} at={p.at} color={p.color || C.yellow} size={p.size} />;
        case "ex":
          return <Mark key={i} text="!" x={p.x} y={p.y} at={p.at} color={p.color || C.red} size={p.size} />;
        case "flag":
          return <FlagPop key={i} flag={p.flag || "?"} x={p.x} y={p.y} at={p.at} w={p.w} />;
        case "text":
          return <Mark key={i} text={p.text || ""} x={p.x} y={p.y} at={p.at} color={p.color || "#fff"} size={p.size || 90} />;
        default:
          return <PaperLabel key={i} text={p.text || ""} x={p.x} y={p.y} at={p.at} color={p.color} size={p.size} rot={p.rot} />;
      }
    })}
  </>
);

/** 종이 무대 */
export const StageV: React.FC<{ tl: Timeline }> = ({ tl }) => {
  const v = useScene().visual;
  const t = useT();
  const z = 1 + 0.025 * Math.min(1, t / 8);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${z})` }}>
        <Img src={staticFile("ui/paper.jpg")} style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
      {v.title && (
        <div style={{ position: "absolute", left: 70, top: 56, transform: "rotate(-1.5deg)" }}>
          <CalloutBox text={v.title} style="dark" size={60} />
        </div>
      )}
      {(v.chars || []).map((ch: CharSpec, i: number) => (
        <Character key={i} tl={tl} ch={ch} i={i} />
      ))}
      <Pops pops={v.pops} />
    </AbsoluteFill>
  );
};

/* ================= 플랫 지도 ================= */
const WORLD = (feature(countries50m as any, (countries50m as any).objects.countries) as any).features as any[];
const SEA = "#3f9a9c";
const LAND = "#e9dcc0";

/** 좌표는 ll([경도, 위도]) — at은 등장 시점(on 단어로 자동 변환) */
type FPin = { ll: [number, number]; text?: string; flag?: FlagKind; at?: number; side?: "below" | "above" | "left" | "right"; color?: string };

export const FlatMapV: React.FC<{ tl: Timeline }> = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const W = 1920, H = 1080;
  // 천천히 다가가는 카메라 (span → span*zoomTo)
  const zk = easeInOut(clamp(t / Math.max(3, sc.dur)));
  const span = v.span * (1 + ((v.zoomTo ?? 0.92) - 1) * zk);
  const proj = geoMercator()
    .center(v.center)
    .scale(W / ((span * Math.PI) / 180))
    .translate([W / 2, H / 2 - 40]);
  const path = geoPath(proj);
  const fill: Record<string, string> = v.fill || {};
  const P = (ll: [number, number]) => proj(ll) as [number, number];
  return (
    <AbsoluteFill style={{ background: SEA, overflow: "hidden" }}>
      {/* 바다 물결 줄무늬 */}
      <AbsoluteFill style={{ background: "repeating-linear-gradient(170deg, rgba(255,255,255,.035) 0 3px, transparent 3px 46px)" }} />
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <filter id="fmShadow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="6" stdDeviation="5" floodColor="#0b3536" floodOpacity="0.45" />
          </filter>
        </defs>
        <g filter="url(#fmShadow)">
          {WORLD.map((f, i) => {
            const d = path(f);
            if (!d) return null;
            return <path key={i} d={d} fill={fill[String(f.id)] || LAND} stroke="#7d6f57" strokeWidth={1.6} strokeLinejoin="round" />;
          })}
        </g>
        {/* 지명·바다 라벨 */}
        {(v.labels || []).map((l: any, i: number) => {
          const [x, y] = P(l.ll);
          const k = (t - atSec(sc, l.at)) / 0.4;
          const sea = l.style === "sea";
          return (
            <text key={i} x={x} y={y} textAnchor="middle" fontFamily={F.head} fontSize={l.size || (sea ? 54 : 46)} fill={sea ? "rgba(255,255,255,.75)" : "#5b4d36"} opacity={l.at === undefined ? 1 : clamp(k)} letterSpacing={sea ? 8 : 1}>
              {l.text}
            </text>
          );
        })}
        {/* 거리 곡선 */}
        {(v.routes || []).map((r: any, i: number) => {
          const a = P(r.from), b = P(r.to);
          const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
          const dx = b[0] - a[0], dy = b[1] - a[1];
          const bend = r.bend ?? 0.22;
          const cx = mx - dy * bend, cy = my + dx * bend;
          const k = clamp((t - atSec(sc, r.at)) / (r.dur ?? 1.4));
          if (k <= 0) return null;
          const len = Math.hypot(dx, dy) * 1.15;
          const col = r.color || "#D32F2F";
          // 곡선 위 점 (화살촉 위치)
          const q = easeOut(k);
          const bx = (1 - q) * (1 - q) * a[0] + 2 * (1 - q) * q * cx + q * q * b[0];
          const by = (1 - q) * (1 - q) * a[1] + 2 * (1 - q) * q * cy + q * q * b[1];
          const lk = clamp((t - atSec(sc, r.at) - (r.dur ?? 1.4) * 0.7) / 0.4);
          return (
            <g key={i}>
              <path d={`M${a[0]},${a[1]} Q${cx},${cy} ${b[0]},${b[1]}`} fill="none" stroke="rgba(0,0,0,.25)" strokeWidth={14} strokeLinecap="round" strokeDasharray={`${len * q} ${len * 2}`} transform="translate(0,5)" />
              <path d={`M${a[0]},${a[1]} Q${cx},${cy} ${b[0]},${b[1]}`} fill="none" stroke={col} strokeWidth={10} strokeLinecap="round" strokeDasharray={r.dash ? `24 18` : `${len * q} ${len * 2}`} opacity={r.dash ? clamp(k * 3) : 1} />
              <circle cx={bx} cy={by} r={13} fill={col} stroke="#fff" strokeWidth={4} />
              {r.label && lk > 0 && (
                <g transform={`translate(${(mx + cx) / 2},${(my + cy) / 2 + (r.labelDy ?? -40)}) scale(${0.6 + 0.4 * popIn(lk)})`} opacity={clamp(lk * 3)}>
                  <rect x={-r.label.length * 19 - 26} y={-44} width={r.label.length * 38 + 52} height={74} rx={10} fill="#111" stroke="#fff" strokeWidth={4} />
                  <text x={0} y={10} textAnchor="middle" fontFamily={F.head} fontSize={50} fill={C.yellow}>
                    {r.label}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>
      {/* 핀 */}
      {(v.pins || []).map((p: FPin, i: number) => {
        const [x, y] = P(p.ll);
        const k = (t - atSec(sc, p.at)) / 0.4;
        if (k < 0) return null;
        const side = p.side || "below";
        const chip = p.text ? (
          <div style={{ ...NOBREAK, whiteSpace: "nowrap", background: "#111", color: "#fff", fontFamily: F.head, fontSize: 44, padding: "6px 18px 2px", border: "3px solid #fff", borderRadius: 6, boxShadow: "0 5px 14px rgba(0,0,0,.4)" }}>{p.text}</div>
        ) : null;
        const pos: React.CSSProperties =
          side === "above" ? { bottom: 30, left: "50%", transform: "translateX(-50%)" } : side === "left" ? { right: 30, top: "50%", transform: "translateY(-50%)" } : side === "right" ? { left: 30, top: "50%", transform: "translateY(-50%)" } : { top: 26, left: "50%", transform: "translateX(-50%)" };
        return (
          <div key={i} style={{ position: "absolute", left: x, top: y, transform: `scale(${0.4 + 0.6 * popIn(k)})`, opacity: clamp(k * 3) }}>
            <div style={{ position: "absolute", left: -15, top: -15, width: 30, height: 30, borderRadius: "50%", background: p.color || C.red, border: "5px solid #fff", boxShadow: "0 3px 8px rgba(0,0,0,.5)" }} />
            {p.flag && (
              <div style={{ position: "absolute", left: -48, top: -130 }}>
                <div style={{ position: "absolute", left: 46, top: 0, width: 5, height: 118, background: "#333" }} />
                <div style={{ position: "relative", left: 50 }}>
                  <Flag kind={p.flag} w={96} />
                </div>
              </div>
            )}
            {chip && <div style={{ position: "absolute", ...pos }}>{chip}</div>}
          </div>
        );
      })}
      {v.title && (
        <div style={{ position: "absolute", left: 60, top: 50 }}>
          <CalloutBox text={v.title} style="dark" size={56} />
        </div>
      )}
      <Pops pops={v.pops} />
      <div style={{ position: "absolute", right: 24, top: 16, fontFamily: F.body, fontSize: 20, color: "rgba(255,255,255,.7)" }}>Natural Earth</div>
    </AbsoluteFill>
  );
};

/* ================= 설명 카드 3종 (석판 배경) ================= */
const CardTitle: React.FC<{ text?: string }> = ({ text }) =>
  text ? (
    <div style={{ position: "absolute", top: 70, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
      <div style={{ ...NOBREAK, whiteSpace: "pre", fontFamily: F.head, fontSize: fitFont(text, 1600, 84, 48), color: "#fff", textShadow: "0 6px 24px rgba(0,0,0,.6)", borderBottom: `6px solid ${C.yellow}`, paddingBottom: 8 }}>{text}</div>
    </div>
  ) : null;

/** 국기 줄 세우기 */
export const FlagGridV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const items: { flag: FlagKind; name: string; at?: number }[] = v.items || [];
  const n = items.length;
  const perRow = n <= 5 ? n : Math.ceil(n / 2);
  const cw = Math.min(300, 1640 / perRow - 30);
  // 지금 강조할 칸 = 가장 최근에 나타난 칸
  let cur = -1;
  items.forEach((it, i) => {
    if (t >= atSec(sc, it.at) + 0.1) cur = i;
  });
  return (
    <AbsoluteFill>
      <Slate dim={0.15} />
      <CardTitle text={v.title} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingTop: 60, paddingBottom: 120 }}>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 30, width: perRow * (cw + 30) }}>
          {items.map((it, i) => {
            const k = (t - atSec(sc, it.at) - 0.1) / 0.35;
            const on = i === cur;
            const shown = k >= 0;
            return (
              <div key={i} style={{ width: cw, display: "flex", flexDirection: "column", alignItems: "center", opacity: shown ? clamp(k * 3) * (cur > i && v.dimPast !== false ? 0.55 : 1) : 0.18, transform: `scale(${shown ? (0.6 + 0.4 * popIn(k)) * (on ? 1.08 : 1) : 0.9})` }}>
                <div style={{ padding: 8, background: on ? C.yellow : "rgba(255,255,255,.12)", borderRadius: 8, boxShadow: on ? `0 0 34px ${C.yellow}` : "none" }}>
                  {shown ? <Flag kind={it.flag} w={cw - 16} border={false} /> : <div style={{ width: cw - 16, height: ((cw - 16) * 2) / 3, border: "4px dashed rgba(255,255,255,.4)" }} />}
                </div>
                <div style={{ ...NOBREAK, whiteSpace: "nowrap", marginTop: 14, fontFamily: F.head, fontSize: fitFont(it.name, cw, 50, 28), color: on ? C.yellow : "#fff" }}>{shown ? it.name : ""}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** 노란 체크리스트 */
export const ChecklistV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const items: { text: string; at?: number; checkAt?: number; bad?: boolean }[] = v.items || [];
  return (
    <AbsoluteFill>
      <Slate dim={0.15} />
      <CardTitle text={v.title} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingTop: 90, paddingBottom: 150 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
          {items.map((it, i) => {
            const k = (t - atSec(sc, it.at) - 0.05) / 0.35;
            if (k < 0) return <div key={i} style={{ height: 104 }} />;
            const ck = it.checkAt === undefined ? -1 : (t - atSec(sc, it.checkAt)) / 0.4;
            const done = ck > 0;
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 34, opacity: clamp(k * 3), transform: `translateX(${(1 - easeOut(k)) * -60}px)` }}>
                <svg width={104} height={104} viewBox="0 0 100 100">
                  <rect x={6} y={6} width={88} height={88} rx={10} fill="rgba(0,0,0,.35)" stroke="#fff" strokeWidth={6} />
                  {done && (
                    <path
                      d={it.bad ? "M24 24 L76 76 M76 24 L24 76" : "M20 52 L42 74 L84 22"}
                      fill="none"
                      stroke={it.bad ? C.red : C.yellow}
                      strokeWidth={13}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeDasharray={160}
                      strokeDashoffset={160 * (1 - easeOut(ck))}
                    />
                  )}
                </svg>
                <div style={{ ...NOBREAK, whiteSpace: "pre", fontFamily: F.head, fontSize: fitFont(it.text, 1300, 70, 40), color: done ? (it.bad ? "#ff8a8a" : C.yellow) : "#fff", textShadow: "0 4px 14px rgba(0,0,0,.5)" }}>{it.text}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** 이유 1·2·3 번호 카드 + 붉은 X */
export const ReasonsV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const items: { text: string; sub?: string; at?: number; xAt?: number; later?: boolean }[] = v.items || []; // later = 이 장면에선 번호만 (다음 장면에서 공개)
  const n = items.length;
  const cw = Math.min(520, 1700 / n - 40);
  return (
    <AbsoluteFill>
      <Slate dim={0.15} />
      <CardTitle text={v.title} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingTop: 110, paddingBottom: 160 }}>
        <div style={{ display: "flex", gap: 40 }}>
          {items.map((it, i) => {
            const k = it.later ? -1 : (t - atSec(sc, it.at) - 0.05) / 0.4;
            const xk = it.xAt === undefined ? -1 : (t - atSec(sc, it.xAt)) / 0.45;
            const crossed = xk > 0;
            return (
              <div key={i} style={{ position: "relative", width: cw, height: 400, opacity: k < 0 ? 0.15 : clamp(k * 3), transform: `translateY(${k < 0 ? 0 : (1 - easeOut(k)) * 50}px) rotate(${(i - (n - 1) / 2) * 1.2}deg)` }}>
                <div style={{ position: "absolute", inset: 0, background: crossed ? "#2a2b2e" : "#f3efe4", borderRadius: 14, border: "6px solid #111", boxShadow: "0 14px 34px rgba(0,0,0,.55)", display: "flex", flexDirection: "column", alignItems: "center", padding: "26px 24px", filter: crossed ? "grayscale(1)" : undefined }}>
                  <div style={{ width: 110, height: 110, borderRadius: "50%", background: crossed ? "#555" : C.red, color: "#fff", fontFamily: F.head, fontSize: 76, display: "flex", alignItems: "center", justifyContent: "center", border: "6px solid #111" }}>{i + 1}</div>
                  {k >= 0 && (
                    <>
                      <div style={{ ...NOBREAK, marginTop: 30, fontFamily: F.head, fontSize: fitFont(it.text.split("\n").sort((a, b) => b.length - a.length)[0], cw - 50, 60, 34), color: crossed ? "#bbb" : "#111", textAlign: "center", lineHeight: 1.18, whiteSpace: "pre" }}>{it.text}</div>
                      {it.sub && <div style={{ ...NOBREAK, marginTop: 18, fontFamily: F.body, fontWeight: 700, fontSize: 32, color: crossed ? "#999" : "#555", textAlign: "center", whiteSpace: "pre-line" }}>{it.sub}</div>}
                    </>
                  )}
                </div>
                {crossed && (
                  <svg width={cw} height={400} style={{ position: "absolute", inset: 0 }}>
                    <path d={`M30 40 L${cw - 30} 360`} stroke={C.red} strokeWidth={26} strokeLinecap="round" strokeDasharray={900} strokeDashoffset={900 * (1 - easeOut(xk * 2))} />
                    <path d={`M${cw - 30} 40 L30 360`} stroke={C.red} strokeWidth={26} strokeLinecap="round" strokeDasharray={900} strokeDashoffset={900 * (1 - easeOut(xk * 2 - 1))} />
                  </svg>
                )}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ================= 사료 사진 라벨 ================= */
/** 좌상단 작은 출처·연도 라벨 */
export const PhotoTag: React.FC<{ text?: string }> = ({ text }) => {
  const t = useT();
  if (!text) return null;
  return (
    <div style={{ position: "absolute", left: 30, top: 26, opacity: easeOut((t - 0.2) / 0.4), background: "rgba(10,10,10,.78)", color: "#eee", fontFamily: F.body, fontWeight: 700, fontSize: 26, padding: "6px 16px", borderLeft: `6px solid ${C.yellow}` }}>{text}</div>
  );
};

/** on에 맞춰 뜨는 노랑/빨강 강조 라벨 (사진 위 x,y) */
export const PhotoMarks: React.FC<{ marks?: { text: string; x: number; y: number; at?: number; color?: "yellow" | "red"; ring?: number }[] }> = ({ marks }) => (
  <>
    {(marks || []).map((m, i) => (
      <PhotoMark key={i} {...m} />
    ))}
  </>
);

const PhotoMark: React.FC<{ text: string; x: number; y: number; at?: number; color?: "yellow" | "red"; ring?: number }> = ({ text, x, y, at, color = "yellow", ring }) => {
  const k = useSince(at, 0.05) / 0.35;
  if (k < 0) return null;
  const col = color === "red" ? C.red : C.yellow;
  return (
    <>
      {ring && (
        <div style={{ position: "absolute", left: x * 1920 - ring, top: y * 1080 - ring, width: ring * 2, height: ring * 2, borderRadius: "50%", border: `8px solid ${col}`, boxShadow: `0 0 0 3px #111, 0 0 26px ${col}`, transform: `scale(${1.4 - 0.4 * easeOut(k)})`, opacity: clamp(k * 3) }} />
      )}
      <div style={{ position: "absolute", left: x * 1920, top: y * 1080 + (ring ? ring + 24 : 0), transform: `translate(-50%,0) scale(${0.5 + 0.5 * popIn(k)})`, transformOrigin: "50% 0", opacity: clamp(k * 3) }}>
        <CalloutBox text={text} style={color} size={58} />
      </div>
    </>
  );
};
