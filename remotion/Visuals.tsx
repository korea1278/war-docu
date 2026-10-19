import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { atSec, C, clamp, easeInOut, easeOut, F, popIn, Timeline } from "./theme";
import { Bubble, CalloutBox, KenBurns, Slate, useScene, useSince, useT } from "./ui";
import { MapView } from "./MapView";

/** 사진이 없을 때 대체 배경 */
const PhotoOrSlate: React.FC<{ src?: string | null; kb?: string; bw?: boolean; dim?: number }> = ({ src, kb, bw = true, dim = 0 }) =>
  src ? (
    <AbsoluteFill>
      <KenBurns src={src} kb={kb} bw={bw} />
      {dim > 0 && <AbsoluteFill style={{ background: `rgba(0,0,0,${dim})` }} />}
    </AbsoluteFill>
  ) : (
    <Slate dim={dim * 0.5} />
  );

const Appear: React.FC<{ at?: number; extra?: number; dy?: number; children: React.ReactNode; style?: React.CSSProperties; pop?: boolean }> = ({
  at,
  extra = 0,
  dy = 30,
  children,
  style,
  pop,
}) => {
  const k = useSince(at, extra) / 0.45;
  if (k < 0) return null;
  const e = pop ? popIn(k) : easeOut(k);
  return <div style={{ opacity: clamp(k * 2), transform: pop ? `scale(${0.6 + 0.4 * e})` : `translateY(${(1 - e) * dy}px)`, ...style }}>{children}</div>;
};

/* ---------- photo / ai ---------- */
const PhotoV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  if (v.frame) {
    const s = 1 + 0.05 * clamp(t / sc.dur);
    return (
      <AbsoluteFill>
        <Slate />
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingBottom: 90 }}>
          {v.src ? (
            <div style={{ transform: `scale(${s}) rotate(-1deg)`, background: "#f3f1ea", padding: 14, boxShadow: "0 18px 50px rgba(0,0,0,.6)" }}>
              <Img src={staticFile(v.src)} style={{ maxHeight: 720, maxWidth: 1300, display: "block", filter: "grayscale(1) contrast(1.1)" }} />
            </div>
          ) : null}
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }
  return <PhotoOrSlate src={v.src} kb={v.kb} bw={v.bw !== false} />;
};

const AiV: React.FC = () => {
  const v = useScene().visual;
  return (
    <AbsoluteFill>
      <PhotoOrSlate src={v.src} kb={v.kb} bw={false} />
      {(v.bubbles || []).map((b: any, i: number) => (
        <Bubble key={i} {...b} />
      ))}
    </AbsoluteFill>
  );
};

/* ---------- 텍스트 / 블랙 ---------- */
const TextV: React.FC = () => {
  const v = useScene().visual;
  return (
    <AbsoluteFill>
      <Slate />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", paddingBottom: 80 }}>
        <Appear pop at={0}>
          <CalloutBox text={v.big} style={v.style || "red"} size={110} />
        </Appear>
        {v.sub && (
          <Appear at={v.subAt ?? 0} extra={0.5}>
            <div style={{ marginTop: 34, fontFamily: F.body, fontWeight: 700, fontSize: 40, color: "rgba(255,255,255,.85)" }}>{v.sub}</div>
          </Appear>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const BlackV: React.FC = () => {
  const v = useScene().visual;
  const t = useT();
  return (
    <AbsoluteFill style={{ background: "#050505", justifyContent: "center", alignItems: "center", flexDirection: "column", paddingBottom: 60 }}>
      <div style={{ opacity: easeOut((t - 0.2) / 1.2), fontFamily: F.head, fontSize: 92, color: "#f2f2f2", textAlign: "center", whiteSpace: "pre-line", lineHeight: 1.3 }}>
        {v.text}
      </div>
      {v.accent && (
        <Appear pop at={v.accentAt ?? 0} style={{ marginTop: 40 }}>
          <CalloutBox text={v.accent} style="red" size={120} />
        </Appear>
      )}
    </AbsoluteFill>
  );
};

/* ---------- 타이틀 / 엔드 카드 ---------- */
const TitleCardV: React.FC = () => {
  const v = useScene().visual;
  const k = useSince(v.at, 0) / 0.8;
  return (
    <AbsoluteFill>
      <PhotoOrSlate src={v.src} kb="in" dim={0.25 + 0.35 * clamp(k)} />
      {k > 0 && (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", paddingBottom: 90 }}>
          <div style={{ width: 900 * easeOut(k), height: 5, background: C.yellow, marginBottom: 30 }} />
          <div style={{ fontFamily: F.head, fontSize: 150, color: "#fff", opacity: clamp(k * 1.5), textShadow: "0 8px 40px rgba(0,0,0,.8)", letterSpacing: 2 }}>
            {v.title}
          </div>
          <div style={{ fontFamily: F.head, fontSize: 56, color: C.yellow, marginTop: 14, opacity: clamp(k - 0.4) }}>{v.sub}</div>
          <div style={{ width: 900 * easeOut(k), height: 5, background: C.yellow, marginTop: 30 }} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

const EndCardV: React.FC = () => {
  const v = useScene().visual;
  const t = useT();
  const k = easeOut((t - 0.3) / 1);
  const btn = popIn((t - 2.5) / 0.4);
  return (
    <AbsoluteFill>
      <PhotoOrSlate src={v.src} kb="out" dim={0.62} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", paddingBottom: 120 }}>
        <div style={{ fontFamily: F.head, fontSize: 104, color: "#fff", opacity: k, textAlign: "center", whiteSpace: "pre-line", lineHeight: 1.25 }}>{v.title}</div>
        {t > 2.5 && (
          <div style={{ display: "flex", gap: 30, marginTop: 60, transform: `scale(${btn})` }}>
            <div style={{ background: C.red, color: "#fff", fontFamily: F.head, fontSize: 56, padding: "14px 46px 8px", borderRadius: 14 }}>구독</div>
            <div style={{ background: "#fff", color: "#111", fontFamily: F.head, fontSize: 56, padding: "14px 46px 8px", borderRadius: 14 }}>좋아요 👍</div>
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- 인물 카드 ---------- */
const PersonV: React.FC = () => {
  const v = useScene().visual;
  const t = useT();
  const k = easeOut(t / 0.6);
  const k2 = easeOut((t - 0.35) / 0.6);
  return (
    <AbsoluteFill>
      <Slate />
      <div style={{ position: "absolute", left: 230, top: 150, transform: `translateX(${(1 - k) * -60}px) rotate(-1.5deg)`, opacity: k }}>
        <div style={{ background: "#f3f1ea", padding: 14, boxShadow: "0 18px 50px rgba(0,0,0,.55)" }}>
          {v.src ? (
            <Img src={staticFile(v.src)} style={{ width: 520, height: 650, objectFit: "cover", objectPosition: "50% 22%", display: "block", filter: "grayscale(1) contrast(1.1)" }} />
          ) : (
            <div style={{ width: 520, height: 650, background: "#333" }} />
          )}
        </div>
      </div>
      <div style={{ position: "absolute", left: 900, top: 330, opacity: k2, transform: `translateX(${(1 - k2) * 40}px)` }}>
        <div style={{ position: "relative", display: "inline-block" }}>
          <div style={{ position: "absolute", left: -10, right: -10, bottom: 6, height: 34, background: C.yellow, transformOrigin: "left", transform: `scaleX(${k2})` }} />
          <div style={{ position: "relative", fontFamily: F.head, fontSize: 130, color: "#fff", textShadow: "0 4px 0 rgba(0,0,0,.4)" }}>{v.name}</div>
        </div>
        <div style={{ fontFamily: F.body, fontWeight: 500, fontSize: 46, color: "#e9e9e9", marginTop: 18 }}>{v.years}</div>
        <div style={{ fontFamily: F.body, fontWeight: 700, fontSize: 46, color: "#e9e9e9", marginTop: 6 }}>{v.role}</div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------- 병력 비교 (아이콘) ---------- */
const DivIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 150 }) => (
  <svg width={size} height={size * 0.72} viewBox="0 0 100 72">
    <circle cx="50" cy="16" r="13" fill={color} />
    <path d="M28 70 C28 44 72 44 72 70 Z" fill={color} />
    <circle cx="20" cy="26" r="10" fill={color} opacity=".85" />
    <path d="M4 70 C4 50 36 50 36 70 Z" fill={color} opacity=".85" />
    <circle cx="80" cy="26" r="10" fill={color} opacity=".85" />
    <path d="M64 70 C64 50 96 50 96 70 Z" fill={color} opacity=".85" />
  </svg>
);

const VersusV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const side = (d: any, base: number, align: string) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 760 }}>
      <div style={{ display: "flex", gap: 26, height: 150, alignItems: "flex-end" }}>
        {Array.from({ length: d.n }).map((_, i) => {
          const k = popIn((t - base - i * 0.25) / 0.35);
          return (
            <div key={i} style={{ transform: `scale(${Math.max(0, k)})`, opacity: clamp(k * 3) }}>
              <DivIcon color={d.color === "red" ? "#e04848" : "#5b8fff"} />
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 34, opacity: clamp((t - base) * 3) }}>
        <CalloutBox text={d.label} style={d.color === "red" ? "red" : "blue"} size={60} />
      </div>
    </div>
  );
  const vsAt = atSec(sc, v.at ?? 0);
  return (
    <AbsoluteFill>
      <Slate />
      <AbsoluteFill style={{ flexDirection: "row", justifyContent: "center", alignItems: "center", paddingBottom: 120, gap: 40 }}>
        {side(v.left, 0.3, "l")}
        <div style={{ fontFamily: F.head, fontSize: 110, color: C.yellow, opacity: clamp((t - vsAt) * 3), transform: `scale(${popIn((t - vsAt) / 0.4)})` }}>VS</div>
        {side(v.right, vsAt + 0.2, "r")}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- 연표 ---------- */
const TimelineV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const n = v.items.length;
  const lineK = easeOut(t / 1.2);
  return (
    <AbsoluteFill>
      <Slate />
      <div style={{ position: "absolute", left: 200, right: 200, top: 470, height: 8, background: "rgba(255,255,255,.25)" }}>
        <div style={{ width: `${lineK * 100}%`, height: "100%", background: C.yellow }} />
      </div>
      {v.items.map((it: any, i: number) => {
        const x = 200 + ((i + 0.5) / n) * 1520;
        const k = popIn((t - atSec(sc, it.at)) / 0.4);
        if (t < atSec(sc, it.at)) return null;
        return (
          <div key={i} style={{ position: "absolute", left: x, top: 474, transform: `translate(-50%,-50%)` }}>
            <div style={{ width: 44, height: 44, borderRadius: 99, background: C.red, border: "6px solid #fff", margin: "0 auto", transform: `scale(${k})` }} />
            <div style={{ position: "absolute", left: "50%", bottom: 70, transform: `translateX(-50%) scale(${k})`, textAlign: "center" }}>
              <CalloutBox text={it.text} style="red" size={70} />
            </div>
            <div style={{ position: "absolute", left: "50%", top: 70, transform: "translateX(-50%)", fontFamily: F.head, fontSize: 56, color: "#fff", whiteSpace: "nowrap", opacity: clamp(k) }}>
              {it.date}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* ---------- 문서(전투상보) ---------- */
const DocumentV: React.FC = () => {
  const v = useScene().visual;
  const t = useT();
  const k = easeOut(t / 0.6);
  const all = v.rows.join("\n");
  const shown = Math.floor(clamp((t - 0.6) / 3.5) * all.length);
  return (
    <AbsoluteFill>
      <Slate dim={0.2} />
      <div
        style={{
          position: "absolute",
          left: 460,
          top: 90,
          width: 1000,
          height: 760,
          background: "linear-gradient(180deg,#ece3cc,#d9cdae)",
          boxShadow: "0 24px 60px rgba(0,0,0,.6)",
          transform: `translateY(${(1 - k) * 80}px) rotate(1deg) scale(${1 + 0.04 * clamp(t / 10)})`,
          opacity: k,
          padding: "60px 70px",
          fontFamily: "'Noto Serif CJK KR', 'Nanum Myeongjo', serif",
          color: "#2a241a",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 30, fontWeight: 700 }}>
          <span>{v.org}</span>
          <span style={{ border: "4px solid #a3261f", color: "#a3261f", padding: "2px 14px", transform: "rotate(-6deg)", fontFamily: F.head }}>軍 秘</span>
        </div>
        <div style={{ textAlign: "center", fontSize: 76, fontWeight: 900, letterSpacing: 18, margin: "36px 0 40px", borderBottom: "3px double #2a241a", paddingBottom: 20 }}>{v.head}</div>
        <div style={{ whiteSpace: "pre-wrap", fontSize: 40, lineHeight: 1.75, fontFamily: "'Courier New', 'Noto Sans KR', monospace", fontWeight: 700 }}>
          {all.slice(0, shown)}
          <span style={{ opacity: Math.floor(t * 3) % 2 ? 1 : 0 }}>▌</span>
        </div>
      </div>
      <div style={{ position: "absolute", left: 470, top: 870, fontFamily: F.body, fontSize: 24, color: "rgba(255,255,255,.7)" }}>※ {v.note}</div>
    </AbsoluteFill>
  );
};

/* ---------- 게이지 (식량·탄약·시간) ---------- */
const GaugesV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  return (
    <AbsoluteFill>
      <Slate />
      <div style={{ position: "absolute", top: 120, left: 0, right: 0, textAlign: "center" }}>
        <Appear pop at={0}>
          <CalloutBox text={v.big} style="yellow" size={120} />
        </Appear>
      </div>
      {v.items.map((it: any, i: number) => {
        const s0 = atSec(sc, it.at);
        const k = t - s0;
        const level = 1 - 0.82 * easeInOut(clamp((t - 0.3) / Math.max(2, sc.dur - 1)));
        return (
          <div key={i} style={{ position: "absolute", left: 360, top: 420 + i * 120, display: "flex", alignItems: "center", gap: 40, opacity: clamp(k * 3) }}>
            <div style={{ width: 190, fontFamily: F.head, fontSize: 64, color: "#fff", textAlign: "right" }}>{it.label}</div>
            <div style={{ width: 900, height: 58, background: "rgba(0,0,0,.45)", border: "4px solid #fff", position: "relative" }}>
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${level * 100}%`, background: level < 0.35 ? C.red : C.yellow }} />
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* ---------- 한자 ---------- */
const HanjaV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const n = v.items.length;
  const per = Math.max(0.6, (sc.lines[0]?.end - sc.lines[0]?.start || 3) / n);
  return (
    <AbsoluteFill>
      <Slate />
      <AbsoluteFill style={{ flexDirection: "row", justifyContent: "center", alignItems: "center", gap: 90, paddingBottom: 120 }}>
        {v.items.map((it: any, i: number) => {
          const s0 = (sc.lines[0]?.start || 0) + i * per;
          const k = popIn((t - s0) / 0.4);
          return (
            <div key={i} style={{ textAlign: "center", opacity: clamp((t - s0) * 4), transform: `scale(${Math.max(0, k)})` }}>
              <div
                style={{
                  width: 300,
                  height: 300,
                  background: i === 1 ? C.red : "#f3f1ea",
                  color: i === 1 ? "#fff" : "#111",
                  fontFamily: "'Noto Serif CJK KR','Noto Serif CJK SC', serif",
                  fontWeight: 900,
                  fontSize: 220,
                  lineHeight: "300px",
                  boxShadow: "0 16px 40px rgba(0,0,0,.5)",
                }}
              >
                {it.h}
              </div>
              <div style={{ fontFamily: F.head, fontSize: 62, color: "#fff", marginTop: 34 }}>{it.r}</div>
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- 4가지 요인 ---------- */
const FactorsV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const s0 = atSec(sc, v.at ?? 0);
  return (
    <AbsoluteFill>
      <Slate />
      <div style={{ position: "absolute", top: 110, left: 0, right: 0, textAlign: "center" }}>
        <Appear pop at={0}>
          <CalloutBox text="1개 사단 vs 3개 사단 — 왜?" style="dark" size={76} />
        </Appear>
      </div>
      <div style={{ position: "absolute", top: 380, left: 140, right: 140, display: "flex", gap: 40 }}>
        {v.items.map((it: string, i: number) => {
          const k = popIn((t - s0 - i * 0.3) / 0.4);
          return (
            <div key={i} style={{ flex: 1, background: "rgba(10,10,12,.72)", border: "4px solid #fff", padding: "34px 10px", textAlign: "center", transform: `scale(${Math.max(0, k)})`, opacity: clamp((t - s0 - i * 0.3) * 4) }}>
              <div style={{ fontFamily: F.head, fontSize: 96, color: C.yellow }}>{i + 1}</div>
              <div style={{ fontFamily: F.head, fontSize: 52, color: "#fff", marginTop: 10 }}>{it}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- 요인 챕터 ---------- */
const ChapterBigV: React.FC = () => {
  const v = useScene().visual;
  const t = useT();
  const k = popIn(t / 0.4);
  const k2 = popIn((t - 0.25) / 0.4);
  return (
    <AbsoluteFill>
      <PhotoOrSlate src={v.src} kb="in" dim={0.55} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", paddingBottom: 100, gap: 26 }}>
        <div style={{ transform: `scale(${Math.max(0, k)})` }}>
          <CalloutBox text={v.num} style="red" size={110} />
        </div>
        <div style={{ transform: `scale(${Math.max(0, k2)})` }}>
          <CalloutBox text={v.title} style="red" size={110} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- 병력 vs 화력 ---------- */
const CompareV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const card = (d: any, s0: number) => {
    const k = popIn((t - s0) / 0.45);
    const col = d.color === "red" ? C.red : C.blue;
    return (
      <div style={{ width: 640, textAlign: "center", opacity: clamp((t - s0) * 3), transform: `scale(${Math.max(0, k)})` }}>
        <div style={{ fontFamily: F.head, fontSize: 60, color: "#fff", marginBottom: 20 }}>{d.title}</div>
        <div style={{ background: "rgba(10,10,12,.7)", border: `6px solid ${col}`, padding: "40px 0" }}>
          <svg width="300" height="200" viewBox="0 0 300 200">
            {d.icon === "crowd"
              ? Array.from({ length: 15 }).map((_, i) => {
                  const x = 30 + (i % 5) * 60,
                    y = 40 + Math.floor(i / 5) * 60;
                  return (
                    <g key={i} fill={col}>
                      <circle cx={x} cy={y} r={13} />
                      <path d={`M${x - 20} ${y + 42} C${x - 20} ${y + 16} ${x + 20} ${y + 16} ${x + 20} ${y + 42} Z`} />
                    </g>
                  );
                })
              : [0, 1].map((i) => (
                  <g key={i} transform={`translate(${30 + i * 140},${40 + i * 40})`} fill={col}>
                    <rect x="0" y="40" width="110" height="26" rx="6" transform="rotate(-22 0 53)" />
                    <circle cx="30" cy="80" r="26" />
                    <rect x="20" y="70" width="90" height="16" />
                  </g>
                ))}
          </svg>
          <div style={{ fontFamily: F.head, fontSize: 110, color: col }}>{d.big}</div>
        </div>
      </div>
    );
  };
  return (
    <AbsoluteFill>
      <Slate />
      <AbsoluteFill style={{ flexDirection: "row", justifyContent: "center", alignItems: "center", gap: 120, paddingBottom: 110 }}>
        {card(v.left, atSec(sc, v.left.at ?? 0) + 0.2)}
        {card(v.right, atSec(sc, v.right.at ?? 0) + 0.1)}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- 막대그래프 ---------- */
const BarsV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const max = Math.max(...v.items.map((i: any) => i.value));
  return (
    <AbsoluteFill>
      <Slate />
      <div style={{ position: "absolute", left: 220, top: 210, width: 1480 }}>
        {v.items.map((it: any, i: number) => {
          const s0 = atSec(sc, it.at) + 0.1;
          const k = easeOut((t - s0) / 1.1);
          const col = it.color === "red" ? C.red : C.blue;
          const w = Math.max(0.02, it.value / max) * 1000 * k;
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", marginBottom: 56, opacity: clamp((t - s0) * 4) }}>
              <div style={{ width: 380, fontFamily: F.head, fontSize: 52, color: "#fff", textAlign: "right", paddingRight: 30 }}>{it.label}</div>
              <div style={{ height: 92, width: w, background: col, boxShadow: "0 6px 18px rgba(0,0,0,.4)" }} />
              <div style={{ fontFamily: F.head, fontSize: 64, color: it.color === "red" ? "#ffb3b3" : "#b9cfff", marginLeft: 26, opacity: clamp((t - s0 - 0.6) * 3) }}>{it.display}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 220, top: 120, fontFamily: F.body, fontWeight: 700, fontSize: 30, color: "rgba(255,255,255,.75)" }}>※ {v.note}</div>
    </AbsoluteFill>
  );
};

/* ---------- 일주일 공세 바 ---------- */
const WeekBarV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  const t = useT();
  const n = v.days.length;
  const s0 = atSec(sc, v.at ?? 0);
  const prog = easeInOut((t - 0.6) / Math.max(2.5, s0 + 2 - 0.6)) * (v.mark + 0.9);
  const cw = 1500 / n;
  return (
    <AbsoluteFill>
      <Slate />
      <div style={{ position: "absolute", top: 110, left: 0, right: 0, textAlign: "center" }}>
        <Appear pop at={0}>
          <CalloutBox text={v.title} style="yellow" size={96} />
        </Appear>
      </div>
      <div style={{ position: "absolute", left: 210, top: 470, width: 1500, height: 110, display: "flex", border: "5px solid #fff" }}>
        {v.days.map((d: string, i: number) => {
          const fill = clamp(prog - i);
          const isHold = v.hold && i >= v.hold[0] && i <= v.hold[1];
          return (
            <div key={i} style={{ width: cw, height: "100%", borderRight: i < n - 1 ? "3px solid rgba(255,255,255,.5)" : "none", position: "relative", background: "rgba(0,0,0,.35)" }}>
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${fill * 100}%`, background: i >= v.mark ? C.red : isHold ? "#d98b2b" : "#9a9a9a" }} />
              <div style={{ position: "absolute", top: 130, width: "100%", textAlign: "center", fontFamily: F.head, fontSize: 42, color: "#fff" }}>{d}</div>
            </div>
          );
        })}
      </div>
      {v.hold && prog > v.hold[0] && (
        <div style={{ position: "absolute", left: 210 + cw * v.hold[0], width: cw * (v.hold[1] - v.hold[0] + 1), top: 380, textAlign: "center", opacity: clamp(prog - v.hold[0]) }}>
          <CalloutBox text={v.holdText} style="dark" size={44} />
        </div>
      )}
      {prog > v.mark && (
        <div style={{ position: "absolute", left: 210 + cw * v.mark + cw / 2, top: 720, transform: `translateX(-50%) scale(${popIn((prog - v.mark) / 0.5)})` }}>
          <CalloutBox text={v.markText} style="red" size={58} />
        </div>
      )}
    </AbsoluteFill>
  );
};

/* ---------- 교훈 문구 ---------- */
const QuotesV: React.FC = () => {
  const sc = useScene();
  const v = sc.visual;
  return (
    <AbsoluteFill>
      <Slate dim={0.15} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 56, paddingBottom: 140 }}>
        <Appear at={0}>
          <div style={{ fontFamily: F.head, fontSize: 64, color: C.yellow }}>용문산 전투가 남긴 교훈</div>
        </Appear>
        {v.items.map((q: any, i: number) => (
          <Appear key={i} at={q.at} extra={0.2}>
            <div style={{ fontFamily: F.head, fontSize: 76, color: "#fff", borderLeft: `14px solid ${C.red}`, paddingLeft: 34 }}>{q.text}</div>
          </Appear>
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Visual: React.FC<{ tl: Timeline }> = ({ tl }) => {
  const v = useScene().visual;
  switch (v.type) {
    case "map":
      return <MapView tl={tl} />;
    case "photo":
      return <PhotoV />;
    case "ai":
      return <AiV />;
    case "text":
      return <TextV />;
    case "black":
      return <BlackV />;
    case "titlecard":
      return <TitleCardV />;
    case "endcard":
      return <EndCardV />;
    case "person":
      return <PersonV />;
    case "versus":
      return <VersusV />;
    case "timeline":
      return <TimelineV />;
    case "document":
      return <DocumentV />;
    case "gauges":
      return <GaugesV />;
    case "hanja":
      return <HanjaV />;
    case "factors":
      return <FactorsV />;
    case "chapterbig":
      return <ChapterBigV />;
    case "compare":
      return <CompareV />;
    case "bars":
      return <BarsV />;
    case "weekbar":
      return <WeekBarV />;
    case "quotes":
      return <QuotesV />;
    default:
      return <Slate />;
  }
};
