import React from "react";
import { AbsoluteFill, Audio, interpolate, Loop, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { atSec, Timeline } from "./theme";
import { Callouts, ChapterOverlay, Grain, LabelBox, SceneCtx, Subtitles, Vignette } from "./ui";
import { Visual } from "./Visuals";

const SceneAudio: React.FC<{ tl: Timeline; i: number }> = ({ tl, i }) => {
  const sc = tl.scenes[i];
  const fps = tl.fps;
  const has = (id: string) => tl.sfx.includes(id);
  const sfx = [...sc.sfx];
  // 자동 효과음: 강조 박스 등장 → pop, 챕터 → whoosh
  sc.callouts.forEach((c) => sfx.push({ id: "pop", at: c.at, volume: 0.35, _auto: true } as any));
  if (sc.chapter) sfx.push({ id: "whoosh", at: -1, volume: 0.5 } as any);
  return (
    <>
      {sc.audio && (
        <Sequence from={Math.round(sc.audioAt * fps)} layout="none">
          <Audio src={staticFile(sc.audio)} playbackRate={(sc as any).tempo || 1} />
        </Sequence>
      )}
      {sfx
        .filter((s) => has(s.id))
        .map((s, j) => {
          const at = (s as any).sec !== undefined ? (s as any).sec : (s as any).at < 0 ? 0 : atSec(sc, s.at) + ((s as any)._auto ? 0.1 : 0);
          return (
            <Sequence key={j} from={Math.max(0, Math.round(at * fps))} layout="none">
              <Audio src={staticFile(`sfx/${s.id}.mp3`)} volume={s.volume ?? 0.5} />
            </Sequence>
          );
        })}
    </>
  );
};

const Music: React.FC<{ tl: Timeline }> = ({ tl }) => {
  const fps = tl.fps;
  return (
    <>
      {tl.music
        .filter((m) => m.src)
        .map((m) => {
          const len = Math.round(m.dur * fps);
          const fileLen = m.fileDur ? Math.floor(m.fileDur * fps) : len;
          const vol = (f: number) =>
            m.volume * interpolate(f, [0, fps * 1.5, len - fps * 2.5, len], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <Sequence key={m.id} from={Math.round(m.start * fps)} durationInFrames={len} layout="none">
              {fileLen < len ? (
                <Loop durationInFrames={fileLen} layout="none">
                  <Audio src={staticFile(m.src!)} volume={vol} />
                </Loop>
              ) : (
                <Audio src={staticFile(m.src!)} volume={vol} />
              )}
            </Sequence>
          );
        })}
    </>
  );
};

const Flash: React.FC = () => {
  const f = useCurrentFrame();
  if (f > 7) return null;
  return <AbsoluteFill style={{ background: "#fff", opacity: 0.85 * (1 - f / 7) }} />;
};

export const Documentary: React.FC<{ ep: string; tl: Timeline | null }> = ({ tl }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  if (!tl) return <AbsoluteFill style={{ background: "#000" }} />;
  const fps = tl.fps;
  const fadeOut = interpolate(frame, [durationInFrames - fps * 1.2, durationInFrames - 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {tl.scenes.map((sc, i) => {
        const from = Math.round(sc.start * fps);
        const to = i + 1 < tl.scenes.length ? Math.round(tl.scenes[i + 1].start * fps) : durationInFrames;
        const v = sc.visual;
        const credit = v.type === "ai" ? "AI 생성 이미지" : v.type === "photo" || v.type === "person" ? v.credit : null;
        const mapNow = v.type === "map" || ((sc as any).visuals || []).some((x: any) => x.type === "map");
        const noSub = false;
        return (
          <Sequence key={sc.id} from={from} durationInFrames={to - from} name={sc.id}>
            <SceneCtx.Provider value={sc}>
              <Visual tl={tl} />
              {((sc as any).visuals || []).map((v2: any, k: number) => {
                const off = Math.max(0, Math.round(v2.start * fps));
                const shifted = {
                  ...sc,
                  visual: v2,
                  dur: sc.dur - v2.start,
                  lines: sc.lines.map((l) => ({ ...l, start: l.start - v2.start, end: l.end - v2.start })),
                };
                return (
                  <Sequence key={k} from={off} layout="absolute-fill">
                    <SceneCtx.Provider value={shifted as any}>
                      <Visual tl={tl} />
                    </SceneCtx.Provider>
                  </Sequence>
                );
              })}
              <Vignette strength={v.type === "map" ? 0.28 : 0.55} />
              <LabelBox label={mapNow ? null : sc.label} credit={mapNow ? null : credit} />
              <Callouts />
              <ChapterOverlay />
              {!noSub && <Subtitles />}
              {(sc as any).flash && <Flash />}
              <SceneAudio tl={tl} i={i} />
            </SceneCtx.Provider>
          </Sequence>
        );
      })}
      <Music tl={tl} />
      <Grain />
      <AbsoluteFill style={{ background: "#000", opacity: fadeOut }} />
    </AbsoluteFill>
  );
};
