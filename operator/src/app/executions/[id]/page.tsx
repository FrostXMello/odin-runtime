"use client";

import { use } from "react";
import { ExecutionDetail } from "@/components/executions/execution-detail";

export default function ExecutionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <ExecutionDetail executionId={id} />;
}
