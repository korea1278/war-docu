import React, { createContext, useContext } from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { atSec, C, clamp, easeOut, F, popIn, Scene } from "./theme";

export const SceneCtx = createContext<Scene | null>(null);
export const useScene = () => useContext(SceneCtx)!;

/** 장면 시작부터 경과한 초 */
export const useT = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return f / fps;
};

/** at 시점 이후 경과 초 (등장 애니메이션용) */
export const useSince = (at: number | undefined, extra = 0) => {
  const sc = useScene();
  const t = useT();
  return t - (atSec(sc, at) + extra);
};

export const Slate: React.FC<{ dim?: number }> = ({ dim = 0 }) => (
  <AbsoluteFill>
    <Img src={staticFile("ui/slate.jpg")} style={{ width: "100%", height: "100%", filter: "brightness(1.18)" }} />
    {dim > 0 && <AbsoluteFill style={{ background: `rgba(0,0,0,${dim})` }} />}
  </AbsoluteFill>
);

export const Grain: React.FC = () => {
  const f = useCurrentFrame();
  const x = ((f * 37) % 97) - 48;
  const y = ((f * 53) % 89) - 44;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "overlay", opacity: 0.16, overflow: "hidden" }}>
      <Img
        src={staticFile("ui/grain.png")}
        style={{ position: "absolute", left: -60 + x, top: -60 + y, width: 2040, height: 1200, imageRendering: "pixelated" }}
      />
    </AbsoluteFill>
  );
};

export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.55 }) => (
  <AbsoluteFill
    style={{ background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,${strength}) 100%)`, pointerEvents: "none" }}
  />
);

/* ---------------- 하단 자막 ---------------- */
export const Subtitles: React.FC = () => {
  const sc = useScene();
  const t = useT();
  let cur: { text: string; start: number; end: number } | null = null;
  const chunks = sc.lines.flatMap((l) => l.chunks);
  for (let i = 0; i < chunks.length; i++) {
    const c = chunks[i];
    const next = chunks[i + 1];
    const hold = next ? Math.min(next.start, c.end + 0.6) : c.end + 0.45;
    if (t >= c.start - 0.05 && t < hold) cur = c;
  }
  if (!cur) return null;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 52, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          position: "relative",
          background: "#fff",
          border: `5px solid ${C.subBorder}`,
          borderRadius: 10,
          boxShadow: "0 0 0 3px #fff, 0 6px 18px rgba(0,0,0,.45)",
          padding: "8px 34px 6px",
          fontFamily: F.sub,
          fontSize: 54,
          color: "#111",
          lineHeight: 1.15,
          letterSpacing: 0.5,
          whiteSpace: "nowrap",
        }}
      >
        <Notch pos="tl" />
        <Notch pos="tr" />
        <Notch pos="bl" />
        <Notch pos="br" />
        {cur.text}
      </div>
    </div>
  );
};

const Notch: React.FC<{ pos: "tl" | "tr" | "bl" | "br" }> = ({ pos }) => {
  const s: React.CSSProperties = { position: "absolute", width: 14, height: 14, background: C.subBorder, borderRadius: 3 };
  if (pos[0] === "t") s.top = -10;
  else s.bottom = -10;
  if (pos[1] === "l") s.left = -10;
  else s.right = -10;
  return <div style={{ ...s, transform: "rotate(45deg)", boxShadow: "0 0 0 3px #fff" }} />;
};

/* ---------------- 우상단 출처 + 라벨 ---------------- */
export const LabelBox: React.FC<{ label?: string | null; credit?: string | null }> = ({ label, credit }) => {
  const t = useT();
  const o = easeOut((t - 0.25) / 0.35);
  if (!label && !credit) return null;
  return (
    <div style={{ position: "absolute", top: 18, right: 26, display: "flex", flexDirection: "column", alignItems: "flex-end", opacity: o }}>
      {credit && (
        <div style={{ fontFamily: F.body, fontWeight: 500, fontSize: 21, color: "rgba(255,255,255,.85)", textShadow: "0 1px 3px #000", marginBottom: 10 }}>
          {credit}
        </div>
      )}
      {label && (
        <div style={{ position: "relative" }}>
          <div
            style={{
              background: "#0d0d0d",
              color: "#fff",
              fontFamily: F.body,
              fontWeight: 700,
              fontSize: 29,
              padding: "9px 22px",
              border: "3px solid #fff",
              borderRadius: 4,
              boxShadow: "0 4px 14px rgba(0,0,0,.5)",
            }}
          >
            {label}
          </div>
          <svg width="44" height="30" style={{ position: "absolute", right: 34, bottom: -26 }}>
            <path d="M0 0 L44 0 L36 26 Z" fill="#0d0d0d" />
            <path d="M2 0 L36 26 L42 0" fill="none" stroke="#fff" strokeWidth="3" />
          </svg>
        </div>
      )}
    </div>
  );
};

/* ---------------- 강조 박스 ---------------- */
export const CalloutBox: React.FC<{ text: string; style: "red" | "yellow" | "dark" | "blue"; size?: number; scale?: number }> = ({
  text,
  style,
  size = 74,
  scale = 1,
}) => {
  const bg = style === "red" ? C.red : style === "yellow" ? C.yellow : style === "blue" ? C.blue : "#0f0f0f";
  const fg = style === "yellow" ? "#111" : "#fff";
  return (
    <div
      style={{
        display: "inline-block",
        background: bg,
        color: fg,
        fontFamily: F.head,
        fontSize: size,
        lineHeight: 1.12,
        padding: "10px 30px 6px",
        border: style === "dark" ? "4px solid #fff" : "none",
        boxShadow: "0 8px 26px rgba(0,0,0,.45)",
        transform: `scale(${scale})`,
        whiteSpace: "pre",
        textAlign: "center",
      }}
    >
      {text}
    </div>
  );
};

export const Callouts: React.FC = () => {
  const sc = useScene();
  const t = useT();
  const shown = sc.callouts
    .map((c, i) => ({ ...c, i, s: atSec(sc, c.at) + 0.1 }))
    .filter((c) => t >= c.s);
  // 같은 위치는 마지막 것만
  const byPos = new Map<string, (typeof shown)[number]>();
  const defPos = sc.visual?.type === "map" ? "top" : "center";
  for (const c of shown) byPos.set(c.pos || defPos, c);
  return (
    <>
      {[...byPos.values()].map((c) => {
        const k = (t - c.s) / 0.35;
        const pos = c.pos || defPos;
        const top = pos === "lower" ? 690 : pos === "top" ? 120 : 430;
        return (
          <div key={c.i} style={{ position: "absolute", left: 0, right: 0, top, display: "flex", justifyContent: "center", opacity: clamp(k * 3) }}>
            <CalloutBox text={c.text} style={c.style} scale={0.6 + 0.4 * popIn(k)} size={pos === "lower" ? 60 : pos === "top" ? 66 : 74} />
          </div>
        );
      })}
    </>
  );
};

/* ---------------- 챕터 오버레이 ---------------- */
export const ChapterOverlay: React.FC = () => {
  const sc = useScene();
  const t = useT();
  const ch = sc.chapter;
  if (!ch) return null;
  const D = ch.big ? 2.4 : 2.1;
  if (t > D + 0.4) return null;
  const inK = easeOut(t / 0.35);
  const outK = 1 - easeOut((t - D) / 0.4);
  const o = Math.min(inK, outK);
  return (
    <AbsoluteFill style={{ background: `rgba(8,8,10,${0.72 * o})`, justifyContent: "center", alignItems: "center", opacity: o }}>
      <div style={{ textAlign: "center", transform: `translateY(${(1 - inK) * 30}px)` }}>
        <div style={{ display: "inline-block", background: C.yellow, color: "#111", fontFamily: F.head, fontSize: 52, padding: "6px 24px 2px", marginBottom: 22 }}>
          {ch.num}
        </div>
        <div style={{ fontFamily: F.head, fontSize: 118, color: "#fff", textShadow: "0 6px 30px rgba(0,0,0,.6)" }}>{ch.title}</div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- 말풍선 ---------------- */
export const Bubble: React.FC<{ text: string; x: number; y: number; at: number }> = ({ text, x, y, at }) => {
  const k = useSince(at, 0.15) / 0.3;
  if (k < 0) return null;
  const s = 0.5 + 0.5 * popIn(k);
  return (
    <div
      style={{
        position: "absolute",
        left: x * 1920,
        top: y * 1080,
        transform: `translate(-50%,-50%) scale(${s})`,
        opacity: clamp(k * 3),
      }}
    >
      <div
        style={{
          position: "relative",
          background: "#fff",
          border: "5px solid #111",
          borderRadius: 26,
          padding: "16px 34px 12px",
          fontFamily: F.sub,
          fontSize: 60,
          lineHeight: 1.15,
          color: "#111",
          textAlign: "center",
          whiteSpace: "pre-line",
          boxShadow: "0 8px 0 rgba(0,0,0,.25)",
        }}
      >
        {text}
        <svg width="60" height="46" style={{ position: "absolute", left: "50%", bottom: -42, marginLeft: -20 }}>
          <path d="M4 0 L48 0 L10 42 Z" fill="#fff" />
          <path d="M6 2 L10 42 L48 2" fill="none" stroke="#111" strokeWidth="5" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  );
};

/* ---------------- 켄 번스 이미지 ---------------- */
export const KenBurns: React.FC<{ src: string; kb?: string; bw?: boolean; fit?: "cover" | "contain"; pos?: string }> = ({ src, kb = "in", bw = true, fit = "cover", pos = "50% 50%" }) => {
  const sc = useScene();
  const t = useT();
  const p = clamp(t / sc.dur);
  let s = 1.04,
    x = 0,
    y = 0;
  if (kb === "in") s = 1.04 + 0.12 * p;
  else if (kb === "in2") s = 1.12 + 0.08 * p;
  else if (kb === "out") s = 1.18 - 0.12 * p;
  else if (kb === "left") (s = 1.14), (x = 3.5 - 7 * p);
  else if (kb === "right") (s = 1.14), (x = -3.5 + 7 * p);
  else if (kb === "up") (s = 1.14), (y = 3 - 6 * p);
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#111" }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: fit,
          objectPosition: pos,
          transformOrigin: pos,
          transform: `scale(${s}) translate(${x}%, ${y}%)`,
          filter: bw ? "grayscale(1) contrast(1.12) brightness(.96)" : "saturate(.8) contrast(1.05)",
        }}
      />
    </AbsoluteFill>
  );
};
