/**
 * DocuKit — 2026-11-26 '다큐 설명 영상 스킬' 튜토리얼(포클랜드 3분 다큐) 분석에서 가져온 화면 5종
 * war-docu · map-of-war 같은 파일 (자동 동기화 안 됨 — 고치면 두 저장소에 같이 복사)
 *
 * 레퍼런스 모양을 베끼지 않고 채널 고유 디자인(노란 세로 막대 · 짙은 유리판 · 노란 윗줄)으로 만든다.
 *   1. globe   — 3D 지구본 원정 비행: 지구가 돌며 출발지→목적지 대권 항로가 그려지고 거리 숫자가 올라감
 *   2. weapon  — 무기 실루엣 도해: 잠수함·군함·항모·제트기·프로펠러기·전차·갤리선·대포·미사일 + 어뢰/미사일/화살/포탄 발사
 *   3. punch   — 초단타 반전 카드: 검은 화면 한 줄 + 노란 밑줄 (1~2초)
 *   4. 오버레이 (어느 화면에나): counter/counters 시간·숫자 카운터 판 · stamp 도장 쾅
 *   (5. 지도 아이템 ring — MapView.tsx, 구역·사거리 원)
 * 전부 frame 기반 결정론 (Date.now·setTimeout 없음)
 */
import React from "react";
import { AbsoluteFill } from "remotion";
import { geoDistance, geoGraticule10, geoInterpolate, geoOrthographic, geoPath } from "d3-geo";
import { feature } from "topojson-client";
// @ts-ignore
import countries110 from "world-atlas/countries-110m.json";
import { atSec, C, clamp, easeInOut, easeOut, F, fitFont, popIn } from "./theme";
import { useScene, useT } from "./ui";

const LAND = (feature(countries110 as any, (countries110 as any).objects.countries) as any).features as any[];
const GRAT = geoGraticule10();

const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
type LL = [number, number];

/** 숫자 표시: fmt "clock"(시간 → H:MM) · "num"(천 단위 쉼표) */
const fmtNum = (v: number, fmt?: string, digits = 0) => {
  if (fmt === "clock") {
    const h = Math.floor(v + 1e-6);
    const m = Math.floor((v - h) * 60 + 1e-6);
    return `${h}:${String(m).padStart(2, "0")}`;
  }
  const r = Math.pow(10, digits);
  return (Math.round(v * r) / r).toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
};

/** 채널 고유 라벨: 노란 세로 막대 + 고딕 이름 + 작은 설명 */
export const BarLabel: React.FC<{ title: string; sub?: string; size?: number; k?: number; style?: React.CSSProperties }> = ({ title, sub, size = 46, k = 1, style }) => (
  <div style={{ display: "flex", gap: 16, opacity: clamp(k * 2), transform: `translateX(${(1 - easeOut(k)) * -24}px)`, ...style }}>
    <div style={{ width: 8, background: C.yellow, borderRadius: 2, boxShadow: "0 0 12px rgba(244,196,48,.5)" }} />
    <div>
      <div style={{ fontFamily: "'Black Han Sans','Noto Sans KR',sans-serif", fontSize: size, color: "#fff", lineHeight: 1.05, whiteSpace: "nowrap", textShadow: "0 3px 10px rgba(0,0,0,.6)" }}>{title}</div>
      {sub && <div style={{ fontFamily: F.body, fontWeight: 700, fontSize: Math.round(size * 0.5), color: "#d9dde2", marginTop: 6, whiteSpace: "nowrap", letterSpacing: 1 }}>{sub}</div>}
    </div>
  </div>
);

/* ======================= 1. 지구본 ======================= */
/**
 * visual: {type:"globe", from:[경도,위도], to:[경도,위도](끝 시점 중심, 없으면 from),
 *   route:[[경도,위도],...] (대권 항로), at|on(항로 시작), dur(항로 그리는 초, 기본 3.5), color,
 *   pins:[{ll, text, at|on}], fill:{"<ISO 숫자>": 색} (나라 칠하기),
 *   counter:{to, from, unit, label, at|on, dur, fmt}(기본: 항로와 같이 올라감), zoom:{to:2.2, at|on, dur}}
 */
export const GlobeV: React.FC = () => {
  const sc = useScene();
  const v: any = sc.visual;
  const t = useT();
  const route: LL[] = v.route || [];
  const rAt = atSec(sc, v.at ?? 0) + 0.3;
  const rDur = v.dur || 3.5;
  const rk = route.length > 1 ? easeInOut((t - rAt) / rDur) : 0;

  // 중심 회전: from → to (항로가 그려지는 동안), 끝나면 아주 느리게 표류
  const from: LL = v.from || route[0] || [0, 20];
  const to: LL = v.to || from;
  const spinK = easeInOut((t - Math.max(0, rAt - 0.6)) / (rDur + 0.8));
  const cen: LL = [lerp(from[0], to[0], spinK) + t * 0.6, lerp(from[1], to[1], spinK)];

  const hasCounter = !!v.counter;
  const cx = hasCounter ? 760 : 960;
  const zk = v.zoom ? easeInOut((t - atSec(sc, v.zoom.at ?? 0)) / (v.zoom.dur || 1.6)) : 0;
  const R = 430 * lerp(1, v.zoom?.to || 1, zk) * (0.92 + 0.08 * easeOut(t / 1.2));
  const proj = geoOrthographic().rotate([-cen[0], -cen[1]]).translate([cx, 540]).scale(R).clipAngle(90);
  const path = geoPath(proj);

  // 항로: 구간마다 대권으로 잘게 나눠 진행률만큼 그림
  const dense: LL[] = [];
  for (let i = 0; i + 1 < route.length; i++) {
    const ip = geoInterpolate(route[i], route[i + 1]);
    for (let j = 0; j < 64; j++) dense.push(ip(j / 64) as LL);
  }
  if (route.length) dense.push(route[route.length - 1]);
  const m = Math.max(0, Math.round(rk * (dense.length - 1)));
  const drawn = dense.slice(0, m + 1);
  const head = drawn[drawn.length - 1];
  const visible = (p: LL) => geoDistance(p, cen) < Math.PI / 2 - 0.05;
  const col = v.color || C.yellow;
  const fills: Record<string, string> = v.fill || {};

  const cnt = v.counter;
  const cAt = cnt ? (cnt.at !== undefined ? atSec(sc, cnt.at) : rAt) : 0;
  const cDur = cnt?.dur || rDur;
  const ck = cnt ? easeInOut((t - cAt) / cDur) : 0;

  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 45%, #14202c 0%, #0a0f15 60%, #05070a 100%)" }}>
      {/* 별 — 결정론 배치 */}
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 90 }, (_, i) => {
          const x = (i * 733) % 1920;
          const y = (i * 389 + 97) % 1080;
          return <circle key={i} cx={x} cy={y} r={(i % 3) * 0.5 + 0.6} fill="#fff" opacity={0.15 + ((i * 7) % 10) / 40} />;
        })}
      </svg>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        <defs>
          <radialGradient id="gOcean" cx="40%" cy="35%" r="75%">
            <stop offset="0%" stopColor="#1f4257" />
            <stop offset="70%" stopColor="#10283a" />
            <stop offset="100%" stopColor="#081521" />
          </radialGradient>
          <radialGradient id="gShade" cx="38%" cy="32%" r="80%">
            <stop offset="55%" stopColor="rgba(0,0,0,0)" />
            <stop offset="100%" stopColor="rgba(0,0,0,.55)" />
          </radialGradient>
        </defs>
        {/* 대기 빛 */}
        <circle cx={cx} cy={540} r={R + 26} fill="none" stroke="rgba(120,190,230,.18)" strokeWidth={30} />
        <circle cx={cx} cy={540} r={R + 6} fill="none" stroke="rgba(150,210,240,.35)" strokeWidth={4} />
        <path d={path({ type: "Sphere" } as any) || ""} fill="url(#gOcean)" />
        <path d={path(GRAT as any) || ""} fill="none" stroke="rgba(160,200,230,.10)" strokeWidth={1} />
        {LAND.map((f, i) => (
          <path key={i} d={path(f) || ""} fill={fills[f.id] || "#b9a678"} fillOpacity={fills[f.id] ? 0.95 : 0.78} stroke="#2a2a22" strokeOpacity={0.5} strokeWidth={0.8} />
        ))}
        <path d={path({ type: "Sphere" } as any) || ""} fill="url(#gShade)" />
        {drawn.length > 1 && (
          <>
            <path d={path({ type: "LineString", coordinates: drawn } as any) || ""} fill="none" stroke="#000" strokeOpacity={0.45} strokeWidth={9} strokeLinecap="round" />
            <path d={path({ type: "LineString", coordinates: drawn } as any) || ""} fill="none" stroke={col} strokeWidth={5} strokeDasharray="14 10" strokeLinecap="round" />
          </>
        )}
        {head && rk > 0 && rk < 1 && visible(head) && (() => {
          const [hx, hy] = proj(head) as [number, number];
          return (
            <g>
              <circle cx={hx} cy={hy} r={22 + 6 * Math.sin(t * 8)} fill={col} opacity={0.25} />
              <circle cx={hx} cy={hy} r={10} fill="#fff" stroke={col} strokeWidth={4} />
            </g>
          );
        })()}
      </svg>
      {(v.pins || []).map((p: any, i: number) => {
        const k = (t - atSec(sc, p.at ?? 0)) / 0.4;
        if (k < 0 || !visible(p.ll)) return null;
        const [x, y] = proj(p.ll) as [number, number];
        const right = p.side !== "left";
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: x - 11, top: y - 11, width: 22, height: 22, borderRadius: 11, background: "#fff", border: `5px solid ${C.yellow}`, transform: `scale(${popIn(k)})`, boxShadow: "0 0 14px rgba(0,0,0,.6)" }} />
            <div style={{ position: "absolute", top: y - 24, ...(right ? { left: x + 22 } : { right: 1920 - x + 22 }), background: "rgba(10,12,16,.82)", borderLeft: `6px solid ${C.yellow}`, color: "#fff", fontFamily: F.body, fontWeight: 800, fontSize: 32, padding: "4px 14px", whiteSpace: "nowrap", opacity: clamp(k * 2) }}>{p.text}</div>
          </React.Fragment>
        );
      })}
      {cnt && t >= cAt - 0.2 && (
        <div style={{ position: "absolute", left: 1290, top: 380, width: 560 }}>
          <div style={{ borderTop: `6px solid ${C.yellow}`, background: "rgba(10,13,18,.72)", padding: "22px 34px 26px", boxShadow: "0 14px 40px rgba(0,0,0,.45)", opacity: clamp((t - cAt + 0.2) / 0.4) }}>
            {cnt.label && <div style={{ fontFamily: F.body, fontWeight: 800, fontSize: 30, color: "#cfd5dc", marginBottom: 6 }}>{cnt.label}</div>}
            <div style={{ fontFamily: "'Black Han Sans','Noto Sans KR',sans-serif", fontSize: fitFont(fmtNum(cnt.to, cnt.fmt) + " " + (cnt.unit || ""), 500, 120, 60), color: "#fff", lineHeight: 1.05, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>
              {fmtNum(lerp(cnt.from || 0, cnt.to, ck), cnt.fmt)}
              <span style={{ fontSize: "0.42em", color: C.yellow, marginLeft: 14 }}>{cnt.unit}</span>
            </div>
          </div>
        </div>
      )}
      {v.title && (
        <div style={{ position: "absolute", left: 70, top: 64 }}>
          <BarLabel title={v.title} sub={v.sub} size={52} k={t / 0.5} />
        </div>
      )}
    </AbsoluteFill>
  );
};

/* ======================= 2. 무기 실루엣 도해 ======================= */
// 실루엣은 400×120 상자, 기수(앞)는 오른쪽 · 바닥선 y≈100. 직접 그린 단순 도형(저작권 없음)
const SIL: Record<string, { d: string[]; nose: [number, number]; light?: string[] }> = {
  sub: {
    d: ["M0,60 C20,40 60,38 120,38 L330,38 C372,38 396,50 400,60 C396,70 372,82 330,82 L120,82 C60,82 20,80 0,60 Z", "M175,38 L186,8 L238,8 L246,38 Z", "M4,60 L-26,38 L-18,60 L-26,82 Z"],
    nose: [400, 64],
  },
  ship: {
    d: ["M0,72 L400,68 L378,100 L28,100 Z", "M110,72 L122,44 L196,44 L202,22 L226,22 L232,44 L262,44 L274,70 Z", "M40,72 L48,58 L84,58 L92,72 Z", "M300,70 L308,56 L344,56 L352,70 Z", "M212,22 L214,0 L218,0 L220,22 Z"],
    nose: [400, 64],
  },
  carrier: {
    d: ["M0,52 L400,48 L392,62 L8,66 Z", "M10,66 L390,62 L366,98 L44,98 Z", "M248,48 L256,18 L286,18 L290,48 Z", "M268,18 L270,2 L274,2 L276,18 Z"],
    nose: [400, 56],
  },
  jet: {
    d: ["M0,60 L70,52 L300,50 L362,54 L400,60 L362,66 L300,70 L70,68 Z", "M150,62 L250,62 L170,104 L132,104 Z", "M30,54 L4,14 L36,14 L96,54 Z", "M40,62 L16,74 L80,68 Z"],
    light: ["M280,51 C296,36 336,38 352,53 Z"],
    nose: [400, 60],
  },
  plane: {
    d: ["M24,60 C40,46 320,44 378,54 L392,60 L378,66 C320,74 40,74 24,60 Z", "M34,58 L12,22 L44,22 L80,56 Z", "M150,62 L270,62 L250,84 L170,84 Z", "M394,34 L398,34 L398,86 L394,86 Z"],
    light: ["M300,50 C312,38 340,40 350,52 Z"],
    nose: [398, 60],
  },
  tank: {
    d: ["M24,74 L376,74 L356,108 L44,108 Z", "M118,74 L138,42 L262,42 L282,74 Z", "M262,52 L400,47 L400,55 L264,60 Z"],
    light: ["M60,96 a10,10 0 1,0 0.1,0 M110,96 a10,10 0 1,0 0.1,0 M160,96 a10,10 0 1,0 0.1,0 M210,96 a10,10 0 1,0 0.1,0 M260,96 a10,10 0 1,0 0.1,0 M310,96 a10,10 0 1,0 0.1,0"],
    nose: [400, 51],
  },
  galley: {
    d: ["M0,52 Q200,104 372,58 L404,64 L384,72 Q200,118 8,66 Z", "M196,6 L200,6 L200,64 L196,64 Z", "M160,10 L240,10 L234,50 L166,50 Z", "M0,52 C-10,40 -6,26 6,22 C2,34 4,44 10,54 Z"],
    nose: [404, 66],
  },
  cannon: {
    d: ["M110,44 L400,34 L400,52 L110,64 Z", "M50,104 L190,62 L204,76 L64,114 Z"],
    light: ["M160,84 m-34,0 a34,34 0 1,0 68,0 a34,34 0 1,0 -68,0"],
    nose: [400, 43],
  },
  missile: {
    d: ["M0,54 L320,54 C360,54 390,57 400,60 C390,63 360,66 320,66 L0,66 Z", "M0,54 L-16,36 L30,54 Z", "M0,66 L-16,84 L30,66 Z"],
    nose: [400, 60],
  },
};

const Backdrop: React.FC<{ bg?: string }> = ({ bg }) => {
  if (bg === "sea")
    return (
      <AbsoluteFill style={{ background: "linear-gradient(180deg,#2b3440 0%,#3b4652 52%,#1d2833 54%,#121b24 100%)" }}>
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          {Array.from({ length: 22 }, (_, i) => (
            <line key={i} x1={(i * 377) % 1920} x2={((i * 377) % 1920) + 120 + (i % 4) * 40} y1={600 + i * 21} y2={600 + i * 21} stroke="#7d93a8" strokeOpacity={0.12} strokeWidth={2} />
          ))}
        </svg>
      </AbsoluteFill>
    );
  if (bg === "sky") return <AbsoluteFill style={{ background: "linear-gradient(180deg,#1c2430 0%,#3a4656 70%,#4b5867 100%)" }} />;
  // 기본: 설계도(청사진) — 짙은 남색 + 옅은 격자
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #13263a 0%, #0b1622 70%, #060c13 100%)" }}>
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {Array.from({ length: 33 }, (_, i) => (
          <line key={"v" + i} x1={i * 60} x2={i * 60} y1={0} y2={1080} stroke="#7fb0d8" strokeOpacity={i % 5 === 0 ? 0.1 : 0.04} />
        ))}
        {Array.from({ length: 19 }, (_, i) => (
          <line key={"h" + i} y1={i * 60} y2={i * 60} x1={0} x2={1920} stroke="#7fb0d8" strokeOpacity={i % 5 === 0 ? 0.1 : 0.04} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};

/**
 * visual: {type:"weapon", bg:"blueprint"|"sea"|"sky",
 *   units:[{kind, x, y(바닥선 중심, 0~1), w(픽셀, 기본 560), flip, label, sub, at|on, move:{to:[x,y], dur}, color}],
 *   shots:[{from:유닛 번호|[x,y], to:[x,y], n:3, gap:0.35, dur:1.6, kind:"torpedo"|"missile"|"arrow"|"shell", hit:true, arc, at|on}],
 *   count:{text:"어뢰 3발", at|on}, title, sub}
 */
export const WeaponV: React.FC = () => {
  const sc = useScene();
  const v: any = sc.visual;
  const t = useT();
  const units: any[] = v.units || [];

  const unitPose = (u: any) => {
    const k = (t - atSec(sc, u.at ?? 0)) / 0.6;
    let x = u.x * 1920,
      y = u.y * 1080;
    if (u.move) {
      const mk = easeInOut((t - atSec(sc, u.move.at ?? u.at ?? 0)) / (u.move.dur || 2.5));
      x = lerp(x, u.move.to[0] * 1920, mk);
      y = lerp(y, u.move.to[1] * 1080, mk);
    }
    const w = u.w || 560;
    const sc2 = w / 400;
    const s = SIL[u.kind] || SIL.ship;
    const flip = !!u.flip;
    const nose: [number, number] = [x + (flip ? -1 : 1) * (s.nose[0] - 200) * sc2, y + (s.nose[1] - 100) * sc2];
    // 물 위·하늘의 아주 느린 흔들림 (결정론)
    const bob = u.kind === "sub" || u.kind === "ship" || u.kind === "carrier" || u.kind === "galley" ? Math.sin(t * 1.3 + (u.x || 0) * 9) * 4 : u.kind === "jet" || u.kind === "plane" ? Math.sin(t * 2 + (u.x || 0) * 7) * 6 : 0;
    return { k, x, y: y + bob, w, sc2, s, flip, nose: [nose[0], nose[1] + bob] as [number, number] };
  };
  const poses = units.map(unitPose);

  const shotEls: React.ReactNode[] = [];
  (v.shots || []).forEach((sh: any, si: number) => {
    const s0 = atSec(sc, sh.at ?? 0);
    const n = sh.n || 1;
    const gap = sh.gap ?? 0.35;
    const dur = sh.dur || 1.6;
    const start: [number, number] = typeof sh.from === "number" ? poses[sh.from]?.nose || [960, 540] : [sh.from[0] * 1920, sh.from[1] * 1080];
    const end: [number, number] = [sh.to[0] * 1920, sh.to[1] * 1080];
    const kind = sh.kind || "torpedo";
    const arc = sh.arc ?? (kind === "arrow" || kind === "shell" ? 220 : 0);
    const posAt = (k: number): [number, number] => [lerp(start[0], end[0], k), lerp(start[1], end[1], k) - arc * 4 * k * (1 - k)];
    for (let j = 0; j < n; j++) {
      const lk = (t - s0 - j * gap) / dur;
      if (lk < 0) continue;
      const yo = (j - (n - 1) / 2) * (kind === "torpedo" ? 14 : 8);
      if (lk <= 1) {
        const k = kind === "torpedo" ? lk : easeOut(lk) * 0.15 + lk * 0.85;
        const [hx, hy] = posAt(k);
        // 꼬리: 지나온 자리 점선/연기
        const tail = Array.from({ length: 14 }, (_, q) => {
          const kk = Math.max(0, k - (q + 1) * 0.022);
          const [tx, ty] = posAt(kk);
          return <circle key={q} cx={tx} cy={ty + yo} r={kind === "missile" ? 7 - q * 0.35 : 3.4} fill={kind === "missile" ? "#d9d9d9" : "#e8eef4"} opacity={(kind === "missile" ? 0.5 : 0.85) * (1 - q / 14)} />;
        });
        const ang = Math.atan2(posAt(Math.min(1, k + 0.01))[1] - hy, posAt(Math.min(1, k + 0.01))[0] - hx) * (180 / Math.PI);
        shotEls.push(
          <g key={`${si}-${j}`}>
            {tail}
            <g transform={`translate(${hx},${hy + yo}) rotate(${ang})`}>
              {kind === "torpedo" && <rect x={-22} y={-4} width={30} height={8} rx={4} fill="#fff" />}
              {kind === "missile" && (
                <>
                  <rect x={-34} y={-5} width={40} height={10} rx={5} fill="#f2f2f2" />
                  <circle cx={-38} cy={0} r={8 + 3 * Math.sin(t * 30 + j)} fill="#ffb347" opacity={0.9} />
                </>
              )}
              {kind === "arrow" && <line x1={-34} y1={0} x2={8} y2={0} stroke="#f2e6c9" strokeWidth={3} />}
              {kind === "shell" && <circle r={7} fill="#ffe3a0" />}
            </g>
          </g>,
        );
      } else if (sh.hit !== false) {
        const hk = (lk - 1) * dur / 0.9;
        if (hk < 1) {
          shotEls.push(
            <g key={`${si}-${j}h`} transform={`translate(${end[0]},${end[1] + yo})`}>
              <circle r={14 + 90 * hk} fill="none" stroke="#ffd27a" strokeWidth={6 * (1 - hk) + 1} opacity={1 - hk} />
              <circle r={26 * (1 - hk) + 6} fill="#fff3c4" opacity={1 - hk} />
            </g>,
          );
        }
      }
    }
  });

  const cnt = v.count;
  const cntK = cnt ? (t - atSec(sc, cnt.at ?? 0)) / 0.4 : -1;

  return (
    <AbsoluteFill>
      <Backdrop bg={v.bg} />
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {poses.map((p, i) => {
          if (p.k < 0) return null;
          const u = units[i];
          const enterX = u.move ? 0 : (1 - easeOut(p.k)) * (p.flip ? 80 : -80);
          return (
            <g key={i} opacity={clamp(p.k * 2)} transform={`translate(${p.x + enterX},${p.y}) scale(${p.flip ? -p.sc2 : p.sc2},${p.sc2}) translate(-200,-100)`}>
              {p.s.d.map((d, j) => (
                <path key={j} d={d} fill={u.color || "#c9d2da"} stroke="#0b1118" strokeWidth={2 / p.sc2} />
              ))}
              {(p.s.light || []).map((d, j) => (
                <path key={"l" + j} d={d} fill="#5f7486" stroke="#0b1118" strokeWidth={1.5 / p.sc2} />
              ))}
              {u.kind === "galley" &&
                Array.from({ length: 14 }, (_, j) => {
                  const ox = 60 + j * 21;
                  const sw = Math.sin(t * 4 + j * 0.2) * 10;
                  return <line key={"o" + j} x1={ox} y1={78} x2={ox - 14 + sw} y2={112} stroke="#c9d2da" strokeWidth={3} />;
                })}
            </g>
          );
        })}
        {shotEls}
      </svg>
      {poses.map((p, i) => {
        const u = units[i];
        if (p.k < 0 || !u.label) return null;
        return (
          <div key={"lb" + i} style={{ position: "absolute", left: p.x - p.w / 2, top: p.y - 100 * p.sc2 - 130 }}>
            <BarLabel title={u.label} sub={u.sub} size={50} k={p.k} />
          </div>
        );
      })}
      {cnt && cntK >= 0 && (
        <div style={{ position: "absolute", right: 80, top: 150, transform: `scale(${0.6 + 0.4 * popIn(cntK)})`, transformOrigin: "100% 0", opacity: clamp(cntK * 3) }}>
          <div style={{ borderTop: `6px solid ${C.yellow}`, background: "rgba(10,13,18,.78)", padding: "14px 30px 18px", fontFamily: "'Black Han Sans','Noto Sans KR',sans-serif", fontSize: 76, color: "#fff", whiteSpace: "nowrap" }}>{cnt.text}</div>
        </div>
      )}
      {v.title && (
        <div style={{ position: "absolute", left: 70, top: 64 }}>
          <BarLabel title={v.title} sub={v.sub} size={52} k={t / 0.5} />
        </div>
      )}
    </AbsoluteFill>
  );
};

/* ======================= 3. 초단타 반전 카드 ======================= */
/** visual: {type:"punch", text:"틀렸습니다.", sub?, color?("yellow"|"red")} — 1~2초짜리 한 줄 반전. 한 편에 2~4번만 */
export const PunchV: React.FC = () => {
  const v: any = useScene().visual;
  const t = useT();
  const k = t / 0.35;
  const lk = easeOut((t - 0.25) / 0.45);
  const col = v.color === "red" ? C.red : C.yellow;
  const size = fitFont(v.text || "", 1600, 190, 90);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, #1a1d22 0%, #0b0c0f 75%)", justifyContent: "center", alignItems: "center" }}>
      <div style={{ textAlign: "center", transform: `scale(${1.08 - 0.08 * easeOut(k)})`, opacity: clamp(k * 1.6) }}>
        <div style={{ fontFamily: "'Black Han Sans','Noto Sans KR',sans-serif", fontSize: size, color: "#fff", whiteSpace: "nowrap", letterSpacing: -2, textShadow: "0 6px 24px rgba(0,0,0,.6)" }}>{v.text}</div>
        <div style={{ height: 12, width: `${Math.round(lk * 62)}%`, margin: "18px auto 0", background: col, borderRadius: 3, boxShadow: `0 0 18px ${col}` }} />
        {v.sub && <div style={{ fontFamily: F.body, fontWeight: 700, fontSize: 44, color: "#c9ced4", marginTop: 26, opacity: clamp((t - 0.6) / 0.4) }}>{v.sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

/* ======================= 4. 어느 화면에나 얹는 오버레이 ======================= */
/**
 * visual.counter 또는 visual.counters: [{from, to, fmt:"clock"|"num", digits, unit, label, at|on, dur}]
 *   → 오른쪽 위 짙은 유리판(노란 윗줄)에 숫자가 올라감. 사진 위 '버틴 시간 0:30 → 3:00', '병력 3,000 / 물자 1,000톤'
 *   pos: "right"(기본) | "left"
 * visual.stamp: {text:"항복", at|on, x, y(0~1, 기본 0.5/0.42), rot(-8), color:"red"|"yellow", size}
 *   → 도장이 크게 쾅 찍힘. (document 화면의 문자열 stamp와는 별개 — 객체일 때만)
 */
export const DocOverlays: React.FC = () => {
  const sc = useScene();
  const v: any = sc.visual || {};
  const t = useT();
  const list: any[] = v.counters || (v.counter && v.type !== "globe" ? [v.counter] : []);
  const st = v.stamp && typeof v.stamp === "object" ? v.stamp : null;
  if (!list.length && !st) return null;
  const left = v.counterPos === "left";
  // 오른쪽 위 모서리는 사진 출처·라벨·'재연 일러스트' 표시 자리라 그 아래(150)부터
  const top = v.counterTop ?? 150;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {list.length > 0 && (
        <div style={{ position: "absolute", top, ...(left ? { left: 60 } : { right: 60 }), display: "flex", flexDirection: "column", gap: 14, alignItems: left ? "flex-start" : "flex-end" }}>
          {list.map((c, i) => {
            const s0 = atSec(sc, c.at ?? 0);
            const k = (t - s0) / 0.35;
            if (k < 0) return null;
            const ck = easeInOut((t - s0) / (c.dur || 1.8));
            return (
              <div key={i} style={{ borderTop: `6px solid ${C.yellow}`, background: "rgba(10,13,18,.8)", padding: "12px 30px 16px", minWidth: 300, textAlign: left ? "left" : "right", opacity: clamp(k * 2), transform: `translateY(${(1 - easeOut(k)) * -16}px)`, boxShadow: "0 12px 34px rgba(0,0,0,.45)" }}>
                <div style={{ fontFamily: "'Black Han Sans','Noto Sans KR',sans-serif", fontSize: c.size || 92, color: "#fff", lineHeight: 1.04, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>
                  {fmtNum(lerp(c.from ?? 0, c.to, ck), c.fmt, c.digits || 0)}
                  {c.unit && <span style={{ fontSize: "0.42em", color: C.yellow, marginLeft: 10 }}>{c.unit}</span>}
                </div>
                {c.label && <div style={{ fontFamily: F.body, fontWeight: 800, fontSize: 28, color: "#cfd5dc", marginTop: 4, whiteSpace: "nowrap" }}>{c.label}</div>}
              </div>
            );
          })}
        </div>
      )}
      {st &&
        (() => {
          const s0 = atSec(sc, st.at ?? 0);
          const k = (t - s0) / 0.22;
          if (k < 0) return null;
          const col = st.color === "yellow" ? C.yellow : "#d8262e";
          const shake = k < 2 ? Math.sin(k * 20) * (2 - k) * 4 : 0;
          return (
            <div style={{ position: "absolute", left: (st.x ?? 0.5) * 1920, top: (st.y ?? 0.42) * 1080, transform: `translate(-50%,-50%) translate(${shake}px,0) rotate(${st.rot ?? -8}deg) scale(${k < 1 ? 2.2 - 1.2 * easeOut(k) : 1})`, opacity: clamp(k * 2) }}>
              <div style={{ border: `8px solid ${col}`, outline: `3px solid ${col}`, outlineOffset: 6, color: col, background: "rgba(10,10,10,.35)", fontFamily: "'Black Han Sans','Noto Sans KR',sans-serif", fontSize: st.size || 112, padding: "4px 40px", whiteSpace: "nowrap", letterSpacing: 4, textShadow: "0 0 2px rgba(0,0,0,.4)" }}>{st.text}</div>
            </div>
          );
        })()}
    </AbsoluteFill>
  );
};
