import React, { useEffect, useMemo, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile } from "remotion";
import { geoMercator, geoPath, GeoProjection } from "d3-geo";
import { feature } from "topojson-client";
// @ts-ignore
import countries10m from "world-atlas/countries-10m.json";
import { atSec, C, clamp, easeInOut, easeOut, F, popIn, S, Timeline } from "./theme";
import { useScene, useT } from "./ui";

type LonLat = [number, number];

// 한반도 주변 국가만 사용 (성능)
const KEEP: Record<string, "korea" | "foreign"> = { "410": "korea", "408": "korea", "156": "foreign", "643": "foreign", "392": "foreign", "496": "foreign" };
const ALL = (feature(countries10m as any, (countries10m as any).objects.countries) as any).features as any[];
const KOREA = ALL.filter((f) => KEEP[String(f.id)] === "korea");
const FOREIGN = ALL.filter((f) => KEEP[String(f.id)] === "foreign");
const LAND = ALL.filter((f) => KEEP[String(f.id)]);

let WATER: any = null;
const useWater = (enabled: boolean) => {
  const [w, setW] = useState<any>(WATER);
  const [h] = useState(() => (enabled && !WATER ? delayRender("water") : null));
  useEffect(() => {
    if (!enabled || WATER) return;
    fetch(staticFile("geo/water.json"))
      .then((r) => r.json())
      .then((j) => {
        WATER = j;
        setW(j);
        if (h !== null) continueRender(h);
      })
      .catch(() => h !== null && continueRender(h));
  }, []);
  return w;
};

const resolveP = (tl: Timeline, p: string | LonLat): LonLat => (typeof p === "string" ? [tl.places[p][0], tl.places[p][1]] : p);

/** Catmull-Rom 보간된 폴리라인 */
const smooth = (pts: [number, number][], seg = 18) => {
  if (pts.length < 3) {
    const out: [number, number][] = [];
    for (let i = 0; i <= seg; i++) out.push([pts[0][0] + ((pts[1][0] - pts[0][0]) * i) / seg, pts[0][1] + ((pts[1][1] - pts[0][1]) * i) / seg]);
    return out;
  }
  const P = [pts[0], ...pts, pts[pts.length - 1]];
  const out: [number, number][] = [];
  for (let i = 1; i < P.length - 2; i++) {
    const [p0, p1, p2, p3] = [P[i - 1], P[i], P[i + 1], P[i + 2]];
    for (let j = 0; j < seg; j++) {
      const t = j / seg,
        t2 = t * t,
        t3 = t2 * t;
      const f = (a: number, b: number, c: number, d: number) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
      out.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])]);
    }
  }
  out.push(pts[pts.length - 1]);
  return out;
};

const partial = (pts: [number, number][], k: number) => {
  const L: number[] = [0];
  for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const target = L[L.length - 1] * clamp(k);
  const out: [number, number][] = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    if (L[i] <= target) out.push(pts[i]);
    else {
      const r = (target - L[i - 1]) / (L[i] - L[i - 1] || 1);
      out.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * r, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * r]);
      break;
    }
  }
  return out;
};

const d = (pts: [number, number][]) => "M" + pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join("L");

/** EP25: 카메라 경로용 Catmull-Rom (THREE.CatmullRomCurve3와 같은 균일 공식) — 값 배열 여러 개를 u(0~1)로 보간 */
const catmull = (P: number[][], u: number) => {
  const n = P.length - 1;
  const x = clamp(u) * n;
  const i = Math.min(n - 1, Math.floor(x));
  const s = x - i;
  const p0 = P[Math.max(0, i - 1)],
    p1 = P[i],
    p2 = P[i + 1],
    p3 = P[Math.min(n, i + 2)];
  const s2 = s * s,
    s3 = s2 * s;
  return p1.map((_, k) => 0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * s + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * s2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * s3));
};

/** EP25: 결정론적 의사 난수 (프레임마다 같은 값 — Math.random 금지) */
const hash = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** EP25: 전술 HUD — 조준 레티클 · 회전 나침반 눈금 · 위경도/고도 카운터. 장면 visual.hud = true 일 때만 */
const TacticalHud: React.FC<{ t: number; center: LonLat; span: number; heading: number; temp?: string }> = ({ t, center, span, heading, temp }) => {
  const c = "rgba(120,255,170,0.85)";
  const dim = "rgba(120,255,170,0.35)";
  const op = clamp(t / 0.6);
  const alt = Math.round(span * 111000 * 0.9); // 화면 폭(도) → 대략의 관측 고도(m)
  const dms = (v: number, pos: string, neg: string) => {
    const a = Math.abs(v),
      dd = Math.floor(a),
      mm = Math.floor((a - dd) * 60),
      ss = ((a - dd) * 60 - mm) * 60;
    return `${dd}°${String(mm).padStart(2, "0")}'${ss.toFixed(1).padStart(4, "0")}"${v >= 0 ? pos : neg}`;
  };
  const ticks: React.ReactNode[] = [];
  for (let deg = -60; deg <= 60; deg += 5) {
    const hd = Math.round(heading / 5) * 5 + deg;
    const x = 960 + (hd - heading) * 7;
    const norm = ((hd % 360) + 360) % 360;
    const major = norm % 30 === 0;
    const lab = norm === 0 ? "N" : norm === 90 ? "E" : norm === 180 ? "S" : norm === 270 ? "W" : String(norm).padStart(3, "0");
    ticks.push(
      <g key={deg}>
        <line x1={x} y1={58} x2={x} y2={major ? 34 : 46} stroke={major ? c : dim} strokeWidth={major ? 3 : 2} />
        {major && (
          <text x={x} y={26} textAnchor="middle" fontFamily="monospace" fontSize={20} fill={c} fontWeight={700}>
            {lab}
          </text>
        )}
      </g>
    );
  }
  const R = 70;
  const sp = (t * 40) % 360;
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0, opacity: op, pointerEvents: "none" }}>
      <defs>
        <linearGradient id="hudFade" x1="0" x2="1">
          <stop offset="0" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.25" stopColor="#fff" stopOpacity="1" />
          <stop offset="0.75" stopColor="#fff" stopOpacity="1" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <mask id="hudMask">
          <rect x={540} y={0} width={840} height={80} fill="url(#hudFade)" />
        </mask>
      </defs>
      {/* 회전 나침반 눈금 (상단 가운데) */}
      <rect x={560} y={6} width={800} height={60} fill="rgba(0,0,0,0.35)" rx={6} />
      <g mask="url(#hudMask)">{ticks}</g>
      <path d="M960,62 l-10,14 h20 Z" fill={c} />
      {/* 조준 레티클 (화면 가운데, 반투명) */}
      <g transform="translate(960,540)" opacity={0.55}>
        <circle r={R} fill="none" stroke={c} strokeWidth={2} />
        <circle r={R * 1.9} fill="none" stroke={dim} strokeWidth={1.5} strokeDasharray="3 9" transform={`rotate(${sp})`} />
        {[0, 90, 180, 270].map((a) => (
          <line key={a} x1={0} y1={-R - 8} x2={0} y2={-R - 34} stroke={c} strokeWidth={3} transform={`rotate(${a})`} />
        ))}
        <line x1={-24} y1={0} x2={-8} y2={0} stroke={c} strokeWidth={2} />
        <line x1={8} y1={0} x2={24} y2={0} stroke={c} strokeWidth={2} />
        <line x1={0} y1={-24} x2={0} y2={-8} stroke={c} strokeWidth={2} />
        <line x1={0} y1={8} x2={0} y2={24} stroke={c} strokeWidth={2} />
      </g>
      {/* 실시간 좌표·고도 카운터 (좌측 상단) */}
      <g fontFamily="monospace" fontSize={22} fill={c} fontWeight={700}>
        <rect x={20} y={48} width={330} height={104} fill="rgba(0,0,0,0.45)" stroke={dim} strokeWidth={1.5} rx={4} />
        <text x={34} y={78}>LAT {dms(center[1], "N", "S")}</text>
        <text x={34} y={108}>LON {dms(center[0], "E", "W")}</text>
        <text x={34} y={138}>ALT {String(alt).padStart(6, "0")} M · HDG {String(Math.round(((heading % 360) + 360) % 360)).padStart(3, "0")}</text>
      </g>
      {/* EP08 장진호(영문): 혹한 온도 표시 (visual.temp, 예: "-40°F") */}
      {temp && (
        <g fontFamily="monospace" fontWeight={700}>
          <rect x={20} y={162} width={330} height={58} fill="rgba(0,20,40,0.6)" stroke="rgba(140,220,255,0.7)" strokeWidth={1.5} rx={4} />
          <text x={34} y={200} fontSize={22} fill="rgba(140,220,255,0.9)">TEMP</text>
          <text x={336} y={203} fontSize={34} textAnchor="end" fill="#bfe9ff" opacity={0.75 + 0.25 * Math.sin(t * 4)}>{temp}</text>
        </g>
      )}
    </svg>
  );
};

const Pill: React.FC<{ x: number; y: number; text: string; bg: string; fg?: string; s: number; anchor?: "left" | "right" | "center"; size?: number }> = ({
  x,
  y,
  text,
  bg,
  fg = "#fff",
  s,
  anchor = "left",
  size = 34,
}) => {
  const tx = anchor === "left" ? "0%" : anchor === "right" ? "-100%" : "-50%";
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `translate(${tx}, -50%) scale(${s})`,
        transformOrigin: anchor === "left" ? "left center" : anchor === "right" ? "right center" : "center",
        background: bg,
        color: fg,
        fontFamily: F.body,
        fontWeight: 900,
        fontSize: size,
        padding: "6px 22px 7px",
        borderRadius: 8,
        border: "1.5px solid rgba(255,255,255,0.4)",
        whiteSpace: "nowrap",
        boxShadow: "0 8px 24px rgba(0,0,0,0.65), 0 2px 6px rgba(0,0,0,0.5)",
        opacity: clamp(s * 2),
      }}
    >
      {text}
    </div>
  );
};

const colorOf = (c: string) => (c === "red" ? C.red : c === "blue" ? C.blue : c === "dark" ? "#111" : c);

export const MapView: React.FC<{ tl: Timeline }> = ({ tl }) => {
  const sc = useScene();
  const t = useT();
  const v = sc.visual;
  const water = useWater(tl.hasWater);
  const from = tl.views[v.from] || tl.views.korea;
  const to = tl.views[v.to || v.from] || from;
  const zoom = v.zoom || 1;
  const moveDur = Math.min(2.6, sc.dur * 0.45);
  const k = easeInOut(t / moveDur);
  const drift = 1 + 0.035 * clamp(t / sc.dur);
  const tiltTo = v.tilt ?? 16;
  const tiltDeg = 16 + (tiltTo - 16) * easeInOut(clamp(t / 1.6));
  // 많이 기울이면 위쪽이 멀어져 빈 곳이 생기므로 살짝 더 키움 (45도 → 약 1.36)
  const tiltScale = 1.08 + Math.max(0, tiltDeg - 16) * 0.012;
  const tiltOrigin = 55 - Math.max(0, tiltDeg - 16) * 0.75; // 45도 → 원점 약 33%: 위쪽 빈 띠 방지
  const toSpan = to.span / zoom;
  let span = Math.exp(Math.log(from.span) + (Math.log(toSpan) - Math.log(from.span)) * k) / drift;
  let center: LonLat = [from.center[0] + (to.center[0] - from.center[0]) * k, from.center[1] + (to.center[1] - from.center[1]) * k];
  // EP25: v.flight = [뷰 키…] → 카메라가 Catmull-Rom 곡선(중심 경위도 + log 폭)을 따라 저공 비행. 프레임(t) 기반, flightDur 초 동안
  let heading = 0;
  if (Array.isArray(v.flight) && v.flight.length >= 2) {
    const keys: any[] = v.flight.map((kk: string) => tl.views[kk] || from);
    const ctrl = keys.map((w) => [w.center[0], w.center[1], Math.log(w.span)]);
    const fd = v.flightDur || sc.dur * 0.9;
    const u = easeInOut(clamp(t / fd));
    const q = catmull(ctrl, u);
    const q2 = catmull(ctrl, Math.min(1, u + 0.02));
    center = [q[0], q[1]];
    span = Math.exp(q[2]) / drift;
    if (Math.hypot(q2[0] - q[0], q2[1] - q[1]) > 1e-6) heading = (Math.atan2(q2[0] - q[0], q2[1] - q[1]) * 180) / Math.PI;
  } else {
    heading = (t * 6) % 360; // 정지 화면에서도 나침반이 천천히 돈다 (HUD 연출)
  }

  // 1920x1080 기준 투영
  const proj: GeoProjection = geoMercator()
    .center(center)
    .scale(1920 / ((span * Math.PI) / 180))
    .translate([960, 540]);
  const P = (ll: LonLat) => proj(ll) as [number, number];
  const clipProj = geoMercator()
    .center(center)
    .scale(1920 / ((span * Math.PI) / 180))
    .translate([960, 540])
    .clipExtent([
      [-300, -300],
      [2220, 1380],
    ]);
  const path = geoPath(clipProj);

  // 지형 래스터
  const rasters = tl.rasters
    .map((r) => {
      const [x0, y0] = P([r.west, r.north]);
      const [x1, y1] = P([r.east, r.south]);
      return { ...r, x0, y0, w: x1 - x0, h: y1 - y0 };
    })
    .filter((r) => r.w < 40000 && r.x0 < 2160 && r.x0 + r.w > -240 && r.y0 < 1320 && r.y0 + r.h > -240); // 틸트 여백까지 포함, 확대 시 넓은 래스터도 바탕으로 유지

  const landD = LAND.map((f) => path(f) || "").join(" ");
  const foreignD = FOREIGN.map((f) => path(f) || "").join(" ");
  const scaleK = 1920 / span;
  const detail = span < 4;

  const items: any[] = v.items || [];
  const html: React.ReactNode[] = [];
  const svgItems: React.ReactNode[] = [];

  items.forEach((it, i) => {
    const s0 = atSec(sc, it.at) + 0.05;
    const since = t - s0;
    if (since < 0) return;
    const col = colorOf(it.color || "blue");
    if (it.k === "arrow") {
      const dur = it.dur || 1.3;
      const kk = easeOut(since / dur);
      const pts = smooth((it.path as LonLat[]).map(P));
      const part = partial(pts, kk);
      const w = 16 * (it.width || 1);
      const tip = part[part.length - 1];
      const prev = part[Math.max(0, part.length - 3)];
      const ang = Math.atan2(tip[1] - prev[1], tip[0] - prev[0]);
      const hl = w * 2.6,
        hw = w * 1.7;
      const body = partial(pts, Math.max(0, kk - hl / (pts.reduce((a, p, j) => (j ? a + Math.hypot(p[0] - pts[j - 1][0], p[1] - pts[j - 1][1]) : 0), 0) || 1)));
      const head = `M${tip[0] + Math.cos(ang) * 4},${tip[1] + Math.sin(ang) * 4} L${tip[0] - Math.cos(ang) * hl + Math.cos(ang + Math.PI / 2) * hw},${
        tip[1] - Math.sin(ang) * hl + Math.sin(ang + Math.PI / 2) * hw
      } L${tip[0] - Math.cos(ang) * hl - Math.cos(ang + Math.PI / 2) * hw},${tip[1] - Math.sin(ang) * hl - Math.sin(ang + Math.PI / 2) * hw} Z`;
      svgItems.push(
        <g key={i} opacity={clamp(since * 6)} filter="url(#tacticalGlow)">
          <path d={d(body)} stroke="rgba(0,0,0,0.6)" strokeWidth={w + 10} fill="none" strokeLinecap="round" strokeLinejoin="round" />
          <path d={d(body)} stroke={col} strokeWidth={w} fill="none" strokeLinecap="round" strokeLinejoin="round" />
          {kk > 0.04 && <path d={head} fill={col} stroke="rgba(0,0,0,0.6)" strokeWidth={3} strokeLinejoin="round" />}
        </g>
      );
    } else if (it.k === "front") {
      const pts = smooth((it.path as LonLat[]).map(P), 10);
      const part = partial(pts, easeOut(since / 1.2));
      svgItems.push(
        <g key={i} filter="url(#tacticalShadow)">
          <path d={d(part)} stroke="rgba(255,255,255,.9)" strokeWidth={11} fill="none" strokeLinecap="round" />
          <path d={d(part)} stroke="#0a0a0a" strokeWidth={5} fill="none" strokeDasharray="18 12" />
        </g>
      );
    } else if (it.k === "line") {
      const pts = smooth((it.path as LonLat[]).map(P), 10);
      const part = partial(pts, easeOut(since / 1.0));
      svgItems.push(
        <g key={i} filter="url(#tacticalGlow)">
          {it.glow && <path d={d(part)} stroke={col} strokeOpacity={0.4 + 0.2 * Math.sin(t * 5)} strokeWidth={44} fill="none" strokeLinecap="round" />}
          <path d={d(part)} stroke="#fff" strokeWidth={20} fill="none" strokeLinecap="round" />
          <path d={d(part)} stroke={col} strokeWidth={13} fill="none" strokeLinecap="round" />
        </g>
      );
    } else if (it.k === "marker") {
      const [x, y] = P(resolveP(tl, it.p));
      const s = popIn(since / 0.35);
      const name = typeof it.p === "string" ? tl.places[it.p][2] : it.text;
      svgItems.push(
        <g key={i} transform={`translate(${x},${y}) scale(${s})`} filter="url(#tacticalShadow)">
          <circle r={14} fill={col} stroke="#fff" strokeWidth={5} />
        </g>
      );
      const right = x < 1500;
      html.push(<Pill key={"h" + i} x={x + (right ? 26 : -26)} y={y} text={it.text || name} bg="#111" s={s} anchor={right ? "left" : "right"} />);
    } else if (it.k === "unit") {
      const [x, y] = P(resolveP(tl, it.p));
      const s = popIn(since / 0.35);
      if (it.pulse) {
        for (let r = 0; r < 2; r++) {
          const ph = ((t * 0.9 + r * 0.5) % 1 + 1) % 1;
          svgItems.push(<circle key={`p${i}${r}`} cx={x} cy={y} r={20 + ph * 90} fill="none" stroke={col} strokeWidth={5} opacity={0.8 * (1 - ph)} />);
        }
      }
      svgItems.push(
        <g key={i} transform={`translate(${x},${y}) scale(${s})`} filter="url(#tacticalShadow)">
          <rect x={-22} y={-15} width={44} height={30} rx={4} fill={col} stroke="#fff" strokeWidth={4} />
          <path d="M-22,-15 L22,15 M22,-15 L-22,15" stroke="#fff" strokeWidth={3} />
        </g>
      );
      html.push(<Pill key={"h" + i} x={x} y={y - 52} text={it.text} bg={col} s={s} anchor="center" size={32} />);
    } else if (it.k === "obj") {
      // EP16 도솔산: 목표 번호 링 (Objective 1~24). takenAt(줄 번호)부터 푸른색 + 체크로 바뀜
      const [x, y] = P(resolveP(tl, it.p));
      const s = popIn(since / 0.35);
      const taken = it.takenAt != null && t >= atSec(sc, it.takenAt) + 0.05;
      const c = taken ? colorOf("blue") : colorOf(it.color || "red");
      const r = it.r || 30;
      if (!taken) {
        const ph = ((t * 0.8 + i * 0.13) % 1 + 1) % 1;
        svgItems.push(<circle key={`op${i}`} cx={x} cy={y} r={r + ph * 34} fill="none" stroke={c} strokeWidth={4} opacity={0.7 * (1 - ph)} />);
      }
      svgItems.push(
        <g key={i} transform={`translate(${x},${y}) scale(${s})`} filter="url(#tacticalShadow)">
          <circle r={r} fill="rgba(8,10,14,.78)" stroke={c} strokeWidth={6} />
          <circle r={r - 9} fill="none" stroke="rgba(255,255,255,.5)" strokeWidth={1.5} strokeDasharray="4 4" />
          <text y={r * 0.36} textAnchor="middle" fontFamily={F.head} fontSize={r * 1.05} fill="#fff" fontWeight={700}>
            {it.n}
          </text>
          {taken && <path d={`M${r * 0.45},${-r * 1.15} l${r * 0.25},${r * 0.28} l${r * 0.5},${-r * 0.55}`} stroke="#7fd4ff" strokeWidth={6} fill="none" strokeLinecap="round" />}
        </g>
      );
      if (it.text) html.push(<Pill key={"h" + i} x={x} y={y + r + 28} text={it.text} bg={taken ? colorOf("blue") : "#111"} s={s} anchor="center" size={28} />);
    } else if (it.k === "clash") {
      // EP16 도솔산: 백병전 충돌 지점 — 번쩍이는 타격 플래시 + 퍼지는 폭발 링 (반복)
      const [x, y] = P(resolveP(tl, it.p));
      const per = it.period || 1.1;
      const ph = ((since % per) + per) % per / per;
      const sz = it.size || 1;
      const flash = Math.max(0, 1 - ph * 3.2);
      svgItems.push(
        <g key={i} transform={`translate(${x},${y})`}>
          <circle r={(26 + ph * 120) * sz} fill="none" stroke="#ffb347" strokeWidth={7 * (1 - ph) + 1} opacity={0.9 * (1 - ph)} />
          <circle r={(14 + ph * 70) * sz} fill="none" stroke="#fff" strokeWidth={4} opacity={0.8 * (1 - ph)} />
          {[0, 1, 2, 3, 4, 5, 6, 7].map((j) => {
            const a = (j / 8) * Math.PI * 2 + i;
            const r1 = 18 * sz,
              r2 = (40 + 50 * flash) * sz;
            return <line key={j} x1={Math.cos(a) * r1} y1={Math.sin(a) * r1} x2={Math.cos(a) * r2} y2={Math.sin(a) * r2} stroke="#fff6d0" strokeWidth={5} opacity={flash} strokeLinecap="round" />;
          })}
          <circle r={(22 + 30 * flash) * sz} fill="#fff3c4" opacity={0.25 + 0.75 * flash} />
          <circle r={12 * sz} fill="#ff6a00" opacity={0.9} />
        </g>
      );
    } else if (it.k === "radar") {
      // EP17 금성: 전술 HUD — 포병 발사 원점 레이더 스윕 (Lottie hud_radar_sweep 대체, SVG 네이티브)
      const [x, y] = P(resolveP(tl, it.p));
      const R = 150 * (it.size || 1);
      const s = popIn(since / 0.4);
      const ang = ((since * (it.speed || 140)) % 360) * (Math.PI / 180);
      const c = colorOf(it.color || "red");
      const wedge = (a0: number, a1: number) =>
        `M0,0 L${Math.cos(a0) * R},${Math.sin(a0) * R} A${R},${R} 0 0 1 ${Math.cos(a1) * R},${Math.sin(a1) * R} Z`;
      svgItems.push(
        <g key={i} transform={`translate(${x},${y}) scale(${s})`} opacity={0.95}>
          <circle r={R} fill="rgba(10,0,0,.35)" stroke={c} strokeWidth={3} />
          <circle r={R * 0.66} fill="none" stroke={c} strokeOpacity={0.6} strokeWidth={2} strokeDasharray="6 6" />
          <circle r={R * 0.33} fill="none" stroke={c} strokeOpacity={0.6} strokeWidth={2} strokeDasharray="6 6" />
          <line x1={-R} y1={0} x2={R} y2={0} stroke={c} strokeOpacity={0.45} strokeWidth={1.5} />
          <line x1={0} y1={-R} x2={0} y2={R} stroke={c} strokeOpacity={0.45} strokeWidth={1.5} />
          {[0.5, 0.32, 0.18].map((k, j) => (
            <path key={j} d={wedge(ang - k, ang)} fill={c} opacity={0.18 + j * 0.12} />
          ))}
          <line x1={0} y1={0} x2={Math.cos(ang) * R} y2={Math.sin(ang) * R} stroke="#fff" strokeWidth={4} />
          {[0.7, 2.1, 3.6, 5.0].map((a, j) => {
            const blip = Math.max(0, 1 - (((ang - a) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2) / 2.2);
            const rr = R * (0.35 + 0.15 * j);
            return <circle key={"b" + j} cx={Math.cos(a) * rr} cy={Math.sin(a) * rr} r={9} fill="#fff" opacity={blip} />;
          })}
        </g>
      );
      if (it.text) html.push(<Pill key={"h" + i} x={x} y={y + R * s + 34} text={it.text} bg={c} s={s} anchor="center" size={30} />);
    } else if (it.k === "shock") {
      // EP17 금성: 연속 탄착 충격파 (Lottie hud_shockwave 대체) — 여러 점에서 엇갈려 반복
      const pts: LonLat[] = (it.pts || [it.p]).map((p: any) => resolveP(tl, p));
      const per = it.period || 0.9;
      const sz = it.size || 1;
      pts.forEach((pp, j) => {
        const [x, y] = P(pp);
        const ph = (((since + j * 0.37) % per) + per) % per / per;
        const fl = Math.max(0, 1 - ph * 4);
        svgItems.push(
          <g key={`${i}-${j}`} transform={`translate(${x},${y})`}>
            <circle r={(10 + ph * 95) * sz} fill="none" stroke="#ff3b1f" strokeWidth={8 * (1 - ph) + 1} opacity={0.9 * (1 - ph)} />
            <circle r={(6 + ph * 55) * sz} fill="none" stroke="#ffd27a" strokeWidth={3} opacity={0.8 * (1 - ph)} />
            <circle r={(14 + 22 * fl) * sz} fill="#fff1c0" opacity={0.15 + 0.85 * fl} />
            <circle r={7 * sz} fill="#ff5a00" opacity={0.85} />
          </g>
        );
      });
    } else if (it.k === "lock") {
      // EP17 금성: 타깃 락온 HUD (Lottie hud_target_lock 대체) — 모서리 브래킷이 조여들고 점멸
      const [x, y] = P(resolveP(tl, it.p));
      const k = easeOut(since / 0.6);
      const S0 = (it.size || 1) * (150 - 80 * k);
      const L = S0 * 0.45;
      const blink = k >= 1 ? (Math.floor(since * 4) % 2 === 0 ? 1 : 0.45) : 1;
      const c = colorOf(it.color || "#ffde00");
      const br = (sx: number, sy: number) => `M${sx * S0},${sy * (S0 - L)} L${sx * S0},${sy * S0} L${sx * (S0 - L)},${sy * S0}`;
      svgItems.push(
        <g key={i} transform={`translate(${x},${y})`} opacity={clamp(since * 5) * blink} filter="url(#tacticalShadow)">
          {[
            [-1, -1],
            [1, -1],
            [1, 1],
            [-1, 1],
          ].map(([sx, sy], j) => (
            <path key={j} d={br(sx, sy)} stroke={c} strokeWidth={8} fill="none" strokeLinecap="square" />
          ))}
          <circle r={S0 * 0.28} fill="none" stroke={c} strokeWidth={3} />
          <line x1={-S0 * 0.5} y1={0} x2={-S0 * 0.12} y2={0} stroke={c} strokeWidth={3} />
          <line x1={S0 * 0.12} y1={0} x2={S0 * 0.5} y2={0} stroke={c} strokeWidth={3} />
          <line x1={0} y1={-S0 * 0.5} x2={0} y2={-S0 * 0.12} stroke={c} strokeWidth={3} />
          <line x1={0} y1={S0 * 0.12} x2={0} y2={S0 * 0.5} stroke={c} strokeWidth={3} />
          <circle r={6} fill={c} />
        </g>
      );
      if (it.text && k >= 1) html.push(<Pill key={"h" + i} x={x} y={y - S0 - 36} text={it.text} bg="#111" s={1} anchor="center" size={30} />);
    } else if (it.k === "swarm") {
      // EP25: 파티클 스웜 — 공세 축선(path)을 따라 붉은 발광 입자 n개(기본 200)가 대열을 이뤄 진격. 결정론적(hash) 배치
      const pts = smooth((it.path as LonLat[]).map(P), 14);
      const L: number[] = [0];
      for (let j = 1; j < pts.length; j++) L.push(L[j - 1] + Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]));
      const total = L[L.length - 1] || 1;
      const at = (dist: number) => {
        let j = 1;
        while (j < L.length - 1 && L[j] < dist) j++;
        const r = (dist - L[j - 1]) / (L[j] - L[j - 1] || 1);
        const a = pts[j - 1],
          b = pts[j];
        return { x: a[0] + (b[0] - a[0]) * r, y: a[1] + (b[1] - a[1]) * r, nx: -(b[1] - a[1]), ny: b[0] - a[0] };
      };
      const n = it.n || 200;
      const head = easeOut(since / (it.dur || 2.2)); // 선두가 축선 끝까지 나아가는 비율
      const spd = (it.speed || 0.12) * total; // px/초 흐름
      const wid = 26 * (it.width || 1);
      const c = colorOf(it.color || "#ff3b30");
      const dots: React.ReactNode[] = [];
      for (let j = 0; j < n; j++) {
        const lag = hash(j) * 0.55; // 대열 뒤쪽일수록 늦게 출발
        let s = (head - lag) * total + ((since * spd + hash(j + 7) * total) % (total * 0.18));
        if (s < 0 || s > head * total) continue;
        s = Math.min(s, total - 1);
        const p = at(s);
        const nl = Math.hypot(p.nx, p.ny) || 1;
        const off = (hash(j + 13) - 0.5) * 2 * wid + Math.sin(since * 3 + j) * 3;
        const x = p.x + (p.nx / nl) * off,
          y = p.y + (p.ny / nl) * off;
        const flick = 0.6 + 0.4 * Math.sin(since * 9 + j * 1.7);
        const r = (4.5 + hash(j + 29) * 3.5) * (it.size || 1);
        dots.push(<circle key={j} cx={x} cy={y} r={r * 2.4} fill={c} opacity={0.32 * flick} />);
        dots.push(<circle key={"c" + j} cx={x} cy={y} r={r} fill={c} stroke="#2a0000" strokeWidth={1.5} opacity={0.95} />);
        dots.push(<circle key={"h" + j} cx={x - r * 0.25} cy={y - r * 0.25} r={r * 0.4} fill="#ffe2d8" opacity={0.85 * flick} />);
      }
      // 밝은 지형 위에서도 보이게 일반 합성 + 붉은 발광(그림자 필터)
      svgItems.push(
        <g key={i} filter="url(#swarmGlow)">
          {dots}
        </g>
      );
    } else if (it.k === "badge") {
      const [x, y] = P(resolveP(tl, it.p));
      const s = popIn(since / 0.35);
      const dy = it.dy || -70;
      html.push(
        <div key={"b" + i} style={{ position: "absolute", left: x, top: y + dy, transform: `translate(-50%,-50%) scale(${s})`, opacity: clamp(s * 2) }}>
          <div style={{ background: col, color: "#fff", fontFamily: F.head, fontSize: 40, padding: "8px 24px 4px", border: "3px solid #fff", boxShadow: "0 8px 25px rgba(0,0,0,0.7)", whiteSpace: "nowrap" }}>
            {it.text}
          </div>
        </div>
      );
    }
  });

  // 하천 / 호수
  let waterEls: React.ReactNode = null;
  if (water && detail) {
    const [vx0, vy1] = proj.invert!([0, 1080]) as LonLat;
    const [vx1, vy0] = proj.invert!([1920, 0]) as LonLat;
    const inView = (ring: number[][]) => ring.some((p) => p[0] > vx0 - 0.2 && p[0] < vx1 + 0.2 && p[1] > vy1 - 0.2 && p[1] < vy0 + 0.2);
    const lakeD = water.lakes
      .filter(inView)
      .map((r: number[][]) => d(r.map((p) => P(p as LonLat))) + "Z")
      .join(" ");
    const rw = clamp(scaleK / 260, 1.5, 7);
    const riverPath = (pred: (n: number) => boolean) =>
      water.rivers
        .filter((rv: any) => pred(rv.len || 50))
        .flatMap((rv: any) => rv.lines)
        .filter(inView)
        .map((l: number[][]) => d(l.map((p) => P(p as LonLat))))
        .join(" ");
    const riverD = riverPath((n) => n >= 100);
    const riverMinor = riverPath((n) => n < 100);
    waterEls = (
      <g>
        <path d={riverMinor} stroke={C.water} strokeWidth={rw * 0.55} strokeOpacity={0.8} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <path d={riverD} stroke={C.water} strokeWidth={rw * 1.4} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <path d={lakeD} fill={C.water} stroke={C.water} strokeWidth={1} />
      </g>
    );
  }

  // 120px 간격 전술 격자망(MGRS Military Grid) 생성
  const gridLines: React.ReactNode[] = [];
  for (let gx = 120; gx < 1920; gx += 240) {
    gridLines.push(<line key={`gx-${gx}`} x1={gx} y1={0} x2={gx} y2={1080} stroke="rgba(255,255,255,0.06)" strokeWidth={1} strokeDasharray="4 8" />);
  }
  for (let gy = 120; gy < 1080; gy += 240) {
    gridLines.push(<line key={`gy-${gy}`} x1={0} y1={gy} x2={1920} y2={gy} stroke="rgba(255,255,255,0.06)" strokeWidth={1} strokeDasharray="4 8" />);
  }

  return (
    // isolation: 3D 틸트 레이어를 이 루트 안에 가둔다 — 없으면 크롬 합성 단계에서 위의 자막·콜아웃을 덮는다 (EP10까지의 버그)
    <AbsoluteFill style={{ background: "#0b0f14", overflow: "hidden", isolation: "isolate", transformStyle: "flat" }}>
      {/* 3D 틸트 원근 컨테이너: 지도를 비스듬히 눕혀 깊이감 형성 */}
      <div
        style={{
          position: "absolute",
          inset: -120, // 틸트 시 외곽 잘림 방지용 여백
          // ★ 틸트 레이어를 자기 크기(2160×1320)로 자른다. 안 자르면 확대 지도에서 전국 래스터가 수만 px로 붙어
          //   크롬 합성 레이어가 한계를 넘고, 그 뒤에 그리는 자막·콜아웃·출처가 통째로 안 나온다 (EP10까지의 버그)
          overflow: "hidden",
          // EP16: v.tilt(도)로 장면별 틸트 — 시작 16도에서 1.6초 동안 서서히 기울여 칼날 능선 고저차를 부각 (기본 16도 그대로)
          transform: `perspective(1400px) rotateX(${tiltDeg}deg) scale(${tiltScale})`,
          transformOrigin: `50% ${tiltOrigin}%`,
        }}
      >
        {/* 지형 래스터 레이어 */}
        {rasters.map((r) => (
          <Img
            key={r.name}
            src={staticFile(r.file)}
            style={{ position: "absolute", left: r.x0 + 120, top: r.y0 + 120, width: r.w, height: r.h, maxWidth: "none" }}
          />
        ))}

        {/* SVG 벡터 및 전술 렌더링 */}
        <svg width={2160} height={1320} style={{ position: "absolute", left: 0, top: 0 }}>
          <defs>
            {/* 네온 발광 필터 */}
            <filter id="tacticalGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="6" floodColor="#000" floodOpacity="0.7" />
              <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#fff" floodOpacity="0.3" />
            </filter>
            {/* EP25 파티클 스웜 붉은 발광 */}
            <filter id="swarmGlow" x="-10%" y="-10%" width="120%" height="120%">
              <feDropShadow dx="0" dy="0" stdDeviation="5" floodColor="#ff2a1a" floodOpacity="0.9" />
            </filter>
            {/* 묵직한 그림자 필터 */}
            <filter id="tacticalShadow" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="#000" floodOpacity="0.8" />
            </filter>
          </defs>

          <g transform="translate(120, 120)">
            {/* demSea(EP11 인천): 확대될수록 Natural Earth 바다 마스크를 걷어 DEM 래스터의 바다·갯벌이 보이게 */}
            <path d={`M-400,-400H2320V1480H-400Z ${landD}`} fill={C.sea} fillRule="evenodd" opacity={v.demSea ? clamp((span - 0.8) / 0.8) : 1} />
            <path d={foreignD} fill={C.foreign} opacity={0.88} />
            <path d={landD} fill="none" stroke="rgba(40,40,40,.4)" strokeWidth={1.5} opacity={v.demSea ? clamp((span - 0.8) / 0.8) : 1} />
            {waterEls}
            {gridLines}
            {svgItems}
          </g>
        </svg>

        {/* HTML 텍스트/뱃지 레이어 (오프셋 보정) */}
        <div style={{ position: "absolute", left: 120, top: 120, width: 1920, height: 1080, pointerEvents: "none" }}>
          {html}
        </div>
      </div>

      {/* 시네마틱 비네팅 레이어 (가장자리 어둡게 처리하여 화면 중심 집중) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(10,14,20,0.55) 80%, rgba(5,7,10,0.92) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* EP25: 밀리터리 Tactical HUD (visual.hud = true) — 틸트 레이어 밖에 그려 화면에 고정 */}
      {v.hud && <TacticalHud t={t} center={center} span={span} heading={heading} temp={v.temp} />}

      {/* 군용 전술 HUD 모서리 표식 */}
      <div style={{ position: "absolute", top: 20, left: 24, fontFamily: F.body, fontSize: 13, color: "rgba(255,255,255,0.4)", letterSpacing: 2 }}>
        GRID: 38°N 127°E // TACTICAL MAP
      </div>

      {/* 우측 상단 지역명 */}
      <div style={{ position: "absolute", top: 16, right: 24, fontFamily: F.head, fontWeight: 700, fontSize: 22, color: "#fff", textShadow: "0 2px 8px rgba(0,0,0,0.8)" }}>
        {S("map")}
      </div>
    </AbsoluteFill>
  );
};