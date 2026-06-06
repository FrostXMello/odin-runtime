import { missionUiPhase, type MissionUiPhase } from "@/components/missions/mission-state";

export type OdinCorePhase =
  | "idle"
  | "listening"
  | "thinking"
  | "executing"
  | "responding"
  | "error"
  | "completed";

export type OdinCoreInput = {
  commandFocused: boolean;
  commandTyping: boolean;
  creating: boolean;
  missionState: string | null;
  missionPhase: MissionUiPhase | null;
  streamEventTick: number;
  hasActiveStream: boolean;
  replayMode: boolean;
};

const THINKING_STATES = new Set(["created", "planning", "planned", "queued", "waiting"]);
const EXECUTING_STATES = new Set(["running", "active", "blocked"]);

export function deriveMissionPhase(state: string | null): MissionUiPhase | null {
  if (!state) return null;
  return missionUiPhase(state);
}

export function deriveOdinCorePhase(input: OdinCoreInput, respondingActive: boolean): OdinCorePhase {
  const state = input.missionState?.toLowerCase() ?? null;

  if (input.creating) return "thinking";
  if (input.commandFocused || input.commandTyping) return "listening";

  if (state === "failed" || state === "cancelled") return "error";
  if (state === "completed") return "completed";
  if (state === "paused") return "executing";

  if (respondingActive && input.hasActiveStream && !input.replayMode) return "responding";

  if (state && THINKING_STATES.has(state)) return "thinking";
  if (state && EXECUTING_STATES.has(state)) return "executing";
  if (input.missionPhase === "running") return "executing";
  if (input.missionPhase === "paused") return "executing";
  if (input.hasActiveStream && !input.replayMode) return "executing";

  return "idle";
}

export function phaseColor(phase: OdinCorePhase): string {
  switch (phase) {
    case "idle":
      return "#6366f1";
    case "listening":
      return "#22d3ee";
    case "thinking":
      return "#38bdf8";
    case "executing":
      return "#22d3ee";
    case "responding":
      return "#67e8f9";
    case "error":
      return "#f43f5e";
    case "completed":
      return "#fcd34d";
  }
}

export function phaseLabel(phase: OdinCorePhase): string {
  switch (phase) {
    case "idle":
      return "Idle";
    case "listening":
      return "Listening";
    case "thinking":
      return "Thinking";
    case "executing":
      return "Executing";
    case "responding":
      return "Responding";
    case "error":
      return "Error";
    case "completed":
      return "Completed";
  }
}
