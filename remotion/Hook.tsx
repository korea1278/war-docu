/* =====================================================================
   초반 후킹 표준 부품 (docs/HOOK_STANDARD.md · EP29 ep29-daejeon부터 모든 신규 롱폼)
   - LeftStatHud      : 좌측 상단 반투명 다크 카드 — 큰 볼드 수치 + 2줄 설명 (장면 필드 hook.hud[])
   - NegationOverlay  : 통념 키워드 위 붉은 X 마크 (hook.neg)
   - CoreQuestionCard : 어두워진 화면 중앙 종이 질감 핵심 질문 카드 (hook.question)
   - TroopsV          : 3D 아이소메트릭 병력 미니어처 대열 (visual.type "troops")
   전부 frame 기반 결정론 (Date.now·setTimeout·Math.random 금지 — LONGFORM_STANDARD 4)
   ===================================================================== */
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { atSec, clamp, easeInOut, easeOut, F, fitFont, popIn } from "./theme";
import { useScene, useT } from "./ui";

type HudItem = { big: string; sub?: string; sub2?: string; at?: number; until?: number; color?: string; count?: boolean };
type Neg = { text: string; at?: number; xAt?: number; until?: number };
type Question = { text: string; at?: number; until?: number; kicker?: string };
export type Hook = { hud?: HudItem[]; neg?: Neg; question?: Question };

/** "3,933명" → [3933, "", "명"] — 숫자 카운트업용 */
const splitNum = (s: string): [number, string, string] | null => {
  const m = s.match(/^([^\d]*)([\d,]+(?:\.\d+)?)(.*)$/);
  if (!m) return null;
  return [parseFloat(m[2].replace(/,/g, "")), m[1], m[3]];
};
const fmt = (n: number, src: string) => {
  const dec = (src.split(".")[1] || "").replace(/[^\d]/g, "").length;
  const v = dec ? n.toFixed(dec) : Math.round(n).toString();
  return src.includes(",") ? v.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : v;
};

/* ---------------- 1) 좌측 상단 수치 HUD ---------------- */
export const LeftStatHud: React.FC = () => {
  const sc = useScene();
  const t = useT();
  const items: HudItem[] = ((sc as any).hook?.hud || []) as HudItem[];
  // 지금 보여야 할 카드 = 시작한 것 중 마지막 (순차 교체)
  let cur = -1;
  items.forEach((it, i) => {
    if (t >= atSec(sc, it.at ?? 0)) cur = i;
  });
  if (cur < 0) return null;
  const it = items[cur];
  const s0 = atSec(sc, it.at ?? 0);
  const k = t - s0;
  const endS = it.until !== undefined ? atSec(sc, it.until) : cur + 1 < items.length ? atSec(sc, items[cur + 1].at ?? 0) : sc.dur + 1;
  const outK = clamp((endS - t) / 0.25);
  const inK = easeOut(k / 0.45);
  const op = Math.min(inK, outK);
  if (op <= 0) return null;
  const color = it.color || "#FFD400";
  // 숫자면 0.9초 카운트업
  let big = it.big;
  const sp = it.count !== false ? splitNum(it.big) : null;
  if (sp) {
    const [n, pre, post] = sp;
    const num = it.big.match(/[\d,]+(?:\.\d+)?/)![0];
    big = pre + fmt(n * easeOut(k / 0.9), num) + post;
  }
  const bigSize = fitFont(it.big, 600, 132, 70);
  return (
    <div
      style={{
        position: "absolute",
        left: 64,
        top: 64,
        minWidth: 420,
        maxWidth: 680,
        padding: "26px 36px 28px 40px",
        background: "linear-gradient(135deg, rgba(8,10,12,.82), rgba(14,16,20,.72))",
        borderLeft: `10px solid ${color}`,
        boxShadow: "0 10px 40px rgba(0,0,0,.55)",
        opacity: op,
        transform: `translateX(${(1 - inK) * -60}px)`,
      }}
    >
      <div style={{ fontFamily: F.head, fontSize: bigSize, lineHeight: 1.0, color, whiteSpace: "nowrap", textShadow: "0 4px 0 rgba(0,0,0,.6)" }}>{big}</div>
      {it.sub && (
        <div style={{ marginTop: 14, fontFamily: F.sub, fontSize: 44, lineHeight: 1.15, color: "#fff", whiteSpace: "nowrap", opacity: clamp((k - 0.25) * 3) }}>{it.sub}</div>
      )}
      {it.sub2 && (
        <div style={{ marginTop: 6, fontFamily: F.sub, fontSize: 34, lineHeight: 1.15, color: "rgba(255,255,255,.72)", whiteSpace: "nowrap", opacity: clamp((k - 0.4) * 3) }}>{it.sub2}</div>
      )}
    </div>
  );
};

/* ---------------- 2) 통념 부정 X 마크 ---------------- */
export const NegationOverlay: React.FC = () => {
  const sc = useScene();
  const t = useT();
  const n: Neg | undefined = (sc as any).hook?.neg;
  if (!n) return null;
  const s0 = atSec(sc, n.at ?? 0);
  const k = t - s0;
  if (k < 0) return null;
  const endS = n.until !== undefined ? atSec(sc, n.until) : sc.dur + 1;
  const op = Math.min(easeOut(k / 0.35), clamp((endS - t) / 0.25));
  if (op <= 0) return null;
  const xs = n.xAt !== undefined ? atSec(sc, n.xAt) : s0 + 0.8;
  const xk = t - xs;
  const d1 = easeOut(xk / 0.18);
  const d2 = easeOut((xk - 0.14) / 0.18);
  const shake = xk > 0 && xk < 0.35 ? Math.sin(xk * 90) * 10 * (1 - xk / 0.35) : 0;
  const size = fitFont(n.text, 560, 150, 80);
  return (
    <div style={{ position: "absolute", left: 64, top: 64, opacity: op, transform: `translateX(${shake}px)` }}>
      <div
        style={{
          position: "relative",
          padding: "30px 48px",
          background: "rgba(8,10,12,.82)",
          borderLeft: "10px solid #fff",
          fontFamily: F.head,
          fontSize: size,
          color: xk > 0 ? "rgba(255,255,255,.55)" : "#fff",
          whiteSpace: "nowrap",
          boxShadow: "0 10px 40px rgba(0,0,0,.55)",
        }}
      >
        {n.text}
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute", inset: -18, width: "calc(100% + 36px)", height: "calc(100% + 36px)", overflow: "visible" }}>
          {d1 > 0 && <line x1={6} y1={8} x2={6 + 88 * d1} y2={8 + 84 * d1} stroke="#FF1E1E" strokeWidth={11} strokeLinecap="round" vectorEffect="non-scaling-stroke" style={{ filter: "drop-shadow(0 0 10px rgba(255,30,30,.8))" }} />}
          {d2 > 0 && <line x1={94} y1={8} x2={94 - 88 * d2} y2={8 + 84 * d2} stroke="#FF1E1E" strokeWidth={11} strokeLinecap="round" vectorEffect="non-scaling-stroke" style={{ filter: "drop-shadow(0 0 10px rgba(255,30,30,.8))" }} />}
        </svg>
      </div>
    </div>
  );
};

/* ---------------- 3) 핵심 질문 카드 ---------------- */
export const CoreQuestionCard: React.FC = () => {
  const sc = useScene();
  const t = useT();
  const q: Question | undefined = (sc as any).hook?.question;
  if (!q) return null;
  const s0 = atSec(sc, q.at ?? 0);
  const k = t - s0;
  if (k < 0) return null;
  const endS = q.until !== undefined ? atSec(sc, q.until) : sc.dur + 1;
  const outK = clamp((endS - t) / 0.3);
  const dim = Math.min(easeInOut(k / 0.5), outK);
  const pk = Math.min(popIn((k - 0.15) / 0.55), outK);
  const lines = q.text.split("\n");
  const longest = lines.reduce((a, b) => (a.length > b.length ? a : b), "");
  const size = fitFont(longest, 1240, 92, 56);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: `rgba(0,0,0,${0.62 * dim})` }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: 110 }}>
        <div
          style={{
            position: "relative",
            width: 1420,
            padding: "56px 80px 64px",
            transform: `scale(${Math.max(0, pk)}) rotate(${-1.2 * pk}deg)`,
            boxShadow: "0 30px 80px rgba(0,0,0,.7)",
            overflow: "hidden",
          }}
        >
          <Img src={staticFile("ui/paper.jpg")} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", filter: "sepia(.35) brightness(1.04)" }} />
          <div style={{ position: "absolute", inset: 14, border: "3px solid rgba(60,40,20,.45)" }} />
          <div style={{ position: "relative", textAlign: "center" }}>
            <div style={{ fontFamily: F.sub, fontSize: 40, letterSpacing: 6, color: "#b3261e", marginBottom: 18 }}>{q.kicker || "■ 오늘의 질문 ■"}</div>
            {lines.map((l, i) => (
              <div key={i} style={{ fontFamily: F.head, fontSize: size, lineHeight: 1.22, color: "#1a1410", whiteSpace: "nowrap", opacity: clamp((k - 0.35 - i * 0.25) * 3) }}>
                {l}
              </div>
            ))}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** 장면 오버레이 묶음 (Video.tsx 오버레이 레이어에서 hook 필드가 있을 때만) */
export const HookOverlays: React.FC = () => (
  <>
    <LeftStatHud />
    <NegationOverlay />
    <CoreQuestionCard />
  </>
);

/* ---------------- 4) 3D 아이소메트릭 병력 대열 (visual.type "troops") ----------------
   visual: { type:"troops", n: 31, cols: 8, side:"us"|"nk"|"kr", keep?: 1, keepAt?: 줄, fadeLabel?: "...",
             vs?: { n, side, cols } (오른쪽에 상대 대열), title?, march?: true (2열 행진), bg?: "photo src" }
   keep/keepAt: keepAt 시점부터 keep개만 남기고 나머지가 사라짐 (예: 31명 → 1명 강조) */
const SIDE: Record<string, { body: string; helm: string; glow: string }> = {
  us: { body: "#6b7a4f", helm: "#4e5a38", glow: "#7fd3ff" },
  kr: { body: "#7b8452", helm: "#5b6440", glow: "#7fd3ff" },
  nk: { body: "#7d6a45", helm: "#5e4f31", glow: "#ff4a4a" },
  cn: { body: "#7a7a55", helm: "#5c5c3d", glow: "#ff4a4a" },
};
const hash = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

const Soldier: React.FC<{ x: number; y: number; s: number; side: string; op: number; hi?: boolean; step?: number }> = ({ x, y, s, side, op, hi, step = 0 }) => {
  const c = SIDE[side] || SIDE.us;
  const lift = Math.abs(Math.sin(step)) * 3 * s;
  return (
    <g transform={`translate(${x},${y - lift}) scale(${s})`} opacity={op}>
      <ellipse cx={0} cy={0} rx={13} ry={6} fill="rgba(0,0,0,.45)" />
      {hi && <ellipse cx={0} cy={0} rx={26} ry={12} fill="none" stroke={c.glow} strokeWidth={3} style={{ filter: `drop-shadow(0 0 8px ${c.glow})` }} />}
      {/* 다리 */}
      <rect x={-7} y={-22 + Math.sin(step) * 2} width={5} height={22} rx={2} fill="#3a3a2c" />
      <rect x={2} y={-22 - Math.sin(step) * 2} width={5} height={22} rx={2} fill="#33332a" />
      {/* 몸통 (아이소메트릭 두 면) */}
      <path d="M -10 -46 L 0 -50 L 0 -20 L -10 -18 Z" fill={c.body} />
      <path d="M 0 -50 L 10 -46 L 10 -18 L 0 -20 Z" fill={c.helm} />
      {/* 총 */}
      <rect x={9} y={-58} width={3} height={36} fill="#2a2420" transform="rotate(12 10 -40)" />
      {/* 얼굴·철모 */}
      <circle cx={0} cy={-57} r={7} fill="#d9b48f" />
      <path d="M -10 -58 Q 0 -72 10 -58 Z" fill={c.helm} />
    </g>
  );
};

export const TroopsV: React.FC = () => {
  const sc = useScene();
  const t = useT();
  const v = sc.visual;
  const groups: { n: number; cols: number; side: string; ox: number }[] = [];
  const vs = v.vs;
  groups.push({ n: v.n || 31, cols: v.cols || 8, side: v.side || "us", ox: vs ? 560 : 960 });
  if (vs) groups.push({ n: vs.n, cols: vs.cols || 8, side: vs.side || "nk", ox: 1360 });
  const keepS = v.keepAt !== undefined ? atSec(sc, v.keepAt) : null;
  const kk = keepS !== null ? easeInOut((t - keepS) / 0.9) : 0;
  const cam = easeOut(t / 2.4);
  const march = !!v.march;
  return (
    <AbsoluteFill>
      {v.src ? (
        <AbsoluteFill>
          <Img src={staticFile(v.src)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(1) brightness(.35) blur(3px)" }} />
        </AbsoluteFill>
      ) : (
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 60%, #3b3d36 0%, #1b1c19 70%, #0d0d0c 100%)" }} />
      )}
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        {/* 아이소메트릭 바닥 격자 */}
        <g opacity={0.22} transform={`translate(960 ${640 - cam * 20}) scale(${1 + cam * 0.06})`}>
          {Array.from({ length: 21 }).map((_, i) => (
            <g key={i}>
              <line x1={-1100 + i * 110} y1={-320} x2={-1100 + i * 110 + 640} y2={320} stroke="#cfd6c4" strokeWidth={1.5} />
              <line x1={1100 - i * 110} y1={-320} x2={1100 - i * 110 - 640} y2={320} stroke="#cfd6c4" strokeWidth={1.5} />
            </g>
          ))}
        </g>
        {groups.map((g, gi) => {
          const rows = Math.ceil(g.n / g.cols);
          const cell = Math.min(64, 760 / Math.max(g.cols, rows) / (vs ? 1.25 : 1));
          const s = cell / 44;
          const out: React.ReactNode[] = [];
          const order: { i: number; y: number }[] = [];
          for (let i = 0; i < g.n; i++) {
            const c = march ? i % 2 : i % g.cols;
            const r = march ? Math.floor(i / 2) : Math.floor(i / g.cols);
            // 아이소메트릭 투영: x = (c - r), y = (c + r)/2
            const gx = march ? (c - 0.5) * cell * 1.3 - r * cell * 0.9 : (c - r) * cell * 0.9 - ((g.cols - rows) * cell * 0.9) / 2;
            const gy = march ? (c + r) * cell * 0.45 : (c + r) * cell * 0.5 - ((g.cols + rows) * cell * 0.5) / 2;
            order.push({ i, y: gy });
            const appear = clamp((t - 0.05 - hash(i + gi * 97) * 0.6) / 0.35);
            const keep = v.keep ?? g.n;
            const isKeep = gi === 0 && i >= g.n - keep;
            const op = gi === 0 && keepS !== null && !isKeep ? appear * (1 - kk) : appear;
            const mx = march ? ((t * 40) % (cell * 0.9)) : 0;
            out[i] = <Soldier key={i} x={g.ox + gx + mx} y={600 + gy - (1 - appear) * 40} s={s} side={g.side} op={op} hi={gi === 0 && keepS !== null && isKeep && kk > 0.3} step={march ? t * 7 + i : 0} />;
          }
          order.sort((a, b) => a.y - b.y);
          return <g key={gi}>{order.map((o) => out[o.i])}</g>;
        })}
      </svg>
      {v.title && (
        <div style={{ position: "absolute", top: 70, left: 0, right: 0, textAlign: "center", fontFamily: F.head, fontSize: 84, color: "#fff", textShadow: "0 4px 0 #000, 0 0 24px rgba(0,0,0,.8)", opacity: clamp(t * 2) }}>{v.title}</div>
      )}
      {(v.labels || []).map((l: any, i: number) => {
        const a = atSec(sc, l.at ?? 0);
        const o = popIn((t - a) / 0.4);
        if (t < a) return null;
        return (
          <div key={i} style={{ position: "absolute", left: l.x * 1920, top: l.y * 1080, transform: `translate(-50%,-50%) scale(${o})`, padding: "10px 28px", background: l.color === "red" ? "#c9242c" : l.color === "blue" ? "#1f5fbf" : "#111", border: "4px solid #fff", fontFamily: F.head, fontSize: 60, color: "#fff", whiteSpace: "nowrap", boxShadow: "0 8px 24px rgba(0,0,0,.6)" }}>
            {l.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
