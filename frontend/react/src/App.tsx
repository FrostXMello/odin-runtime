import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "@/components/Sidebar";
import { StatusBar } from "@/components/StatusBar";
import { AgentGrid } from "@/components/AgentGrid";
import { EventStream } from "@/components/EventStream";
import { WorkflowMonitor } from "@/components/WorkflowMonitor";
import { WorkflowGraph } from "@/components/WorkflowGraph";
import { TaskQueueViewer } from "@/components/TaskQueueViewer";
import { PermissionPanel } from "@/components/PermissionPanel";
import { MemorySearch } from "@/components/MemorySearch";
import { MemoryClusters } from "@/components/MemoryClusters";
import { LogsViewer } from "@/components/LogsViewer";
import { RuntimeHealth } from "@/components/RuntimeHealth";
import { CognitionViewer } from "@/components/CognitionViewer";
import { BrowserSessionViewer } from "@/components/BrowserSessionViewer";
import { WatcherDashboard } from "@/components/WatcherDashboard";
import { CommandPalette } from "@/components/CommandPalette";
import { ConversationTimeline } from "@/components/ConversationTimeline";
import { KnowledgeGraphViewer } from "@/components/KnowledgeGraphViewer";
import { ReflectionReports } from "@/components/ReflectionReports";
import { VoiceSessionConsole } from "@/components/VoiceSessionConsole";
import { SandboxViewer } from "@/components/SandboxViewer";
import { ActiveObjectivesPanel } from "@/components/ActiveObjectivesPanel";
import { ContextTimeline } from "@/components/ContextTimeline";
import { RecommendationCenter } from "@/components/RecommendationCenter";
import { ExecutionIntelligenceDashboard } from "@/components/ExecutionIntelligenceDashboard";
import { LocalModelDashboard } from "@/components/LocalModelDashboard";
import { CollaborationViewer } from "@/components/CollaborationViewer";
import { CognitiveAttentionViewer } from "@/components/CognitiveAttentionViewer";
import { LiveDesktopContext } from "@/components/LiveDesktopContext";
import { ResilienceDashboard } from "@/components/ResilienceDashboard";
import { AgentSocietyMonitor } from "@/components/AgentSocietyMonitor";
import { TrustSecurityCenter } from "@/components/TrustSecurityCenter";
import { KernelStateViewer } from "@/components/KernelStateViewer";
import { useOdinStore } from "@/store/odinStore";
import { api, createEventSource } from "@/lib/api";

const isOverlay = new URLSearchParams(window.location.search).get("mode") === "overlay";

export default function App() {
  const [view, setView] = useState("command");
  const [objective, setObjective] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [chatInput, setChatInput] = useState("");
  const [graphQuery, setGraphQuery] = useState("Heimdall");
  const [graphNodes, setGraphNodes] = useState<Array<Record<string, unknown>>>([]);
  const [lastReflection, setLastReflection] = useState<Record<string, unknown> | null>(null);
  const [cognitiveTimeline, setCognitiveTimeline] = useState<Array<Record<string, unknown>>>([]);
  const [recommendations, setRecommendations] = useState<
    Array<{ id: string; title: string; message: string; category: string }>
  >([]);
  const [reliability, setReliability] = useState<Array<Record<string, unknown>>>([]);
  const [localModelStatus, setLocalModelStatus] = useState<Record<string, unknown> | null>(null);
  const [collabChains, setCollabChains] = useState<
    Array<{ id: string; objective: string; steps: Array<{ agent: string; description: string }> }>
  >([]);
  const [contextInsight, setContextInsight] = useState<string | null>(null);
  const [desktopState, setDesktopState] = useState<Record<string, unknown> | null>(null);
  const [workspaceSummary, setWorkspaceSummary] = useState<Record<string, unknown> | null>(null);
  const [attention, setAttention] = useState<Array<Record<string, unknown>>>([]);
  const [breakers, setBreakers] = useState<Array<Record<string, unknown>>>([]);
  const [societyAgents, setSocietyAgents] = useState<Array<Record<string, unknown>>>([]);
  const [trustDash, setTrustDash] = useState<Record<string, unknown> | null>(null);
  const [computeDash, setComputeDash] = useState<Record<string, unknown> | null>(null);
  const [memTimeline, setMemTimeline] = useState<Array<Record<string, unknown>>>([]);
  const [kernelState, setKernelState] = useState<Record<string, unknown> | null>(null);
  const {
    connected,
    loading,
    error,
    status,
    agents,
    tools,
    workflows,
    tasks,
    permissions,
    events,
    auditLogs,
    cognition,
    runtimeStatus,
    runtimeAgents,
    browserSession,
    memoryClusters,
    watcherInsights,
    fetchAll,
    addEvent,
    submitObjective,
    refreshBrowser,
  } = useOdinStore();

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 8000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  useEffect(() => {
    if (!connected) return;
    const es = createEventSource((e) => addEvent(e));
    return () => es.close();
  }, [connected, addEvent]);

  useEffect(() => {
    if (view === "browser" && connected) refreshBrowser();
  }, [view, connected, refreshBrowser]);

  useEffect(() => {
    if (!connected) return;
    if (view === "cognitive-stream") {
      api.ambient.cognitiveTimeline(40).then((r) => setCognitiveTimeline(r.timeline));
    }
    if (view === "recommendations") {
      api.ambient.recommendations().then(setRecommendations);
    }
    if (view === "execution-intel") {
      api.ambient.reliability().then(setReliability);
    }
    if (view === "local-models") {
      api.ambient.localModels().then(setLocalModelStatus);
    }
    if (view === "collaboration") {
      api.ambient.collaborationChains().then(setCollabChains);
    }
    if (view === "context-timeline") {
      api.contextEngine.get().then((r) => {
        setContextInsight((r.explain as { insight?: string })?.insight ?? null);
      });
      api.ambient.cognitiveTimeline(30).then((r) => setCognitiveTimeline(r.timeline));
    }
    if (view === "live-desktop") api.desktopRuntime.get().then(setDesktopState);
    if (view === "workspace-intel") api.environment.workspaceSummary().then(setWorkspaceSummary);
    if (view === "attention")
      api.environment.liveCognition().then((r) => setAttention(r.attention));
    if (view === "resilience")
      api.environment.resilience().then((r) => setBreakers(r.circuit_breakers));
    if (view === "agent-society")
      api.environment.agentSociety().then((r) => setSocietyAgents(r.agents));
    if (view === "trust") api.environment.trustDashboard().then(setTrustDash);
    if (view === "compute-runtime") api.environment.compute().then(setComputeDash);
    if (view === "memory-timeline")
      api.environment.memoryTimeline(40).then(setMemTimeline);
    if (view === "kernel") api.kernel.state().then(setKernelState);
  }, [view, connected]);

  const handleObjective = async () => {
    if (!objective.trim()) return;
    setSubmitting(true);
    try {
      await submitObjective(objective);
      setObjective("");
    } finally {
      setSubmitting(false);
    }
  };

  const latestWorkflow = workflows.length ? workflows[workflows.length - 1] : null;

  const sendChat = async () => {
    if (!chatInput.trim() || !connected) return;
    setSubmitting(true);
    try {
      const res = await api.conversation.chat(chatInput, chatSessionId ?? undefined, true);
      setChatSessionId(res.session_id);
      setChatMessages((m) => [
        ...m,
        { role: "user", content: chatInput },
        {
          role: "assistant",
          content: `Plan: ${res.plan?.steps?.length ?? 0} steps · ${res.run_status ?? "planned"}`,
        },
      ]);
      if (res.reflection) setLastReflection(res.reflection as Record<string, unknown>);
      setChatInput("");
    } finally {
      setSubmitting(false);
    }
  };

  const searchGraph = async () => {
    const hits = await api.knowledgeGraph.search(graphQuery);
    setGraphNodes(hits);
  };

  if (isOverlay) {
    return <CommandPalette onClose={() => window.close()} />;
  }

  return (
    <div className="flex h-screen bg-odin-bg text-slate-200">
      <Sidebar active={view} onNavigate={setView} />

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-odin-border flex items-center px-6">
          <h2 className="text-lg font-medium capitalize">{view.replace("-", " ")}</h2>
          {loading && <span className="ml-4 text-xs text-odin-muted">Syncing…</span>}
        </header>

        <main className="flex-1 overflow-auto p-6">
          {error && (
            <div className="mb-4 p-4 rounded-lg border border-red-500/30 bg-red-500/10 text-red-300 text-sm">
              {error}
            </div>
          )}

          {view === "command" && (
            <section>
              <div className="rounded-xl border border-odin-border bg-odin-panel p-6 max-w-2xl mb-8">
                <label className="text-sm text-odin-muted block mb-2">Objective</label>
                <textarea
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  rows={3}
                  placeholder="Describe what ODIN should plan and delegate…"
                  className="w-full bg-odin-bg border border-odin-border rounded-lg px-3 py-2 text-sm resize-none"
                  disabled={!connected || submitting}
                />
                <button
                  onClick={handleObjective}
                  disabled={!connected || submitting}
                  className="mt-3 px-4 py-2 rounded-lg bg-odin-accent/20 text-odin-accent text-sm disabled:opacity-40"
                >
                  {submitting ? "Running…" : "Run through ODIN"}
                </button>
              </div>
              <div className="grid lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium mb-3">Live cognition</h3>
                  <CognitionViewer items={cognition.slice(0, 12)} />
                </div>
                <div>
                  <h3 className="text-sm font-medium mb-3">Recent workflows</h3>
                  <WorkflowMonitor workflows={workflows.slice(-3)} />
                </div>
              </div>
            </section>
          )}

          {view === "kernel" && <KernelStateViewer state={kernelState} />}

          {view === "live-desktop" && (
            <div className="space-y-4 max-w-lg">
              <LiveDesktopContext state={desktopState} />
              <button
                onClick={() => api.desktopRuntime.enable(true).then(setDesktopState)}
                className="text-xs px-3 py-1 rounded border border-odin-border text-odin-accent"
              >
                Enable live collector (opt-in)
              </button>
            </div>
          )}

          {view === "workspace-intel" && (
            <div className="max-w-xl text-sm space-y-2">
              {workspaceSummary ? (
                <>
                  <p className="text-odin-accent">{String(workspaceSummary.summary)}</p>
                  <p className="text-odin-muted">Type: {String(workspaceSummary.session_type)}</p>
                  <p>Project: {String(workspaceSummary.primary_project)}</p>
                </>
              ) : (
                <p className="text-odin-muted">Enable context to see workspace intelligence.</p>
              )}
            </div>
          )}

          {view === "attention" && (
            <CognitiveAttentionViewer
              items={attention.map((a) => ({
                message: String(a.message ?? ""),
                priority: String(a.priority ?? ""),
                source: String(a.source ?? ""),
                reason: String(a.reason ?? ""),
              }))}
            />
          )}

          {view === "resilience" && (
            <ResilienceDashboard
              breakers={breakers.map((b) => ({
                name: String(b.name ?? ""),
                state: String(b.state ?? ""),
                failure_count: Number(b.failure_count ?? 0),
              }))}
            />
          )}

          {view === "agent-society" && (
            <AgentSocietyMonitor
              agents={societyAgents.map((a) => ({
                agent_id: String(a.agent_id ?? ""),
                domains: (a.domains as string[]) || [],
                reliability_score: Number(a.reliability_score ?? 0),
              }))}
            />
          )}

          {view === "trust" && <TrustSecurityCenter dashboard={trustDash} />}

          {view === "compute-runtime" && (
            <LocalModelDashboard status={(computeDash?.local_models as Record<string, unknown>) ?? computeDash} />
          )}

          {view === "memory-timeline" && (
            <ContextTimeline
              entries={memTimeline.map((e) => ({
                message: String(e.detail ?? e.type ?? ""),
                source: "memory",
                timestamp: String(e.timestamp ?? ""),
              }))}
            />
          )}

          {view === "context-timeline" && (
            <div className="max-w-2xl space-y-4">
              {contextInsight && (
                <p className="text-sm text-odin-accent border border-odin-border rounded-lg p-3">
                  {contextInsight}
                </p>
              )}
              <button
                onClick={() =>
                  api.contextEngine.update({ enabled: true, application: "ODIN Command Center" })
                }
                className="text-xs px-3 py-1 rounded border border-odin-border text-odin-muted"
              >
                Enable context awareness
              </button>
              <ContextTimeline
                entries={cognitiveTimeline.map((e) => ({
                  message: String(e.message ?? ""),
                  source: String(e.source ?? ""),
                  timestamp: String(e.timestamp ?? ""),
                }))}
              />
            </div>
          )}

          {view === "cognitive-stream" && (
            <ContextTimeline
              entries={cognitiveTimeline.map((e) => ({
                message: String(e.message ?? ""),
                source: String(e.source ?? ""),
                timestamp: String(e.timestamp ?? ""),
              }))}
            />
          )}

          {view === "recommendations" && (
            <RecommendationCenter
              items={recommendations}
              onDismiss={async (id) => {
                await api.ambient.dismissRecommendation(id);
                setRecommendations((r) => r.filter((x) => x.id !== id));
              }}
            />
          )}

          {view === "execution-intel" && (
            <ExecutionIntelligenceDashboard
              scores={reliability.map((s) => ({
                tool_name: String(s.tool_name ?? ""),
                success_rate: Number(s.success_rate ?? 0),
                sample_size: Number(s.sample_size ?? 0),
              }))}
            />
          )}

          {view === "collaboration" && <CollaborationViewer chains={collabChains} />}

          {view === "local-models" && <LocalModelDashboard status={localModelStatus} />}

          {view === "conversation" && (
            <div className="grid lg:grid-cols-2 gap-6 max-w-5xl">
              <div>
                <div className="rounded-xl border border-odin-border bg-odin-panel p-4 mb-4">
                  <textarea
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    rows={2}
                    placeholder="Continue the conversation…"
                    className="w-full bg-odin-bg border border-odin-border rounded-lg px-3 py-2 text-sm"
                    disabled={!connected || submitting}
                  />
                  <button
                    onClick={sendChat}
                    disabled={!connected || submitting}
                    className="mt-2 px-4 py-2 rounded-lg bg-odin-accent/20 text-odin-accent text-sm"
                  >
                    Send
                  </button>
                </div>
                <ConversationTimeline messages={chatMessages} />
              </div>
              <div>
                <h3 className="text-sm font-medium mb-3">Active objectives</h3>
                <ActiveObjectivesPanel objectives={[]} />
              </div>
            </div>
          )}

          {view === "cognition" && <CognitionViewer items={cognition} />}
          {view === "workflows" && (
            <div className="grid lg:grid-cols-2 gap-6">
              <WorkflowGraph workflow={latestWorkflow} />
              <WorkflowMonitor workflows={workflows} />
            </div>
          )}
          {view === "runtime" && (
            <RuntimeHealth status={runtimeStatus} agents={runtimeAgents} />
          )}
          {view === "browser" && <BrowserSessionViewer session={browserSession} />}
          {view === "watchers" && <WatcherDashboard insights={watcherInsights} />}
          {view === "agents" && <AgentGrid agents={agents} />}
          {view === "tasks" && <TaskQueueViewer tasks={tasks} />}
          {view === "events" && <EventStream events={events} />}
          {view === "permissions" && (
            <PermissionPanel requests={permissions} onApproved={fetchAll} />
          )}
          {view === "knowledge" && (
            <div className="max-w-xl space-y-4">
              <div className="flex gap-2">
                <input
                  value={graphQuery}
                  onChange={(e) => setGraphQuery(e.target.value)}
                  className="flex-1 bg-odin-bg border border-odin-border rounded-lg px-3 py-2 text-sm"
                />
                <button
                  onClick={searchGraph}
                  className="px-4 py-2 rounded-lg bg-odin-accent/20 text-odin-accent text-sm"
                >
                  Search graph
                </button>
              </div>
              <KnowledgeGraphViewer nodes={graphNodes} />
            </div>
          )}

          {view === "reflection" && <ReflectionReports report={lastReflection} />}

          {view === "voice" && <VoiceSessionConsole sessions={[]} />}

          {view === "sandbox" && <SandboxViewer snapshots={[]} />}

          {view === "memory" && (
            <div className="space-y-8">
              <MemorySearch />
              <div>
                <h3 className="text-sm font-medium mb-3">Project clusters</h3>
                <MemoryClusters clusters={memoryClusters} />
              </div>
            </div>
          )}
          {view === "logs" && <LogsViewer logs={auditLogs} />}
          {view === "tools" && (
            <ul className="space-y-2 max-w-lg">
              {tools.map((t) => (
                <li key={t.name} className="rounded-lg border border-odin-border bg-odin-panel px-4 py-3 text-sm">
                  <span className="font-mono text-odin-accent">{t.name}</span>
                  <p className="text-odin-muted mt-1">{t.description}</p>
                </li>
              ))}
            </ul>
          )}
        </main>

        <StatusBar
          connected={connected}
          running={status?.running ?? false}
          activeTasks={status?.active_tasks ?? 0}
        />
      </div>
    </div>
  );
}
