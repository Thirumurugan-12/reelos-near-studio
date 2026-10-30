import React from "react";
import {
  AbsoluteFill,
  Composition,
  interpolate,
  registerRoot,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Glasses, Classroom } from "./story-illustrations";

type Props = {
  template: "document_stack" | "browser_demo" | "glasses" | "classroom";
  title: string;
  body: string;
  accent: string;
  duration: number;
};
const paper = "#f3eee4";

function Backdrop({ accent }: { accent: string }) {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#080808", overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: -160,
          background: `radial-gradient(ellipse at 10% 95%, ${accent}77, transparent 48%), radial-gradient(ellipse at 95% 5%, ${accent}44, transparent 45%)`,
          transform: `rotate(${Math.sin(frame / 50) * 7}deg)`,
        }}
      />
      <svg
        viewBox="0 0 1080 1920"
        style={{ position: "absolute", inset: 0, opacity: 0.28 }}
      >
        <path
          d="M-100 1700 C300 1420 150 2080 900 1700 L1200 1980 L-100 1980Z"
          fill={accent}
        />
        <path
          d="M-100 1630 C300 1350 150 2010 900 1630"
          fill="none"
          stroke={accent}
          strokeWidth="3"
        />
      </svg>
    </AbsoluteFill>
  );
}

function DocumentStack({ title, body, accent }: Props) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {[0, 1, 2].map((i) => {
        const enter = spring({
          frame: frame - i * 5,
          fps,
          config: { damping: 18, stiffness: 130 },
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              width: 650,
              height: 760,
              top: 620,
              left: 215,
              background: paper,
              color: "#171411",
              border: `2px solid ${i === 2 ? accent : "#d4cdc2"}`,
              borderRadius: 10,
              padding: "64px 58px",
              boxShadow: `0 28px 70px #000b`,
              opacity: enter,
              transform: `translate(${(i - 1) * 38}px, ${(1 - enter) * 280 + i * -24}px) rotate(${(i - 1) * 9}deg)`,
            }}
          >
            <div style={{ fontSize: 22, letterSpacing: 5, color: "#766f64" }}>
              AN IDEA WORTH SHARING
            </div>
            <div
              style={{
                height: 2,
                background: "#c9c1b5",
                margin: "28px 0 52px",
              }}
            />
            <svg width="96" height="110" viewBox="0 0 96 110" fill="none">
              <path
                d="M12 4H58L84 30V104H12Z"
                stroke={accent}
                strokeWidth="5"
              />
              <path
                d="M58 4V30H84M28 52H68M28 68H68M28 84H55"
                stroke={accent}
                strokeWidth="5"
              />
            </svg>
            <h2
              style={{
                fontSize: 64,
                lineHeight: 1.05,
                letterSpacing: -3,
                margin: "42px 0 28px",
              }}
            >
              {title}
            </h2>
            <p
              style={{
                fontSize: 29,
                lineHeight: 1.5,
                margin: 0,
                color: "#50483f",
              }}
            >
              {body}
            </p>
            <div
              style={{
                position: "absolute",
                bottom: 55,
                left: 58,
                width: 300,
                height: 8,
                background: accent,
                transform: "rotate(-2deg)",
              }}
            />
          </div>
        );
      })}
    </>
  );
}

function BrowserDemo({ title, body, accent }: Props) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 20 } });
  const typed = Math.floor(
    interpolate(frame, [12, 62], [0, body.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  return (
    <div
      style={{
        position: "absolute",
        left: 76,
        top: 600,
        width: 928,
        height: 790,
        borderRadius: 20,
        border: `3px solid ${accent}`,
        background: "#141414",
        boxShadow: `0 0 80px ${accent}55`,
        overflow: "hidden",
        opacity: enter,
        transform: `translateY(${(1 - enter) * 140}px) rotate(-3deg) scale(${0.94 + enter * 0.06})`,
      }}
    >
      <div
        style={{
          height: 64,
          background: "#212121",
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "0 25px",
          borderBottom: "1px solid #414141",
        }}
      >
        {[accent, "#d5bc77", "#719e82"].map((color) => (
          <div
            key={color}
            style={{
              width: 14,
              height: 14,
              borderRadius: 20,
              background: color,
            }}
          />
        ))}
        <span style={{ marginLeft: 30, fontSize: 21, color: "#aaa" }}>
          your workspace / draft
        </span>
      </div>
      <div style={{ padding: "62px 52px" }}>
        <div style={{ fontSize: 19, letterSpacing: 5, color: accent }}>
          ONE THOUGHT. CLEARLY TOLD.
        </div>
        <h2
          style={{
            fontSize: 67,
            lineHeight: 1.12,
            letterSpacing: -3,
            margin: "36px 0",
            color: paper,
          }}
        >
          {title}
        </h2>
        <div
          style={{
            height: 180,
            padding: "26px 28px",
            background: "#222",
            borderRadius: 12,
            border: "1px solid #454545",
            color: "#d7d3ca",
            fontSize: 30,
            lineHeight: 1.5,
          }}
        >
          {body.slice(0, typed)}
          <span style={{ color: accent, opacity: frame % 20 < 10 ? 1 : 0 }}>
            ▍
          </span>
        </div>
        <div style={{ display: "flex", gap: 12, marginTop: 32 }}>
          {["IDEA", "CLARITY", "IMPACT"].map((word, i) => (
            <div
              key={word}
              style={{
                border: `1px solid ${accent}88`,
                padding: "14px 22px",
                color: paper,
                fontSize: 22,
                opacity: interpolate(frame, [24 + i * 7, 34 + i * 7], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              {word}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Graphic(props: Props) {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const fade = interpolate(
    frame,
    [0, 5, durationInFrames - 6, durationInFrames - 1],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return (
    <AbsoluteFill
      style={{ fontFamily: "DejaVu Sans, Arial, sans-serif", color: paper }}
    >
      <Backdrop accent={props.accent} />
      <AbsoluteFill style={{ opacity: fade }}>
        <div
          style={{
            position: "absolute",
            left: 80,
            top: 160,
            fontSize: 24,
            letterSpacing: 7,
            color: "#aaa",
          }}
        >
          A CLEARER PICTURE
        </div>
        <div
          style={{
            position: "absolute",
            left: 72,
            top: 230,
            right: 72,
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            fontSize: 112,
            letterSpacing: -5,
            lineHeight: 1.05,
            color: props.accent,
          }}
        >
          {props.title}
        </div>
        {props.template === "document_stack" && <DocumentStack {...props} />}
        {props.template === "browser_demo" && <BrowserDemo {...props} />}
        {props.template === "glasses" && <Glasses {...props} />}
        {props.template === "classroom" && <Classroom {...props} />}
        <div
          style={{
            position: "absolute",
            bottom: 145,
            left: 80,
            right: 80,
            display: "flex",
            alignItems: "center",
            gap: 20,
          }}
        >
          <div style={{ width: 48, height: 3, background: props.accent }} />
          <span style={{ fontSize: 22, letterSpacing: 4, color: "#c7c1b7" }}>
            YOUR VOICE. MADE VISIBLE.
          </span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}

const defaults: Props = {
  template: "document_stack",
  title: "Make it clear.",
  body: "One idea can start a conversation.",
  accent: "#F21F2B",
  duration: 3,
};
function Root() {
  return (
    <Composition
      id="GraphicInsert"
      component={Graphic}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={90}
      defaultProps={defaults}
      calculateMetadata={({ props }) => ({
        durationInFrames: Math.max(6, Math.ceil(props.duration * 30)),
      })}
    />
  );
}
registerRoot(Root);
