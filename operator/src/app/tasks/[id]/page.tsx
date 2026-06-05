"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { MissionTimelineView } from "@/components/timeline/mission-timeline";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function TaskTimelinePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data, isLoading, isError } = useQuery({
    queryKey: ["task-timeline", id],
    queryFn: () => runtimeApi.taskTimeline(id),
  });

  if (isLoading) return <p className="text-odin-muted">Resolving task…</p>;
  if (isError || !data) return <p className="text-rose-400">Task not found in mission graph</p>;

  const status = "status" in data ? String(data.status) : "unknown";
  const goal = "goal" in data ? String(data.goal) : "";

  return (
    <Card>
      <CardHeader title={goal || "Task"} subtitle={`${status} · ${id}`} />
      <CardBody>
        <MissionTimelineView entries={data.entries} traceId={data.trace_id} />
      </CardBody>
    </Card>
  );
}
