import type { Metadata } from "next";
import {
  ColorSchemeScript,
  MantineProvider,
  mantineHtmlProps
} from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import { Notifications } from "@mantine/notifications";
import { Inter } from "next/font/google";
import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import "./design-tokens.css";
import "./globals.css";
import { theme } from "@/lib/theme";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"]
});

export const metadata: Metadata = {
  title: "Kenang — AI Material Quality QC",
  description:
    "AI-powered material quality sorting for Sima Arome. Real-time good/defective grading with a live QC command center.",
  icons: {
    icon: "/Group 12.svg",
    shortcut: "/Group 12.svg",
    apple: "/Group 12.svg",
  },
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" {...mantineHtmlProps}>
      <head>
        <ColorSchemeScript />
        <link rel="icon" href="/Group 12.svg" type="image/svg+xml" />
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width, user-scalable=no"
        />
      </head>
      <body className={inter.variable}>
        <MantineProvider theme={theme} defaultColorScheme="light">
          <ModalsProvider>
            <Notifications position="top-right" />
            {children}
          </ModalsProvider>
        </MantineProvider>
      </body>
    </html>
  );
}
