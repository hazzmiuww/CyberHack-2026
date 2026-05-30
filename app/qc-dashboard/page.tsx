"use client";

import {
  ActionIcon,
  Alert,
  Badge,
  Box,
  Group,
  Loader,
  Paper,
  ScrollArea,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
  Tooltip,
} from "@mantine/core";
import {
  IconAlertTriangle,
  IconCheck,
  IconPackage,
  IconRefresh,
  IconStack2,
  IconX,
} from "@tabler/icons-react";
import { useInventory } from "@/lib/qc/use-inventory";
import type { Detection } from "@/lib/qc/types";
import { QualityCard } from "./QualityCard";
import { KenangLogo } from "./KenangLogo";

const BRAND = "#4A55A2";
const BRAND_MUTED = "#7986CB";
const GOOD = "#2E7D6F";
const BAD = "#C0544A";

function timeAgo(date: Date | null): string {
  if (!date) return "—";
  const secs = Math.floor((Date.now() - date.getTime()) / 1000);
  if (secs < 5) return "just now";
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  return `${mins}m ago`;
}

function StatCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  accent: string;
}) {
  return (
    <Paper
      withBorder
      p="md"
      radius="md"
      style={{ borderColor: "rgba(121,134,203,0.25)", background: "#ffffff" }}
    >
      <Group gap="sm" wrap="nowrap">
        <Box
          style={{
            background: `${accent}1a`,
            color: accent,
            borderRadius: 12,
            width: 40,
            height: 40,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {icon}
        </Box>
        <Stack gap={2}>
          <Text style={{ fontSize: 12, color: BRAND_MUTED, fontWeight: 600 }}>
            {label}
          </Text>
          <Text
            style={{
              fontSize: 22,
              fontWeight: 800,
              color: BRAND,
              fontFamily: "var(--ds-font-mono, 'JetBrains Mono', monospace)",
              lineHeight: 1,
            }}
          >
            {value}
          </Text>
        </Stack>
      </Group>
    </Paper>
  );
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function DetectionRow({ d }: { d: Detection }) {
  const isGood = d.item_class === "material_bagus";
  return (
    <Table.Tr>
      <Table.Td
        style={{
          fontFamily: "var(--ds-font-mono, 'JetBrains Mono', monospace)",
          color: "#3949AB",
          fontSize: 13,
        }}
      >
        #{String(d.id).padStart(5, "0")}
      </Table.Td>
      <Table.Td>
        <Badge
          variant="light"
          color={isGood ? "teal" : "red"}
          styles={{
            root: {
              background: isGood ? "rgba(46,125,111,0.12)" : "rgba(192,84,74,0.12)",
              color: isGood ? GOOD : BAD,
            },
          }}
        >
          {isGood ? "bagus" : "rusak"}
        </Badge>
      </Table.Td>
      <Table.Td
        style={{
          fontFamily: "var(--ds-font-mono, 'JetBrains Mono', monospace)",
          fontSize: 13,
          color: BRAND_MUTED,
        }}
      >
        {Math.round(d.confidence_score * 100)}%
      </Table.Td>
      <Table.Td style={{ fontSize: 13, color: BRAND_MUTED }}>{d.camera_id}</Table.Td>
      <Table.Td
        style={{
          fontFamily: "var(--ds-font-mono, 'JetBrains Mono', monospace)",
          fontSize: 12,
          color: "#9aa0c4",
        }}
      >
        {formatTime(d.timestamp)}
      </Table.Td>
    </Table.Tr>
  );
}

export default function QcDashboardPage() {
  const { data, loading, error, lastUpdated, refresh } = useInventory({
    pollMs: 4000,
    limit: 50,
  });

  const total = data?.total ?? 0;
  const good = data?.material_bagus_count ?? 0;
  const bad = data?.material_rusak_count ?? 0;
  const acceptance = data?.acceptance_rate ?? 0;
  const detections = data?.detections ?? [];

  const goodPercent = total > 0 ? (good / total) * 100 : 0;
  const badPercent = total > 0 ? (bad / total) * 100 : 0;

  return (
    <Box
      style={{
        minHeight: "100%",
        background:
          "radial-gradient(ellipse at 60% 0%, #fde8e4 0%, #fdf0ee 45%, #fef9f7 100%)",
      }}
    >
      <Box style={{ maxWidth: 900, margin: "0 auto", padding: "32px 20px 64px" }}>
        <Stack gap="lg">
          {/* Header */}
          <Group justify="space-between" align="flex-start" wrap="nowrap">
            <Stack gap={6}>
              <Group gap="sm" align="center">
                <KenangLogo size={30} />
                <Box
                  style={{
                    width: 1,
                    height: 22,
                    background: "rgba(121,134,203,0.35)",
                  }}
                />
                <Title order={3} style={{ color: BRAND, fontWeight: 800 }}>
                  QC Command Center
                </Title>
              </Group>
              <Text style={{ color: BRAND_MUTED, fontSize: 13 }}>
                Live material quality analysis · Sima Arome
              </Text>
            </Stack>

            <Stack gap={8} align="flex-end">
              {/* LIVE indicator */}
              <Group gap={6} align="center">
                <Box className="qc-live-dot" />
                <Text
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: "0.08em",
                    color: GOOD,
                    fontFamily: "var(--ds-font-mono, 'JetBrains Mono', monospace)",
                  }}
                >
                  LIVE
                </Text>
                <Tooltip label="Refresh now">
                  <ActionIcon
                    variant="subtle"
                    color="indigo"
                    onClick={refresh}
                    aria-label="Refresh data"
                  >
                    {loading ? (
                      <Loader size={14} color={BRAND_MUTED} />
                    ) : (
                      <IconRefresh size={16} color={BRAND_MUTED} />
                    )}
                  </ActionIcon>
                </Tooltip>
              </Group>
              <Text style={{ fontSize: 11, color: "#9aa0c4" }}>
                Updated {timeAgo(lastUpdated)}
              </Text>
            </Stack>
          </Group>

          {error && (
            <Alert
              icon={<IconAlertTriangle size={16} />}
              color="red"
              variant="light"
              title="Backend unavailable"
            >
              {error}
            </Alert>
          )}

          {/* Metric cards */}
          <SimpleGrid cols={{ base: 1, xs: 3 }} spacing="md" className="qc-fade-in">
            <StatCard
              label="Total Scanned"
              value={total}
              icon={<IconStack2 size={20} />}
              accent={BRAND}
            />
            <StatCard
              label="Material Bagus"
              value={good}
              icon={<IconCheck size={20} />}
              accent={GOOD}
            />
            <StatCard
              label="Material Rusak"
              value={bad}
              icon={<IconX size={20} />}
              accent={BAD}
            />
          </SimpleGrid>

          {/* Quality breakdown cards */}
          <SimpleGrid cols={{ base: 1, xs: 2 }} spacing="md">
            <QualityCard
              label="Good Quality"
              percent={goodPercent}
              count={good}
              variant="good"
            />
            <QualityCard
              label="Bad Quality"
              percent={badPercent}
              count={bad}
              variant="bad"
            />
          </SimpleGrid>

          {/* Acceptance rate strip */}
          <Paper
            withBorder
            radius="md"
            p="md"
            style={{ borderColor: "rgba(121,134,203,0.25)", background: "#ffffff" }}
          >
            <Group justify="space-between">
              <Text style={{ color: BRAND_MUTED, fontSize: 13, fontWeight: 600 }}>
                Acceptance Rate
              </Text>
              <Text
                style={{
                  fontFamily: "var(--ds-font-mono, 'JetBrains Mono', monospace)",
                  fontSize: 20,
                  fontWeight: 800,
                  color: acceptance >= 50 ? GOOD : BAD,
                }}
              >
                {Math.round(acceptance)}%
              </Text>
            </Group>
          </Paper>

          {/* Detection log */}
          <Stack gap="xs">
            <Group justify="space-between" align="center">
              <Text style={{ color: BRAND, fontWeight: 800, fontSize: 16 }}>
                Recent Detections
              </Text>
              {detections.length > 0 && (
                <Badge
                  variant="light"
                  styles={{
                    root: {
                      background: "rgba(74,85,162,0.1)",
                      color: BRAND,
                    },
                  }}
                >
                  {detections.length} shown
                </Badge>
              )}
            </Group>
            <Paper
              withBorder
              radius="md"
              style={{ borderColor: "rgba(121,134,203,0.25)", overflow: "hidden", background: "#ffffff" }}
            >
              {detections.length === 0 ? (
                <Stack align="center" gap="sm" p={48}>
                  <Box
                    style={{
                      width: 56,
                      height: 56,
                      borderRadius: 16,
                      background: "rgba(121,134,203,0.1)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <IconPackage size={28} color={BRAND_MUTED} />
                  </Box>
                  <Text ta="center" style={{ color: BRAND_MUTED, fontSize: 14, fontWeight: 600 }}>
                    {loading ? "Loading detections…" : "No detections yet"}
                  </Text>
                  {!loading && (
                    <Text ta="center" style={{ color: "#9aa0c4", fontSize: 12, maxWidth: 280 }}>
                      Run the edge camera (edge_camera.py) to start streaming
                      quality detections into the dashboard.
                    </Text>
                  )}
                </Stack>
              ) : (
                <ScrollArea h={360}>
                  <Table highlightOnHover stickyHeader>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>ID</Table.Th>
                        <Table.Th>Quality</Table.Th>
                        <Table.Th>Confidence</Table.Th>
                        <Table.Th>Camera</Table.Th>
                        <Table.Th>Time</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {detections.map((d) => (
                        <DetectionRow key={d.id} d={d} />
                      ))}
                    </Table.Tbody>
                  </Table>
                </ScrollArea>
              )}
            </Paper>
          </Stack>
        </Stack>
      </Box>
    </Box>
  );
}
