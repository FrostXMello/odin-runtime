"use client";

import Link from "next/link";
import { useRuntimeHealth, useRuntimeIntrospection } from "@/lib/hooks/use-runtime-health";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import type { RootCauseFinding } from "@/lib/api/types";
import { isCriticalFinding } from "@/lib/stream/event-filter";

function SeverityBadge({ s }: { s: string }) {
  const v =
    s === "critical" ? "critical" : s === "high" ? "degraded" : ("default" as const);
  return <Badge variant={v}>{s}</Badge>;
}

function FindingCard({ f }: { f: RootCauseFinding }) {
  return (
    <div className="rounded-lg border border-odin-border bg-odin-bg/40 p-4">
      <div className="flex items-center justify-between gap-2">
        <h4 className="font-medium text-slate-200">{f.issue}</h4>
        <SeverityBadge s={f.severity} />
      </div>
      <p className="mt-2 text-sm text-odin-muted">{f.probable_cause}</p>
      <p className="mt-2 text-xs text-emerald-400/90">→ {f.recommended_action}</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {f.affected_components.map((c) => (
          <span key={c} className="rounded bg-odin-border/50 px-1.5 py-0.5 text-[10px] text-slate-400">
            {c}
          </span>
        ))}
      </div>
      {Array.isArray(f.evidence.mission_ids) && (f.evidence.mission_ids as string[]).length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {(f.evidence.mission_ids as string[]).map((mid) => (
            <Link
              key={mid}
              href={`/missions/${mid}`}
              className="font-mono text-[10px] text-odin-cyan hover:underline"
            >
              {mid.slice(0, 12)}…
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function DiagnosticsPanel() {
  const health = useRuntimeHealth();
  const intro = useRuntimeIntrospection();
  const findings = health.data?.root_cause_analysis?.findings ?? intro.data?.diagnostics?.findings ?? [];
  const criticalCount =
    health.data?.root_cause_analysis?.issue_count ??
    findings.filter((f) => isCriticalFinding(f.severity)).length;
  const introData = intro.data?.introspection;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Badge variant={criticalCount > 0 ? "critical" : "default"}>
          {health.data?.root_cause_analysis?.summary ?? "Analyzing…"}
        </Badge>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader title="Executing" subtitle={`${introData?.executing_tasks?.length ?? 0} tasks`} />
          <CardBody className="max-h-40 overflow-auto space-y-1 text-xs">
            {(introData?.executing_tasks ?? []).map((t) => (
              <div key={t.task_id} className="font-mono text-slate-400">
                {t.goal.slice(0, 40)}
              </div>
            ))}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Blocked" subtitle={`${introData?.blocked_tasks?.length ?? 0}`} />
          <CardBody className="max-h-40 overflow-auto space-y-1 text-xs text-rose-300/80">
            {(introData?.blocked_tasks ?? []).map((t) => (
              <div key={t.task_id}>{t.goal.slice(0, 40)}</div>
            ))}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Policy blocked" />
          <CardBody className="max-h-40 overflow-auto space-y-1 text-xs">
            {(introData?.policy_blocked_missions ?? []).map((m) => (
              <Link key={m.mission_id} href={`/missions/${m.mission_id}`} className="block text-amber-400 hover:underline">
                {m.objective.slice(0, 50)}
              </Link>
            ))}
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader
          title="Root cause analysis"
          subtitle={`${criticalCount} critical · ${findings.length} findings`}
        />
        <CardBody className="space-y-3">
          {findings.length === 0 && (
            <p className="text-sm text-odin-muted">Runtime operating within normal parameters</p>
          )}
          {findings
            .filter((f) => isCriticalFinding(f.severity) || f.severity === "high")
            .map((f) => (
            <FindingCard key={f.issue} f={f} />
          ))}
          {findings.length > 0 &&
            findings.filter((f) => isCriticalFinding(f.severity) || f.severity === "high").length === 0 && (
              <p className="text-sm text-odin-muted">
                No critical issues — {findings.length} advisory signal(s) suppressed from this view
              </p>
            )}
        </CardBody>
      </Card>
    </div>
  );
}
