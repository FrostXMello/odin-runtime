"use client";

import { use } from "react";
import { TraceExplorer } from "@/components/traces/trace-explorer";

export default function TracePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <TraceExplorer traceId={id} />;
}
