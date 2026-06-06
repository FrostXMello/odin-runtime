"""Generate P50 operator pages."""
from pathlib import Path

pages = [
    ("native-os", "Native OS", "Desktop integration", "/runtime/native-os", "native_os", "Tray, notifications, window state, and OS-level focus detection."),
    ("system-intents", "System Intents", "Intent routing", "/runtime/system-intents", "system_intents", "File open/share intents and supervised system dispatch."),
    ("autonomous-loop-v2", "Autonomous Loop V2", "Persistent agent loop", "/runtime/autonomous-loop-v2", "autonomous_loop_v2", "Multi-day task continuity with approval-gated execution."),
    ("long-horizon-planning", "Long Horizon Planning", "Deferred planning", "/runtime/autonomous-loop-v2", "autonomous_loop_v2", "Bounded long-horizon engineering coordination."),
    ("multi-repo", "Multi Repo", "Cross-repo reasoning", "/runtime/engineering-evolution-v2", "engineering_evolution_v2", "Supervised multi-repository architecture reasoning."),
    ("regression-forecast", "Regression Forecast", "Risk forecasting", "/runtime/engineering-evolution-v2", "engineering_evolution_v2", "Regression forecasting with mandatory rollback plans."),
    ("memory-fabric-v2", "Memory Fabric V2", "Semantic memory", "/runtime/memory-fabric-v2", "memory_fabric_v2", "Persistent semantic memory and cross-session linkage."),
    ("context-rehydration", "Context Rehydration", "Session restore", "/runtime/memory-fabric-v2", "memory_fabric_v2", "Replayable engineering sessions and context resurrection."),
    ("deep-focus", "Deep Focus", "Focus sessions", "/runtime/operator-intelligence-v3", "operator_intelligence_v3", "Deep work orchestration with interruption minimization."),
    ("burnout-awareness", "Burnout Awareness", "Fatigue detection", "/runtime/operator-intelligence-v3", "operator_intelligence_v3", "Transparent burnout risk detection and recovery."),
    ("workflow-mentor", "Workflow Mentor", "Adaptive workflows", "/runtime/operator-intelligence-v3", "operator_intelligence_v3", "Personalized workflow strategies with operator override."),
    ("cognitive-recovery", "Cognitive Recovery", "Recovery planning", "/runtime/operator-intelligence-v3", "operator_intelligence_v3", "Cognitive fatigue prevention and recovery plans."),
    ("autonomous-activity", "Autonomous Activity", "Live activity", "/runtime/autonomous-activity", "autonomous_loop_v2", "Live autonomous activity stream across runtimes."),
    ("reasoning-pulse", "Reasoning Pulse", "Live cognition", "/runtime/reasoning-pulse", "cognitive_streams", "Live reasoning pulse with adaptive FPS scaling."),
]

root = Path(__file__).resolve().parent.parent.parent / "operator" / "src" / "app"
tpl = '''"use client";
import {{ DesktopExperiencePanel }} from "@/components/desktop-experience/runtime-panel";
export default function Page() {{
  return <DesktopExperiencePanel title="{title}" subtitle="{sub}" endpoint="{ep}" rootKey="{key}" description="{desc}" />;
}}
'''
for slug, title, sub, ep, key, desc in pages:
    d = root / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "page.tsx").write_text(tpl.format(title=title, sub=sub, ep=ep, key=key, desc=desc), encoding="utf-8")
    print("wrote", slug)
