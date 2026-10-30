import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

type Props = { title: string; body: string; accent: string };

export function Glasses({ body, accent }: Props) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 17, stiffness: 120 } });
  return (
    <div
      style={{
        position: "absolute",
        inset: "560px 50px 380px",
        opacity: enter,
        transform: `translateY(${(1 - enter) * 160}px) rotate(${Math.sin(frame / 22) * 4}deg) scale(${0.8 + enter * 0.2})`,
      }}
    >
      <svg
        viewBox="0 0 980 750"
        width="980"
        height="750"
        style={{ filter: `drop-shadow(0 0 30px ${accent}88)` }}
      >
        <defs>
          <linearGradient id="lens" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#f4eee0" stopOpacity=".16" />
            <stop offset="1" stopColor={accent} stopOpacity=".1" />
          </linearGradient>
        </defs>
        <path
          d="M100 270 L45 110 M880 270 L935 110"
          stroke="#ddd5c8"
          strokeWidth="18"
          strokeLinecap="round"
        />
        <rect
          x="90"
          y="250"
          width="340"
          height="265"
          rx="100"
          fill="url(#lens)"
          stroke="#f0e9dd"
          strokeWidth="20"
        />
        <rect
          x="550"
          y="250"
          width="340"
          height="265"
          rx="100"
          fill="url(#lens)"
          stroke="#f0e9dd"
          strokeWidth="20"
        />
        <path
          d="M430 330 Q490 280 550 330"
          fill="none"
          stroke={accent}
          strokeWidth="22"
        />
        <path
          d="M150 285 L285 285 M610 285 L745 285"
          stroke="white"
          strokeOpacity=".45"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {[180, 800].map((x) => (
          <g key={x} transform={`translate(${x} 625) rotate(${frame * 2})`}>
            <path
              d="M-25 0H25M0-25V25M-17-17L17 17M-17 17L17-17"
              stroke={accent}
              strokeWidth="5"
            />
          </g>
        ))}
      </svg>
      <p
        style={{
          fontSize: 44,
          lineHeight: 1.3,
          color: "#e7e0d4",
          textAlign: "center",
          margin: "-40px 100px 0",
        }}
      >
        {body}
      </p>
    </div>
  );
}

export function Classroom({ body, accent }: Props) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 20 } });
  const blur = interpolate(frame, [14, 50], [0, 9], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 80,
        right: 80,
        top: 590,
        height: 850,
        transform: `translateY(${(1 - enter) * 160}px)`,
        opacity: enter,
      }}
    >
      <div
        style={{
          position: "relative",
          height: 490,
          border: "18px solid #64503c",
          background: "#193028",
          borderRadius: 8,
          boxShadow: `0 0 70px ${accent}44`,
          padding: 55,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            fontFamily: "Georgia, serif",
            color: "#dddcd0",
            filter: `blur(${blur}px)`,
            transform: `scale(${1 + frame * 0.0008})`,
            fontSize: 73,
            lineHeight: 1.7,
          }}
        >
          <div>A + B = ?</div>
          <div style={{ fontSize: 52 }}>Today’s lesson</div>
          <div
            style={{
              height: 3,
              background: "#b9beaa",
              width: "80%",
              marginTop: 12,
            }}
          />
          <div
            style={{
              height: 3,
              background: "#b9beaa",
              width: "60%",
              marginTop: 25,
            }}
          />
        </div>
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 18,
            background: "#937658",
          }}
        />
      </div>
      <svg viewBox="0 0 920 230" width="920" height="230">
        <path d="M80 100H840L890 160H30Z" fill="#8f6c4d" />
        <path d="M80 100V205M840 100V205" stroke="#c49d70" strokeWidth="17" />
        <path d="M400 35H520M460-10V80" stroke={accent} strokeWidth="8" />
        <path
          d="M435 55L460 80L485 55"
          fill="none"
          stroke={accent}
          strokeWidth="8"
        />
      </svg>
      <p
        style={{
          color: "#eee6da",
          fontSize: 43,
          lineHeight: 1.3,
          textAlign: "center",
          margin: "0 40px",
        }}
      >
        {body}
      </p>
    </div>
  );
}
