"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Stream Throughput" subtitle="Event throughput" endpoint="/runtime/stream-throughput" rootKey="production_observability" description="Stream throughput measurement and batching metrics." />;
}
