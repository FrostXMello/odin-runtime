import { useEffect, useState } from "react";
import { ShellBar } from "./shell/ShellBar";
import { WorkspaceGrid } from "./workspace/WorkspaceGrid";
import { ThoughtStream } from "./cognition/ThoughtStream";
import { ReasoningGraph } from "./cognition/ReasoningGraph";
import { streamSync } from "./streaming/StreamSynchronizer";
import { OverlayDock } from "./overlays/OverlayDock";
import { VoiceConsole } from "./voice/VoiceConsole";
import { MemoryExplorer } from "./memory/MemoryExplorer";
import { MissionHud } from "./missions/MissionHud";
import { AgentSocietyView } from "./agents/AgentSocietyView";
import { EvolutionDashboard } from "./evolution/EvolutionDashboard";
import { desktopApi } from "./lib/api";
import type { DesktopMode } from "./shell/modes";
import { FPS_CAPS } from "./shell/modes";
import "./index.css";

export function App() {
  const [mode, setMode] = useState<DesktopMode>("balanced");
  const [thoughts, setThoughts] = useState<string[]>(["Odin desktop ready"]);
  const [agents, setAgents] = useState<string[]>([]);

  useEffect(() => {
    void desktopApi.connect().then(() => desktopApi.startup());
    const wsUrl = import.meta.env.VITE_ODIN_WS ?? "ws://127.0.0.1:8000/api/v1/ws/runtime";
    streamSync.connect(wsUrl);
    return streamSync.subscribe("visualization:runtime", (payload) => {
      setThoughts((prev) => [...prev.slice(-20), JSON.stringify(payload)]);
    });
  }, []);

  const onMode = (m: DesktopMode) => {
    setMode(m);
    void desktopApi.setMode(m);
  };

  return (
    <div className="odin-desktop" data-mode={mode} style={{ ["--fps-cap" as string]: FPS_CAPS[mode] }}>
      <ShellBar mode={mode} onMode={onMode} />
      <main>
        <WorkspaceGrid
          panels={[
            { id: "chat", title: "Chat", content: "Persistent unified conversation" },
            { id: "missions", title: "Missions", content: "Active mission control" },
            { id: "context", title: "Context", content: "Workspace + repo awareness" },
          ]}
        />
        <ThoughtStream lines={thoughts} />
        <ReasoningGraph
          nodes={[{ id: "1", label: "plan" }, { id: "2", label: "act" }]}
          edges={[{ from: "1", to: "2" }]}
        />
        <MissionHud missions={["federation", "patch-review"]} />
        <AgentSocietyView agents={agents.length ? agents : ["planner", "coder"]} />
        <MemoryExplorer threads={["session", "project-odin"]} />
        <EvolutionDashboard sections={["upgrades", "benchmarks", "patches"]} />
        <OverlayDock attached={["mission_hud", "subtitles"]} />
        <VoiceConsole transcript="" pushToTalk={false} onPtt={() => void desktopApi.openWorkspace()} />
      </main>
    </div>
  );
}
