import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile } from "remotion";

/* =====================================================================================
 * ★★★ 썸네일 표준 v4 = '조회수 레퍼런스' 공식 (2026-11-24 사용자 지시 · war-docu·map-of-war 공통 · 이후 모든 신규 롱폼 A안 — v3보다 우선)
 *   레퍼런스: 조회수가 잘 나온 남의 썸네일 5장(낙동강 트럭 300대 · 아마존강 다리 · 러일전쟁 · 73 이스팅 · 6.25 전쟁 전날)
 *   ① 배경: 대본 핵심 장면 사진/재연 그림 Full-Bleed (흑백·컬러는 저장소 기본값 그대로 — war-docu 흑백, map-of-war 컬러)
 *   ② 왼쪽 위 태그 박스 `tag` — 대본에 맞게 매번 새로 창작 ("장소 | 연월", "전쟁명 | 그날", "작전명" 등)
 *      `tagStyle`: red(빨강 바탕·흰 글자) · cream(미색 바탕·검은 글자) · black(검정 바탕·흰 글자, | 뒤 노랑) · yellow(노랑 바탕·검은 글자) · white
 *      "|"로 나누면 가는 구분선으로 표시. 색은 편의 분위기에 맞게 고른다 (위기·비극=red, 전술 분석=cream, 미스터리=black, 의외의 사실=yellow)
 *   ③ 하단 큰 글자 2줄 — 검은 굵은 외곽선, 기본 흰색, **단어 단위 강조색**: `[빨강]` `{노랑}` (예: "트럭 [300대]가" / "[30대만] 남았다")
 *      두 줄은 같은 크기(가장 긴 줄 기준으로 가로를 채움, 상한 210px) · `box2: true`면 2줄째를 빨간 박스 위 흰 글자로 (질문형에 어울림)
 *      `align`: left(기본) · center · right — 인물·피사체를 피하는 쪽으로
 *   ④ 선택: 말풍선 `bubble` {text, x, y, to:[꼬리 끝 x,y]} — 등장인물·현장의 한마디 ("큰일납니다")
 *            사진 설명 라벨 `note` (v3과 같음)
 *   ⑤ 오른쪽 아래 재생시간 표시 없음 · 위 가운데 검은 박스(v3 top) 없음
 *   카피 공식: Line 1 = [구체적 숫자·상황] / Line 2 = [충격적 결과 또는 질문] — 숫자는 대본에서 확인된 것만, 줄당 5~10자
 * ===================================================================================== */

export type HitTagStyle = "red" | "cream" | "black" | "yellow" | "white";
export type HitBubble = { text: string; x: number; y: number; to?: [number, number]; size?: number };
export type HitNote = { text: string; x: number; y: number; to: [number, number]; size?: number };
export interface HitProps {
  bg: string; // 이미 해석된 public 경로
  bgPos?: string;
  filter: string;
  line1: string;
  line2: string;
  tag?: string;
  tagStyle?: HitTagStyle;
  box2?: boolean | string; // true = 빨강 박스, 문자열 = 박스 색
  align?: "left" | "center" | "right";
  size?: number; // 글자 크기 직접 지정 (없으면 자동)
  bubble?: HitBubble;
  note?: HitNote;
  en?: boolean;
}

const W = 1920, H = 1080;
const HIT = { side: 54, bottom: 34, max: 210, min: 120, fill: 0.96, red: "#FF2B2B", yellow: "#FFD83A", boxRed: "#E3221C" };
const FONT_KO = "'Pretendard', 'Black Han Sans', sans-serif";
const FONT_EN = "'Montserrat', 'Anton', sans-serif";
const TAG: Record<HitTagStyle, { bg: string; fg: string; accent?: string }> = {
  red: { bg: "#E0241B", fg: "#FFFFFF" },
  cream: { bg: "#F2E8D0", fg: "#141414" },
  black: { bg: "rgba(12,12,12,.94)", fg: "#FFFFFF", accent: HIT.yellow },
  yellow: { bg: "#FFD400", fg: "#141414" },
  white: { bg: "#FFFFFF", fg: "#141414" },
};

/** "트럭 [300대]가" → [{t:"트럭 ",c:null},{t:"300대",c:red},{t:"가",c:null}] */
const parse = (s: string): { t: string; c: string | null }[] =>
  s.split(/(\[[^\]]*\]|\{[^}]*\})/).filter(Boolean).map((p) =>
    p.startsWith("[") ? { t: p.slice(1, -1), c: HIT.red } : p.startsWith("{") ? { t: p.slice(1, -1), c: HIT.yellow } : { t: p, c: null },
  );
const plain = (s: string) => parse(s).map((p) => p.t).join("");

const useMeasure = (texts: string[], font: string) => {
  const [fn, setFn] = useState<((t: string) => number) | null>(null);
  const [hd] = useState(() => delayRender("hit-measure"));
  useEffect(() => {
    const fam = font.split(",")[0].trim();
    document.fonts.load(`900 100px ${fam}`, texts.join(""))
      .then(() => document.fonts.ready)
      .then(() => {
        const ctx = document.createElement("canvas").getContext("2d")!;
        ctx.font = `900 100px ${font}`;
        setFn(() => (t: string) => (ctx.measureText(t).width - 2 * Math.max(0, [...t].length - 1)) / 100);
      })
      .catch(() => setFn(() => (t: string) => [...t].length * 0.92))
      .finally(() => continueRender(hd));
  }, [texts.join("|")]);
  return fn;
};

const Tag: React.FC<{ text: string; style: HitTagStyle; font: string }> = ({ text, style, font }) => {
  const c = TAG[style] || TAG.red;
  const parts = text.split("|").map((s) => s.trim());
  const size = 60;
  return (
    <div style={{ position: "absolute", left: 40, top: 36, display: "flex", alignItems: "center", background: c.bg, borderRadius: 10, padding: `${size * 0.14}px ${size * 0.42}px ${size * 0.2}px`, boxShadow: "0 6px 18px rgba(0,0,0,.55)", fontFamily: font, fontWeight: 900, fontSize: size, lineHeight: 1.1, letterSpacing: "-0.02em", whiteSpace: "nowrap", color: c.fg }}>
      {parts.map((p, i) => (
        <React.Fragment key={i}>
          {i > 0 && <span style={{ display: "inline-block", width: 4, height: size * 0.8, background: c.fg, opacity: 0.55, margin: `0 ${size * 0.3}px`, borderRadius: 2 }} />}
          <span style={{ color: i > 0 && c.accent ? c.accent : c.fg }}>{p}</span>
        </React.Fragment>
      ))}
    </div>
  );
};

const Bubble: React.FC<{ b: HitBubble; font: string; w: number }> = ({ b, font, w }) => {
  const size = b.size ?? 66;
  const rx = (w * size) / 2 + size * 0.85;
  const ry = size * 1.05;
  const to = b.to ?? [b.x + rx * 0.7, b.y + ry * 1.7];
  // 꼬리: 타원 가장자리 두 점 → 꼬리 끝
  const ang = Math.atan2((to[1] - b.y) / ry, (to[0] - b.x) / rx);
  const p = (a: number) => [b.x + rx * Math.cos(a) * 0.92, b.y + ry * Math.sin(a) * 0.92];
  const [a1, a2] = [p(ang - 0.28), p(ang + 0.28)];
  const tail = `M ${a1[0]} ${a1[1]} L ${to[0]} ${to[1]} L ${a2[0]} ${a2[1]} Z`;
  return (
    <>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <g filter="drop-shadow(0 8px 10px rgba(0,0,0,.55))">
          <ellipse cx={b.x} cy={b.y} rx={rx} ry={ry} fill="#fff" stroke="#111" strokeWidth={9} />
          <path d={tail} fill="#fff" stroke="#111" strokeWidth={9} strokeLinejoin="round" />
          <ellipse cx={b.x} cy={b.y} rx={rx - 4.5} ry={ry - 4.5} fill="#fff" />
        </g>
      </svg>
      <div style={{ position: "absolute", left: b.x - rx, top: b.y - ry, width: rx * 2, height: ry * 2, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: font, fontWeight: 900, fontSize: size, color: "#111", letterSpacing: "-0.03em", whiteSpace: "nowrap" }}>{b.text}</div>
    </>
  );
};

const Note: React.FC<{ n: HitNote; font: string; w: number }> = ({ n, font, w }) => {
  const size = n.size ?? 46;
  const bw = w * size + size * 0.9;
  const bh = size * 1.5;
  const [tx, ty] = n.to;
  const sx = Math.max(n.x - bw / 2 + 20, Math.min(n.x + bw / 2 - 20, tx));
  const sy = ty > n.y ? n.y + bh / 2 + 8 : n.y - bh / 2 - 8;
  const dx = tx - sx, dy = ty - sy;
  const cx = sx + dx * 0.15 + (dy > 0 ? -1 : 1) * Math.abs(dy) * 0.5 * Math.sign(dx || 1);
  const cy = sy + dy * 0.85;
  const ang = Math.atan2(ty - cy, tx - cx);
  const L = 30;
  const head = `M ${tx} ${ty} L ${tx - L * Math.cos(ang - 0.5)} ${ty - L * Math.sin(ang - 0.5)} M ${tx} ${ty} L ${tx - L * Math.cos(ang + 0.5)} ${ty - L * Math.sin(ang + 0.5)}`;
  const path = `M ${sx} ${sy} Q ${cx} ${cy} ${tx} ${ty}`;
  return (
    <>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {([["#000", 13, 0.55], ["#fff", 7, 1]] as const).map(([c, sw, op], i) => (
          <g key={i} fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" opacity={op}>
            <path d={path} />
            <path d={head} />
          </g>
        ))}
      </svg>
      <div style={{ position: "absolute", left: n.x - bw / 2, top: n.y - bh / 2, width: bw, height: bh, background: "#fff", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: font, fontWeight: 900, fontSize: size, color: "#111", letterSpacing: "-0.02em", whiteSpace: "nowrap", boxShadow: "0 6px 18px rgba(0,0,0,.55)" }}>{n.text}</div>
    </>
  );
};

export const HitThumb: React.FC<{ d: HitProps }> = ({ d }) => {
  const font = d.en ? FONT_EN : FONT_KO;
  const measure = useMeasure([plain(d.line1), plain(d.line2), d.tag || "", d.bubble?.text || "", d.note?.text || ""], font);
  const box = d.box2 ? (typeof d.box2 === "string" ? d.box2 : HIT.boxRed) : null;
  const avail = (W - HIT.side * 2) * HIT.fill;
  const m1 = measure ? measure(plain(d.line1)) : plain(d.line1).length * 0.92;
  const m2 = measure ? measure(plain(d.line2)) : plain(d.line2).length * 0.92;
  const boxPad = box ? 0.5 : 0; // 박스 좌우 여백 (글자 크기 배수)
  const auto = Math.floor(Math.min(avail / Math.max(0.5, m1), avail / Math.max(0.5, m2 + boxPad)));
  const size = d.size ?? Math.max(HIT.min, Math.min(HIT.max, auto));
  const lh = 1.08;
  const gap = Math.round(size * (box ? 0.1 : 0.0));
  const blockH = size * lh * 2 + gap + (box ? size * 0.16 : 0);
  const textTop = H - HIT.bottom - blockH;
  const justify = d.align === "right" ? "flex-end" : d.align === "center" ? "center" : "flex-start";
  const stroke = Math.round(size * 0.075);
  const lineEl = (s: string, onBox: boolean) => (
    <div style={{ fontFamily: font, fontWeight: 900, fontSize: size, lineHeight: lh, letterSpacing: "-0.03em", whiteSpace: "nowrap", color: "#fff",
      ...(onBox ? { textShadow: `0 ${Math.round(size * 0.03)}px ${Math.round(size * 0.05)}px rgba(0,0,0,.45)` }
        : { WebkitTextStroke: `${stroke}px #000`, paintOrder: "stroke fill", textShadow: `0 ${Math.round(size * 0.045)}px 0 #000, 0 ${Math.round(size * 0.06)}px ${Math.round(size * 0.12)}px rgba(0,0,0,.9)` }) }}>
      {parse(s).map((p, i) => <span key={i} style={{ color: onBox ? "#fff" : p.c ?? "#fff" }}>{p.t}</span>)}
    </div>
  );
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <style>{`@font-face{font-family:'Pretendard';font-weight:900;font-style:normal;src:url(${staticFile("fonts/Pretendard-Black.woff2")}) format('woff2');}`}</style>
      <Img src={staticFile(d.bg)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", objectPosition: d.bgPos || "50% 40%", filter: d.filter }} />
      {/* 가장자리 비네트 + 왼쪽 위(태그) 살짝 어둡게 */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 55% 40%, rgba(0,0,0,0) 55%, rgba(0,0,0,.42) 100%)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 700px 260px at 0% 0%, rgba(0,0,0,.45), rgba(0,0,0,0))" }} />
      {/* 아래쪽 글자 뒤만 어둡게 — 솔리드 바닥판 없이 사진 위에 글자 */}
      <div style={{ position: "absolute", left: 0, right: 0, top: textTop - 240, bottom: 0, background: "linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,.45) 40%, rgba(0,0,0,.78) 75%, rgba(0,0,0,.88) 100%)" }} />
      {d.note && <Note n={d.note} font={font} w={measure ? measure(d.note.text) : d.note.text.length * 0.9} />}
      {d.bubble && <Bubble b={d.bubble} font={font} w={measure ? measure(d.bubble.text) : d.bubble.text.length * 0.9} />}
      {d.tag && <Tag text={d.tag} style={d.tagStyle || "red"} font={font} />}
      <div style={{ position: "absolute", left: HIT.side, right: HIT.side, top: textTop, display: "flex", flexDirection: "column", alignItems: justify, gap }}>
        {lineEl(d.line1, false)}
        {box ? (
          <div style={{ background: box, padding: `${size * 0.02}px ${size * 0.25}px ${size * 0.14}px`, borderRadius: 6, boxShadow: "0 8px 22px rgba(0,0,0,.6)" }}>{lineEl(d.line2, true)}</div>
        ) : (
          lineEl(d.line2, false)
        )}
      </div>
    </AbsoluteFill>
  );
};
