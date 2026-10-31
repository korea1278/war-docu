import "@fontsource/black-han-sans/400.css";
import "@fontsource/do-hyeon/400.css";
import "@fontsource/noto-sans-kr/500.css";
import "@fontsource/noto-sans-kr/700.css";
import "@fontsource/noto-sans-kr/900.css";
import "@fontsource/oswald/600.css";
import "@fontsource/oswald/700.css";
import "@fontsource/roboto-condensed/600.css";
import "@fontsource/roboto-condensed/700.css";

export const W = 1920;
export const H = 1080;

export const C = {
  red: "#c9242c",
  redDark: "#8f141b",
  blue: "#2e66d8",
  blueDark: "#1b3f8f",
  yellow: "#f4c430",
  ink: "#121314",
  white: "#ffffff",
  subBorder: "#22594a",
  sea: "#5a5f66",
  foreign: "#e7a4a4",
  water: "#7aa3d6",
  land: "#e9eaec",
};

export const F = {
  head: "'Black Han Sans', 'Noto Sans KR', sans-serif",
  sub: "'Do Hyeon', 'Noto Sans KR', sans-serif",
  body: "'Noto Sans KR', sans-serif",
};

/** 언어별 글꼴·고정 문구 (렌더 시작 시 setLang 호출) */
export let LANG: "ko" | "en" = "ko";
export const setLang = (l?: string) => {
  LANG = l === "en" ? "en" : "ko";
  if (LANG === "en") {
    F.head = "'Oswald', 'Black Han Sans', sans-serif";
    F.sub = "'Roboto Condensed', 'Do Hyeon', sans-serif";
    F.body = "'Roboto Condensed', 'Noto Sans KR', sans-serif";
  } else {
    F.head = "'Black Han Sans', 'Noto Sans KR', sans-serif";
    F.sub = "'Do Hyeon', 'Noto Sans KR', sans-serif";
    F.body = "'Noto Sans KR', sans-serif";
  }
};
const STR = {
  ko: { map: "지도: Natural Earth · OpenStreetMap · SRTM", ai: "AI 생성 이미지", factors: "1개 사단 vs 3개 사단 — 왜?", lesson: "용문산 전투가 남긴 교훈", stamp: "軍 秘", sub: "구독", like: "좋아요 👍", subbed: "구독중", likeTxt: "좋아요" },
  en: { map: "Map: Natural Earth · OpenStreetMap · SRTM", ai: "AI-generated image", factors: "1 Division vs 3 — Why?", lesson: "The Lesson of Yongmunsan", stamp: "DECLASSIFIED", sub: "SUBSCRIBE", like: "LIKE 👍", subbed: "SUBSCRIBED", likeTxt: "LIKE" },
};
export const S = (k: keyof (typeof STR)["ko"]) => STR[LANG][k];

export type Line = { text: string; start: number; end: number; chunks: { text: string; start: number; end: number }[] };

export type Scene = {
  id: string;
  start: number;
  dur: number;
  audio: string | null;
  audioAt: number;
  lines: Line[];
  visual: any;
  label?: string | null;
  callouts: { text: string; style: "red" | "yellow" | "dark"; at: number; pos?: string }[];
  sfx: { id: string; at: number; volume?: number }[];
  chapter?: { num: string; title: string; big?: boolean } | null;
};

export type Timeline = {
  lang?: string;
  fps: number;
  duration: number;
  title: string;
  places: Record<string, [number, number, string]>;
  views: Record<string, { center: [number, number]; span: number }>;
  scenes: Scene[];
  music: { id: string; start: number; dur: number; volume: number; src: string | null; fileDur?: number }[];
  rasters: { name: string; file: string; west: number; east: number; north: number; south: number; w: number; h: number }[];
  sfx: string[];
  hasWater: boolean;
};

/** 스토리보드의 at(줄 번호, 소수 허용) → 장면 내 초 */
export const atSec = (scene: Scene, at: number | undefined): number => {
  if (at === undefined || at === null) return 0;
  const ls = scene.lines;
  if (!ls.length) return at;
  const i = Math.floor(at);
  if (i >= ls.length) return ls[ls.length - 1].end;
  const l = ls[Math.max(0, i)];
  const frac = at - i;
  return l.start + frac * Math.max(0.6, l.end - l.start);
};

export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const easeOut = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
export const easeInOut = (t: number) => {
  t = clamp(t);
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
};
/** 살짝 튀어오르는 등장 */
export const popIn = (t: number) => {
  t = clamp(t);
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};

/**
 * 한 줄 맞춤 글자 크기 (2026-10-31 줄바꿈 버그 패치)
 * Black Han Sans 기준 대략 폭: 한글 1.0em · 영문/숫자 0.56em · 공백 0.3em · 문장부호 0.38em.
 * 박스 안 핵심 키워드가 외톨이 글자 없이 한 줄(nowrap)에 들어가도록 기본 크기에서 줄여 준다.
 */
export const estWidthEm = (text: string, letterSpacingEm = 0) => {
  let w = 0;
  for (const ch of String(text ?? "")) {
    if (/[\u3131-\uD7A3\u4E00-\u9FFF]/.test(ch)) w += 1.0;
    else if (ch === " ") w += 0.3;
    else if (/[A-Za-z0-9]/.test(ch)) w += 0.56;
    else w += 0.38;
    w += letterSpacingEm;
  }
  return w;
};
export const fitFont = (text: string, maxW: number, base: number, min = 40, letterSpacingEm = 0) => {
  const lines = String(text ?? "").split("\n");
  const em = Math.max(...lines.map((l) => estWidthEm(l, letterSpacingEm)), 0.01);
  return Math.max(min, Math.min(base, Math.floor(maxW / em)));
};
/** 박스 안 텍스트 공통: 음절 단위로 쪼개지지 않게 */
export const NOBREAK: { wordBreak: "keep-all"; overflowWrap: "normal" } = { wordBreak: "keep-all", overflowWrap: "normal" };
