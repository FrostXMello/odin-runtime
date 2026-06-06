"""Generate P52 operator pages."""
from pathlib import Path

pages = [
    ("unified-core", "Unified Core", "Orchestration", "/runtime/unified-core/status", "unified_cognitive_core", "Central cognition orchestration loop and runtime synchronization."),
    ("attention", "Attention", "Routing engine", "/runtime/attention", "attention_engine", "Salience scoring, focus weighting, and interruption classification."),
    ("focus-heatmap", "Focus Heatmap", "Attention map", "/runtime/focus-heatmap", "attention_engine", "Live focus heatmap with cognitive pressure estimation."),
    ("cognitive-scheduler", "Cog Scheduler", "Bounded queues", "/runtime/cognitive-scheduler", "cognitive_scheduler", "Cognition budgeting, deferred queues, and overnight orchestration."),
    ("persistent-agents", "Persistent Agents", "SQLite agents", "/runtime/persistent-agents", "persistent_agents", "Supervised persistent agents with memory summaries and objectives."),
    ("runtime-coordination", "Runtime Coord", "Sync layer", "/runtime/runtime-coordination", "runtime_coordination", "Detect overlaps, merge contexts, and resolve priority conflicts."),
    ("cognitive-state", "Cognitive State", "Global state", "/runtime/cognitive-state", "cognitive_state", "Cognitive pressure, operator engagement, and runtime load."),
    ("global-context", "Global Context", "Context rebuild", "/runtime/global-context", "unified_cognitive_core", "Rebuild unified operator context across runtimes."),
    ("cognition-heartbeat", "Cog Heartbeat", "Live pulse", "/runtime/cognition-heartbeat", "unified_cognitive_core", "Global cognition heartbeat and continuity snapshots."),
    ("active-objectives", "Objectives", "Active stack", "/runtime/active-objectives", "unified_cognitive_core", "Active objective stack and task continuity."),
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
