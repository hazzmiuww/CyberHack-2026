"use client";

import { useState } from "react";
import { Box, Text } from "@mantine/core";

/**
 * Kenang brand logo.
 *
 * Renders the official logo image from /public/kenang-logo.png when available.
 * If the image is missing, falls back to a text wordmark with star accents so
 * the dashboard never shows a broken image.
 *
 * Drop the logo file at:  public/kenang-logo.png
 */
export function KenangLogo({ size = 32 }: { size?: number }) {
  const [imgFailed, setImgFailed] = useState(false);

  if (!imgFailed) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src="/Property_1_kenang_logo_-_gradient-removebg-preview.png"
        alt="Kenang"
        height={size}
        style={{ height: size, width: "auto", display: "block" }}
        onError={() => setImgFailed(true)}
      />
    );
  }

  // Text fallback
  return (
    <Box style={{ position: "relative", display: "inline-block" }}>
      <Text
        component="span"
        style={{
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
    </Box>
  );
}
