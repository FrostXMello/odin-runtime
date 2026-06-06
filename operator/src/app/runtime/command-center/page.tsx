"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

const btn = "rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan";

export default function CommandCenterPage() {
  const [command, setCommand] = useState("show failed missions");
  const { data } = useQuery({
    queryKey: ["runtime", "command-center"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/command-center"),
    refetchInterval: 15000,
  });
  const execute = useMutation({
    mutationFn: (cmd: string) =>
      apiFetch<Record<string, unknown>>("/runtime/command-center/execute", {
        method: "POST",
        body: { command: cmd },
      }),
  });
  const actions = (data?.quick_actions as Array<Record<string, string>>) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Command Center</h2>
      <Card>
        <CardHeader title="Natural commands" subtitle="Operator shell" />
        <CardBody className="flex gap-2">
          <input
            className="flex-1 rounded border border-odin-border bg-odin-bg px-2 py-1 text-xs"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
          />
          <button type="button" className={btn} onClick={() => execute.mutate(command)}>Run</button>
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Quick actions" subtitle={`${actions.length} available`} />
      </Card>
    </div>
  );
}
