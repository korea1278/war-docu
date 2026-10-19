import "@fontsource/black-han-sans/400.css";
import "@fontsource/do-hyeon/400.css";
import "@fontsource/noto-sans-kr/500.css";
import "@fontsource/noto-sans-kr/700.css";
import "@fontsource/noto-sans-kr/900.css";

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
