import type { MissionSummary } from "@/lib/api/types";

const TERMINAL = new Set(["completed", "failed", "cancelled"]);
const PAUSED = new Set(["paused"]);
const RUNNING = new Set(["running", "active", "planning", "planned", "queued", "waiting", "blocked"]);

export type MissionUiPhase = "running" | "paused" | "failed" | "completed" | "created";

export function missionUiPhase(state: string): MissionUiPhase {
  const s = state.toLowerCase();
  if (TERMINAL.has(s)) {
    return s === "completed" ? "completed" : "failed";
  }
  if (PAUSED.has(s)) return "paused";
  if (RUNNING.has(s) || s === "created") return "running";
  return "created";
}

export function isTerminalState(state: string): boolean {
  return TERMINAL.has(state.toLowerCase());
}

export function streamBorderClass(phase: MissionUiPhase): string {
  switch (phase) {
    case "running":
    case "created":
      return "border-l-odin-cyan";
    case "paused":
      return "border-l-amber-400";
    case "failed":
      return "border-l-rose-500";
    case "completed":
      return "border-l-slate-600 opacity-80";
  }
}

export function phaseLabel(phase: MissionUiPhase): string {
  switch (phase) {
    case "running":
      return "RUNNING";
    case "paused":
      return "PAUSED";
    case "failed":
      return "FAILED";
    case "completed":
      return "COMPLETED";
    case "created":
      return "CREATED";
  }
}

export function splitMissions(missions: MissionSummary[]) {
  const active: MissionSummary[] = [];
  const completed: MissionSummary[] = [];
  for (const m of missions) {
    if (isTerminalState(m.current_state)) completed.push(m);
    else active.push(m);
  }
  return { active, completed };
}

export function outcomeLabel(state: string): "success" | "failure" {
  return state.toLowerCase() === "completed" ? "success" : "failure";
}
