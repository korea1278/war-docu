import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { Documentary } from "./Video";
import { Thumbnail } from "./Thumbnail";
import { MAPT } from "./MapThumb";
import { Timeline } from "./theme";

type Props = { ep: string; tl: Timeline | null };

const calc: CalculateMetadataFunction<Props> = async ({ props }) => {
  const res = await fetch(staticFile(`ep/${props.ep}/timeline.json`));
  const tl: Timeline = await res.json();
  return {
    durationInFrames: Math.max(1, Math.ceil(tl.duration * tl.fps)),
    fps: tl.fps,
    props: { ...props, tl },
  };
};

// 공통 썸네일 표준(MAPT) 에피소드 A안은 1920×1080, 그 밖의 예전 디자인은 1280×720
const thumbCalc: CalculateMetadataFunction<{ ep: string; variant: string }> = ({ props }) => {
  const std = props.variant === "A" && MAPT[props.ep.replace(/_en$/, "")];
  return std ? { width: 1920, height: 1080 } : { width: 1280, height: 720 };
};

export const Root: React.FC = () => (
  <>
  <Composition
    id="Thumbnail"
    component={Thumbnail as any}
    width={1280}
    height={720}
    fps={30}
    durationInFrames={1}
    defaultProps={{ ep: "yongmunsan", variant: "A" }}
    calculateMetadata={thumbCalc as any}
  />
  <Composition
    id="Documentary"
    component={Documentary as any}
    width={1920}
    height={1080}
    fps={30}
    durationInFrames={300}
    defaultProps={{ ep: "yongmunsan", tl: null } as Props}
    calculateMetadata={calc as any}
  />
  </>
);
