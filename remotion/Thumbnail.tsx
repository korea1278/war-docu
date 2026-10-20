import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, F, setLang } from "./theme";

const big = (size: number, color: string, stroke = "#000", sw = 10): React.CSSProperties => ({
  fontFamily: F.head,
  fontSize: size,
  lineHeight: 1.02,
  color,
  WebkitTextStroke: `${sw}px ${stroke}`,
  paintOrder: "stroke fill",
  textShadow: "0 8px 24px rgba(0,0,0,.65)",
  whiteSpace: "nowrap",
});

const Tag: React.FC<{ text: string; bg?: string; fg?: string; size?: number }> = ({ text, bg = C.yellow, fg = "#111", size = 44 }) => (
  <div style={{ display: "inline-block", background: bg, color: fg, fontFamily: F.head, fontSize: size, padding: "6px 22px 2px", boxShadow: "0 6px 18px rgba(0,0,0,.5)" }}>{text}</div>
);

/** A안: 숫자 대결 — "1개 사단이 3개 사단을 무너뜨렸다" */
const ThumbA: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/rok_counter.jpg`)} style={{ position: "absolute", left: -160, top: -40, height: 800, filter: "contrast(1.1) saturate(1.1)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 30%, rgba(8,8,10,.92) 58%, #08080a 100%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 25% 60%, rgba(0,0,0,0) 40%, rgba(0,0,0,.55) 100%)" }} />
    <div style={{ position: "absolute", right: 46, top: 52, textAlign: "right" }}>
      <Tag text="1951 용문산 전투" />
      <div style={{ ...big(108, "#fff"), marginTop: 26 }}>1개 사단이</div>
      <div style={{ ...big(150, C.red, "#fff", 12), marginTop: 6 }}>3개 사단을</div>
      <div style={{ ...big(108, C.yellow), marginTop: 6 }}>무너뜨렸다</div>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
  </AbsoluteFill>
);

/** B안: 호수 미스터리 — "破虜湖 / 오랑캐를 깨뜨린 호수" */
const ThumbB: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/photos/s43_photo_0.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(.85) contrast(1.15) brightness(.62)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.15) 0%, rgba(0,0,0,.2) 45%, rgba(0,0,0,.85) 100%)" }} />
    <Img
      src={staticFile(`ep/${ep}/photos/s40_photo_0.jpg`)}
      style={{ position: "absolute", right: 40, top: 40, width: 360, height: 250, objectFit: "cover", border: "8px solid #fff", transform: "rotate(3deg)", filter: "grayscale(1) contrast(1.15)", boxShadow: "0 14px 34px rgba(0,0,0,.6)" }}
    />
    <div style={{ position: "absolute", left: 52, top: 60 }}>
      <div style={{ display: "flex", gap: 14 }}>
        {["破", "虜", "湖"].map((h, i) => (
          <div
            key={h}
            style={{
              width: 190,
              height: 190,
              background: i === 1 ? C.red : "#f3f1ea",
              color: i === 1 ? "#fff" : "#111",
              fontFamily: "'Noto Serif CJK KR','Noto Serif CJK SC', serif",
              fontWeight: 900,
              fontSize: 150,
              lineHeight: "190px",
              textAlign: "center",
              boxShadow: "0 12px 30px rgba(0,0,0,.6)",
            }}
          >
            {h}
          </div>
        ))}
      </div>
    </div>
    <div style={{ position: "absolute", left: 52, bottom: 50 }}>
      <div style={{ ...big(76, "#fff") }}>이 호수 이름이 왜</div>
      <div style={{ ...big(112, C.yellow), marginTop: 8 }}>'오랑캐를 깨뜨린'</div>
      <div style={{ ...big(76, "#fff"), marginTop: 8 }}>호수일까?</div>
    </div>
  </AbsoluteFill>
);

/** 영문 A안: "1 DIVISION vs 3 — AND IT WON" */
const ThumbA_EN: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/rok_counter.jpg`)} style={{ position: "absolute", left: -160, top: -40, height: 800, filter: "contrast(1.1) saturate(1.1)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 30%, rgba(8,8,10,.92) 56%, #08080a 100%)" }} />
    <div style={{ position: "absolute", right: 50, top: 46, textAlign: "right" }}>
      <Tag text="KOREA · MAY 1951" />
      <div style={{ ...big(120, "#fff", "#000", 8), marginTop: 22, letterSpacing: 1 }}>1 DIVISION</div>
      <div style={{ ...big(190, C.red, "#fff", 10), marginTop: -6 }}>VS 3</div>
      <div style={{ ...big(104, C.yellow, "#000", 8), marginTop: -4 }}>AND IT WON</div>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
  </AbsoluteFill>
);

/** 영문 B안: 破虜湖 — "THE LAKE THAT DEFEATED THE INVADERS" */
const ThumbB_EN: React.FC<{ ep: string }> = ({ ep }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/photos/s43_photo_0.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(.85) contrast(1.15) brightness(.62)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.15) 0%, rgba(0,0,0,.2) 40%, rgba(0,0,0,.88) 100%)" }} />
    <Img
      src={staticFile(`ep/${ep}/photos/s40_photo_0.jpg`)}
      style={{ position: "absolute", right: 40, top: 40, width: 360, height: 250, objectFit: "cover", border: "8px solid #fff", transform: "rotate(3deg)", filter: "grayscale(1) contrast(1.15)", boxShadow: "0 14px 34px rgba(0,0,0,.6)" }}
    />
    <div style={{ position: "absolute", left: 52, top: 56, display: "flex", gap: 14 }}>
      {["破", "虜", "湖"].map((h, i) => (
        <div key={h} style={{ width: 170, height: 170, background: i === 1 ? C.red : "#f3f1ea", color: i === 1 ? "#fff" : "#111", fontFamily: "'Noto Serif CJK KR','Noto Serif CJK SC', serif", fontWeight: 900, fontSize: 134, lineHeight: "170px", textAlign: "center", boxShadow: "0 12px 30px rgba(0,0,0,.6)" }}>
          {h}
        </div>
      ))}
    </div>
    <div style={{ position: "absolute", left: 52, bottom: 46 }}>
      <div style={{ ...big(84, "#fff", "#000", 7) }}>THE LAKE THAT</div>
      <div style={{ ...big(118, C.yellow, "#000", 8), marginTop: -2 }}>DEFEATED</div>
      <div style={{ ...big(84, "#fff", "#000", 7), marginTop: -2 }}>THE INVADERS</div>
    </div>
    <div style={{ position: "absolute", right: 50, bottom: 56 }}>
      <Tag text="KOREAN WAR · 1951" bg={C.red} fg="#fff" size={40} />
    </div>
  </AbsoluteFill>
);


/** EP02 다부동 — A안: 백선엽 "내가 물러서면 나를 쏴라" */
const DabuA: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/rok_paik.jpg`)} style={{ position: "absolute", left: -140, top: -40, height: 800, filter: "contrast(1.1) saturate(1.05)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 28%, rgba(8,8,10,.9) 55%, #08080a 100%)" }} />
    <div style={{ position: "absolute", right: 46, top: 50, textAlign: "right" }}>
      <Tag text={en ? "DABU-DONG · AUG 1950" : "1950 다부동 전투"} />
      {en ? (
        <>
          <div style={{ ...big(112, "#fff", "#000", 8), marginTop: 24 }}>"IF I RETREAT,</div>
          <div style={{ ...big(176, C.red, "#fff", 10), marginTop: -4 }}>SHOOT</div>
          <div style={{ ...big(112, C.yellow, "#000", 8), marginTop: -4 }}>ME."</div>
        </>
      ) : (
        <>
          <div style={{ ...big(104, "#fff"), marginTop: 26 }}>"내가 물러서면</div>
          <div style={{ ...big(170, C.red, "#fff", 12), marginTop: 6 }}>나를 쏴라"</div>
          <div style={{ ...big(76, C.yellow), marginTop: 18 }}>대구까지 남은 20km</div>
        </>
      )}
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
  </AbsoluteFill>
);

/** EP02 다부동 — B안: 볼링장 전차전 */
const DabuB: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => (
  <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
    <Img src={staticFile(`ep/${ep}/ai/us_tank.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 30%", filter: "contrast(1.15) brightness(1.25) saturate(1.1)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 35%, rgba(0,0,0,.85) 100%)" }} />
    <div style={{ position: "absolute", left: 52, top: 46 }}>
      <Tag text={en ? "KOREAN WAR · 1950" : "6·25 낙동강 최후 방어선"} bg={C.red} fg="#fff" />
    </div>
    <div style={{ position: "absolute", left: 52, bottom: 48 }}>
      {en ? (
        <>
          <div style={{ ...big(84, "#fff", "#000", 7) }}>NIGHT TANK BATTLE IN</div>
          <div style={{ ...big(124, C.yellow, "#000", 9), marginTop: -2 }}>"THE BOWLING ALLEY"</div>
        </>
      ) : (
        <>
          <div style={{ ...big(84, "#fff") }}>계곡이 함정이 된 밤</div>
          <div style={{ ...big(156, C.yellow), marginTop: 6 }}>'볼링장' 전차전</div>
        </>
      )}
    </div>
  </AbsoluteFill>
);

export const Thumbnail: React.FC<{ ep: string; variant: "A" | "B"; lang?: string }> = ({ ep, variant, lang }) => {
  setLang(lang);
  if (ep.startsWith("dabudong")) return variant === "A" ? <DabuA ep={ep} en={lang === "en"} /> : <DabuB ep={ep} en={lang === "en"} />;
  if (lang === "en") return variant === "A" ? <ThumbA_EN ep={ep} /> : <ThumbB_EN ep={ep} />;
  return variant === "A" ? <ThumbA ep={ep} /> : <ThumbB ep={ep} />;
};
