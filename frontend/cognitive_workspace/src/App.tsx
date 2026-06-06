import { useEffect, useState } from "react";
import { AdaptiveShell } from "./shell/AdaptiveShell";
import { CommandPalette } from "./shell/CommandPalette";
import type { ResourceProfile, WorkspaceMode } from "./shell/modes";
import { FPS } from "./shell/modes";
import { DraggablePanels } from "./workspace/DraggablePanels";
import { MissionDock } from "./workspace/MissionDock";
import { MemoryTimeline } from "./memory/MemoryTimeline";
import { AgentInspector } from "./agents/AgentInspector";
import { ThoughtStreamPanel } from "./cognition/ThoughtStreamPanel";
import { VoiceDock } from "./voice/VoiceDock";
import { TokenStream } from "./reasoning/TokenStream";
import { ReasoningGraph } from "./reasoning/ReasoningGraph";
import { AttentionHeatmap } from "./reasoning/AttentionHeatmap";
import {
  AgentConstellation,
  AttentionField,
  MemoryPulse,
  MissionMap,
  VoiceReactiveOverlay,
} from "./immersive/ImmersiveSurfaces";
import { workspaceApi } from "./lib/api";
import "./index.css";

const PANELS = [
  { id: "chat", title: "Chat" },
  { id: "reasoning", title: "Reasoning" },
  { id: "missions", title: "Missions" },
  { id: "agents", title: "Agents" },
  { id: "memory", title: "Memory" },
  { id: "voice", title: "Voice" },
];

export function App() {
  const [mode, setMode] = useState<WorkspaceMode>("operator");
  const [profile] = useState<ResourceProfile>("balanced");
  const [thoughts, setThoughts] = useState<string[]>(["workspace ready"]);
  const [tokens, setTokens] = useState<string[]>([]);

  useEffect(() => {
    void workspaceApi.open(mode);
  }, [mode]);

  const immersive = mode === "immersive" || mode === "cinematic";

  return (
    <div className="cognitive-workspace" data-mode={mode} style={{ ["--fps-cap" as string]: FPS[profile] }}>
      <AdaptiveShell mode={mode} onMode={setMode} />
      <CommandPalette
        onRun={(q) => {
          void workspaceApi.presenceTurn(q).then(() => setThoughts((p) => [...p, q]));
        }}
      />
      <main className={immersive ? "immersive" : ""}>
        <DraggablePanels panels={PANELS} />
        <MissionDock missions={["patch-review", "federation"]} />
        <ThoughtStreamPanel lines={thoughts} />
        <MemoryTimeline events={["checkpoint", "thread-activated", "recall"]} />
        <AgentInspector agents={["planner", "coder", "reviewer"]} />
        <VoiceDock
          onPtt={() => {
            void workspaceApi.renderReasoning("voice command").then((r: { tokens?: string[] }) =>
              setTokens(r.tokens ?? [])
            );
          }}
        />
        <TokenStream tokens={tokens.length ? tokens : ["streaming…"]} />
        <ReasoningGraph nodes={["observe", "plan", "act"]} />
        <AttentionHeatmap cells={[20, 55, 80, 40]} />
        {immersive && (
          <>
            <MissionMap nodes={["m1", "m2"]} />
            <AgentConstellation agents={["a1", "a2", "a3"]} />
            <MemoryPulse />
            <AttentionField />
            <VoiceReactiveOverlay level={0.4} />
          </>
        )}
      </main>
    </div>
  );
}
