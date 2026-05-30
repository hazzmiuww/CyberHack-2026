"use client";

import { Box, Text } from "@mantine/core";

/**
 * Kenang wordmark with floating star accents.
 * `k` and `g` in deep indigo, middle letters in medium indigo.
 */
export function KenangLogo({ size = 28 }: { size?: number }) {
  return (
    <Box style={{ position: "relative", display: "inline-block" }}>
      <Text
        component="span"
        style={{
          fontFamily: "var(--ds-font-family)",
          fontWeight: 800,
          fontSize: size,
          lineHeight: 1,
          letterSpacing: "-0.02em",
        }}
      >
        <span style={{ color: "#4A55A2" }}>k</span>
        <span style={{ color: "#7986CB" }}>enan</span>
        <span style={{ color: "#4A55A2" }}>g</span>
      </Text>
      {/* Star accents */}
      <Text
        component="span"
        style={{
          position: "absolute",
          top: -size * 0.35,
          right: -size * 0.5,
          color: "#FFCA28",
          fontSize: size * 0.5,
          lineHeight: 1,
        }}
      >
        ✦
      </Text>
      <Text
        component="span"
        style={{
          position: "absolute",
          top: -size * 0.1,
          right: -size * 0.72,
          color: "#FFA726",
          fontSize: size * 0.32,
          lineHeight: 1,
        }}
      >
        ✦
      </Text>
    </Box>
  );
}
