import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { Documentary } from "./Video";
import { Thumbnail } from "./Thumbnail";
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
