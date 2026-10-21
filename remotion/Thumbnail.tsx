import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import "@fontsource/bebas-neue/400.css";
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

/** EP03 백마고지 — A안: 숫자 "주인이 24번 바뀐 고지" */
const BaengmaA: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => {
  const a = ep.replace(/_en$/, "");
  return (
    <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
      <Img src={staticFile(`ep/${a}/ai/human_wave.jpg`)} style={{ position: "absolute", left: -170, top: -40, height: 800, filter: "contrast(1.1) brightness(1.3) saturate(1.1)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0) 26%, rgba(8,8,10,.9) 54%, #08080a 100%)" }} />
      <div style={{ position: "absolute", right: 46, top: 46, textAlign: "right" }}>
        <Tag text={en ? "WHITE HORSE HILL · 1952" : "1952 백마고지 전투"} />
        {en ? (
          <>
            <div style={{ ...big(92, "#fff", "#000", 7), marginTop: 22 }}>ONE HILL CHANGED</div>
            <div style={{ ...big(92, "#fff", "#000", 7), marginTop: 0 }}>HANDS</div>
            <div style={{ ...big(200, C.red, "#fff", 10), marginTop: -8 }}>24 TIMES</div>
          </>
        ) : (
          <>
            <div style={{ ...big(96, "#fff"), marginTop: 22 }}>고지의 주인이</div>
            <div style={{ ...big(230, C.red, "#fff", 12), marginTop: -6 }}>24번</div>
            <div style={{ ...big(96, C.yellow), marginTop: -6 }}>바뀌었다</div>
          </>
        )}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 14, background: C.red }} />
    </AbsoluteFill>
  );
};

/** EP03 백마고지 — B안: 미스터리 "白馬 — 28만 발이 산을 흰 말로" */
const BaengmaB: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => {
  const a = ep.replace(/_en$/, "");
  return (
    <AbsoluteFill style={{ background: "#0b0b0c", overflow: "hidden" }}>
      <Img src={staticFile(`ep/${a}/ai/hill_dawn.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 40%", filter: "contrast(1.1) brightness(1.15)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.25) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,.88) 100%)" }} />
      <div style={{ position: "absolute", left: 52, top: 48, display: "flex", gap: 14 }}>
        {["白", "馬"].map((h, i) => (
          <div key={h} style={{ width: 180, height: 180, background: i === 1 ? C.red : "#f3f1ea", color: i === 1 ? "#fff" : "#111", fontFamily: "'Noto Serif CJK KR','Noto Serif CJK SC', serif", fontWeight: 900, fontSize: 140, lineHeight: "180px", textAlign: "center", boxShadow: "0 12px 30px rgba(0,0,0,.6)" }}>
            {h}
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", right: 46, top: 60 }}>
        <Tag text={en ? "KOREAN WAR · OCT 1952" : "6·25 철원 395고지"} bg={C.red} fg="#fff" size={40} />
      </div>
      <div style={{ position: "absolute", left: 52, bottom: 46 }}>
        {en ? (
          <>
            <div style={{ ...big(120, C.yellow, "#000", 8) }}>280,000 SHELLS</div>
            <div style={{ ...big(78, "#fff", "#000", 7), marginTop: 0 }}>TURNED A HILL INTO A WHITE HORSE</div>
          </>
        ) : (
          <>
            <div style={{ ...big(82, "#fff") }}>포탄 28만 발이</div>
            <div style={{ ...big(116, C.yellow), marginTop: 6 }}>산을 흰 말로 만들었다</div>
          </>
        )}
      </div>
    </AbsoluteFill>
  );
};

/** '격전의 지도' CTR 규칙 썸네일 (EP04~): 실사풍 전용 그림 + 한글 5~7자 1~2줄, 좌측 상단, 우측 하단 비움 */
const ctrText = (size: number, color: string): React.CSSProperties => ({
  fontFamily: "'Black Han Sans', sans-serif",
  fontSize: size,
  lineHeight: 1.0,
  color,
  WebkitTextStroke: "18px #000",
  paintOrder: "stroke fill",
  textShadow: "0 10px 30px rgba(0,0,0,.75)",
  whiteSpace: "nowrap",
  letterSpacing: -2,
});
const CtrThumb: React.FC<{ img: string; lines: [string, string?]; pos?: string; en?: boolean; right?: boolean }> = ({ img, lines, pos = "50% 40%", en, right }) => (
  <AbsoluteFill style={{ background: "#05070c", overflow: "hidden" }}>
    <Img src={staticFile(img)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos, filter: "contrast(1.18) saturate(1.3) brightness(1.08)" }} />
    {/* 좌상단 글자 가독성 + 우하단(재생시간 박스) 쪽은 어둡게 */}
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at ${right ? "82%" : "18%"} 18%, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 45%), linear-gradient(315deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 30%)` }} />
    <div style={{ position: "absolute", ...(right ? { right: 44, textAlign: "right" as const } : { left: 44 }), top: 34 }}>
      <div style={{ ...ctrText(en ? 150 : 178, C.yellow), ...(en ? { fontFamily: "'Oswald', sans-serif", WebkitTextStroke: "14px #000", letterSpacing: 0 } : {}) }}>{lines[0]}</div>
      {lines[1] && <div style={{ ...ctrText(en ? 150 : 178, "#fff"), marginTop: 6, ...(en ? { fontFamily: "'Oswald', sans-serif", WebkitTextStroke: "14px #000", letterSpacing: 0 } : {}) }}>{lines[1]}</div>}
    </div>
  </AbsoluteFill>
);

/* ===== '격전의 지도' 레퍼런스 디자인 시스템 (3단 텍스트 계층) — 한국어판 A안 ===== */
type Seg = [string, "w" | "s" | "r"];
const SEG_COLOR = { w: "#ffffff", s: "#8fd6ff", r: "#ff2a2a" };
type RefDef = { ep: string; mid: Seg[][]; key: string; keyStyle: "red" | "stone" | "yellow"; pos?: string };
/** 영문판(EN) — 압축 영문 공식: 'Battle of' 제외, 지명 + 숫자/핵심 단어만, Bebas Neue */
const REF_EN: Record<string, RefDef> = {
  yongmunsan: { ep: "01", mid: [[["1 REGIMENT", "s"], [" DESTROYED", "w"]], [["3 DIVISIONS", "r"]]], key: "YONGMUNSAN", keyStyle: "red" },
  dabudong: { ep: "02", mid: [[["STAND OR DIE:", "r"]], [["55 DAYS OF HELL", "s"]]], key: "TABU-DONG", keyStyle: "stone" },
  baengma: { ep: "03", mid: [[["LOST AND RETAKEN", "w"]], [["24 TIMES", "r"]]], key: "WHITE HORSE", keyStyle: "red" },
  jipyeong: { ep: "04", mid: [[["360° SURROUNDED", "r"]], [["BY ", "w"], ["4 DIVISIONS", "s"]]], key: "CHIPYONG-NI", keyStyle: "yellow" },
  chuncheon: { ep: "05", mid: [[["THE ONLY VICTORY", "w"]], [["ON DAY 1", "r"]]], key: "CHUNCHEON", keyStyle: "red" },
};
const REF: Record<string, RefDef> = {
  yongmunsan: { ep: "01", mid: [[["중공군 ", "w"], ["3개 사단", "r"], [" 격멸,", "w"]], [["1개 연대의 기적", "s"]]], key: "용문산 전투", keyStyle: "red" },
  dabudong: { ep: "02", mid: [[["대구 함락 직전", "r"], [",", "w"]], [["55일간의 결사항전", "s"]]], key: "다부동 전투", keyStyle: "stone" },
  baengma: { ep: "03", mid: [[["주인이 ", "w"], ["24번", "r"], [" 바뀐", "w"]], [["지옥의 능선", "s"]]], key: "백마고지", keyStyle: "red" },
  jipyeong: { ep: "04", mid: [[["중공군 4개 사단", "r"], [" 완전 포위,", "w"]], [["퇴로는 없다", "s"]]], key: "지평리 전투", keyStyle: "yellow" },
  chuncheon: { ep: "05", mid: [[["개전 첫날 유일한 승리", "r"], [",", "w"]], [["3일간의 기적", "s"]]], key: "춘천 전투", keyStyle: "red" },
};
const CrackDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <defs>
      {/* 갈라진 돌 질감: 거친 노이즈로 글자 면을 부분적으로 깎아 균열·얼룩을 만든다 */}
      <filter id="crack" x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
        {/* 가는 균열선: turbulence 값이 0에 가까운 주름만 투명하게 */}
        <feTurbulence type="turbulence" baseFrequency="0.018 0.03" numOctaves={2} seed={7} result="t" />
        <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  14 0 0 0 -0.35" result="veins" />
        {/* 잔 점박이 마모 */}
        <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={3} result="g" />
        <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  9 0 0 0 -2.2" result="speck" />
        <feComposite in="veins" in2="speck" operator="in" result="mask" />
        <feComposite in="SourceGraphic" in2="mask" operator="in" result="cut" />
        {/* 돌 표면 얼룩 */}
        <feTurbulence type="fractalNoise" baseFrequency="0.12" numOctaves={3} seed={11} result="shade" />
        <feColorMatrix in="shade" type="matrix" values="0.45 0 0 0 0.55  0.45 0 0 0 0.55  0.45 0 0 0 0.55  0 0 0 0 1" result="shadeC" />
        <feBlend in="cut" in2="shadeC" mode="multiply" result="sh" />
        <feComposite in="sh" in2="cut" operator="in" />
      </filter>
    </defs>
  </svg>
);
const KeyWord: React.FC<{ text: string; style: "red" | "stone" | "yellow"; size: number; en?: boolean }> = ({ text, style, size, en }) => {
  const base: React.CSSProperties = { fontFamily: en ? "'Bebas Neue', 'Oswald', sans-serif" : "'Black Han Sans', sans-serif", fontSize: size, lineHeight: 1, whiteSpace: "nowrap", letterSpacing: en ? 1 : -3 };
  const parts = style === "yellow" ? (en ? text.replace("-", " -").split(" ") : text.split(" ")) : [text];
  const fill = (i: number) => (style === "red" ? "#e3161d" : style === "stone" ? "#f1efe8" : i === 0 ? "#ffd21f" : "#ffffff");
  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      {/* 1층: 두꺼운 검은 외곽선 + 그림자 (균열 사이로 비치는 바탕) */}
      <div style={{ ...base, color: "#0a0a0a", WebkitTextStroke: "22px #000", paintOrder: "stroke fill", textShadow: "0 12px 34px rgba(0,0,0,.9), 0 0 3px #000" }}>
        {parts.map((p, i) => (
          <span key={i}>{i && !p.startsWith("-") ? " " : ""}{p}</span>
        ))}
      </div>
      {/* 2층: 색 면 + 크랙/스톤 질감 */}
      <div style={{ ...base, position: "absolute", left: 0, top: 0, filter: "url(#crack)" }}>
        {parts.map((p, i) => (
          <span key={i} style={{ color: fill(i) }}>{i && !p.startsWith("-") ? " " : ""}{p}</span>
        ))}
      </div>
    </div>
  );
};
const RefThumb: React.FC<{ ep: string; en?: boolean }> = ({ ep, en }) => {
  const a = ep.replace(/_en$/, "");
  const d = (en ? REF_EN : REF)[a];
  const keySize = en ? Math.min(230, Math.floor(900 / (d.key.length * 0.46))) : d.key.length <= 4 ? 200 : 168;
  const head = en ? "'Bebas Neue', 'Oswald', sans-serif" : "'Black Han Sans', sans-serif";
  return (
    <AbsoluteFill style={{ background: "#050505", overflow: "hidden" }}>
      <CrackDefs />
      <Img src={staticFile(`ep/${a}/ai/thumb_ref.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: d.pos || "50% 45%", filter: "contrast(1.25) saturate(1.25) brightness(1.02)" }} />
      {/* 아카이브 질감: 비네트 + 좌측·상단 글자 가독성 + 우하단 타임스탬프 영역 어둡게 */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 45%, rgba(0,0,0,0) 35%, rgba(0,0,0,.6) 100%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,.7) 0%, rgba(0,0,0,.25) 45%, rgba(0,0,0,0) 70%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(315deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 28%)" }} />
      <div style={{ position: "absolute", left: 40, top: 30, right: 360 }}>
        {/* 상단: 회색 박스 태그 */}
        <div style={{ display: "inline-block", background: "rgba(225,225,225,.92)", color: "#111", fontFamily: head, fontSize: en ? 40 : 34, padding: "6px 18px 2px", border: "3px solid #fff", boxShadow: "0 6px 16px rgba(0,0,0,.6)", letterSpacing: 1 }}>
          {en ? `MAP OF WAR EP ${d.ep}` : `격전의 지도 EP ${d.ep}`}
        </div>
        {/* 중단: 2색 분할 위기 카피 */}
        <div style={{ marginTop: 18 }}>
          {d.mid.map((line, i) => (
            <div key={i} style={{ fontFamily: head, fontSize: en ? 84 : 66, lineHeight: en ? 1.0 : 1.12, letterSpacing: en ? 1 : 0, whiteSpace: "nowrap", WebkitTextStroke: "12px #000", paintOrder: "stroke fill", textShadow: "0 6px 18px rgba(0,0,0,.85)" }}>
              {line.map(([t, c], j) => (
                <span key={j} style={{ color: SEG_COLOR[c] }}>{t}</span>
              ))}
            </div>
          ))}
        </div>
      </div>
      {/* 하단: 초대형 메인 키워드 (좌측, 우하단 25% 비움) */}
      <div style={{ position: "absolute", left: 30, bottom: 34 }}>
        <KeyWord text={d.key} style={d.keyStyle} size={keySize} en={en} />
      </div>
    </AbsoluteFill>
  );
};

export const Thumbnail: React.FC<{ ep: string; variant: "A" | "B"; lang?: string }> = ({ ep, variant, lang }) => {
  setLang(lang);
  const refKey = ep.replace(/_en$/, "");
  if (variant === "A" && (lang === "en" ? REF_EN : REF)[refKey]) return <RefThumb ep={ep} en={lang === "en"} />;
  if (ep.startsWith("jipyeong")) {
    const a = ep.replace(/_en$/, "");
    const en = lang === "en";
    return variant === "A" ? (
      <CtrThumb img={`ep/${a}/ai/thumb_a.jpg`} lines={en ? ["NO WAY", "OUT"] : ["퇴로는", "없었다"]} pos="35% 35%" en={en} right />
    ) : (
      <CtrThumb img={`ep/${a}/ai/thumb_b.jpg`} lines={en ? ["SURROUNDED", "ON ALL SIDES"] : ["사방이", "적이었다"]} en={en} />
    );
  }
  if (ep.startsWith("baengma")) return variant === "A" ? <BaengmaA ep={ep} en={lang === "en"} /> : <BaengmaB ep={ep} en={lang === "en"} />;
  if (ep.startsWith("dabudong")) return variant === "A" ? <DabuA ep={ep} en={lang === "en"} /> : <DabuB ep={ep} en={lang === "en"} />;
  if (lang === "en") return variant === "A" ? <ThumbA_EN ep={ep} /> : <ThumbB_EN ep={ep} />;
  return variant === "A" ? <ThumbA ep={ep} /> : <ThumbB ep={ep} />;
};
