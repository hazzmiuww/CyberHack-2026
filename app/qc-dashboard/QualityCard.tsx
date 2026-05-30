"use client";

import { useEffect, useState } from "react";
import { Box, Stack, Text } from "@mantine/core";

interface QualityCardProps {
  label: string;
  /** 0..100 */
  percent: number;
  count: number;
  variant: "good" | "bad";
}

const GRADIENTS = {
  good: "linear-gradient(90deg, #2E7D6F 0%, #3D9E8C 100%)",
  bad: "linear-gradient(90deg, #C0544A 0%, #E07068 100%)",
} as const;

/**
 * Quality result card with an animated fill bar.
 * Uses the Kenang design language (teal = good, red = bad).
 */
export function QualityCard({ label, percent, count, variant }: QualityCardProps) {
  const [fill, setFill] = useState(0);

  // Animate the bar from 0 -> percent on mount / when percent changes
  useEffect(() => {
    const t = setTimeout(() => setFill(percent), 100);
    return () => clearTimeout(t);
  }, [percent]);

  return (
    <Box
      style={{
        background: GRADIENTS[variant],
        borderRadius: 16,
        padding: "20px 22px",
        boxShadow: "0 10px 30px rgba(0,0,0,0.12)",
        width: "100%",
      }}
    >
      <Stack gap={10}>
        <Text
          style={{
            color: "rgba(255,255,255,0.85)",
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          {label}
        </Text>

        <Text
          style={{
            color: "#fff",
            fontFamily:
              "var(--ds-font-mono, 'JetBrains Mono', monospace)",
            fontSize: 40,
            fontWeight: 700,
            lineHeight: 1,
          }}
        >
          {Math.round(percent)}%
        </Text>

        {/* Progress track */}
        <Box
          style={{
            background: "rgba(255,255,255,0.25)",
            borderRadius: 999,
            height: 8,
            width: "100%",
            overflow: "hidden",
          }}
        >
          <Box
            style={{
              background: "rgba(255,255,255,0.85)",
              borderRadius: 999,
              height: "100%",
              width: `${fill}%`,
              transition: "width 900ms ease-out",
            }}
          />
        </Box>

        <Text style={{ color: "rgba(255,255,255,0.75)", fontSize: 12 }}>
          {count} item{count === 1 ? "" : "s"} detected
        </Text>
      </Stack>
    </Box>
  );
}
