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
  const toSpan = to.span / zoom;
  const span = Math.exp(Math.log(from.span) + (Math.log(toSpan) - Math.log(from.span)) * k) / drift;
  const center: LonLat = [from.center[0] + (to.center[0] - from.center[0]) * k, from.center[1] + (to.center[1] - from.center[1]) * k];

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
    <AbsoluteFill style={{ background: "#0b0f14", overflow: "hidden" }}>
      {/* 3D 틸트 원근 컨테이너: 지도를 비스듬히 눕혀 깊이감 형성 */}
      <div
        style={{
          position: "absolute",
          inset: -120, // 틸트 시 외곽 잘림 방지용 여백
          transform: "perspective(1400px) rotateX(16deg) scale(1.08)",
          transformOrigin: "50% 55%",
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
            {/* 묵직한 그림자 필터 */}
            <filter id="tacticalShadow" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="#000" floodOpacity="0.8" />
            </filter>
          </defs>

          <g transform="translate(120, 120)">
            <path d={`M-400,-400H2320V1480H-400Z ${landD}`} fill={C.sea} fillRule="evenodd" />
            <path d={foreignD} fill={C.foreign} opacity={0.88} />
            <path d={landD} fill="none" stroke="rgba(40,40,40,.4)" strokeWidth={1.5} />
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