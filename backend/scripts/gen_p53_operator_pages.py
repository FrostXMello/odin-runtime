"""Generate P53 operator pages."""
from pathlib import Path

pages = [
    ("overnight-cognition", "Overnight Cognition", "Runs while idle", "/runtime/overnight", "overnight_cognition", "Bounded overnight cognition orchestration with low-power scheduling."),
    ("deferred-reasoning", "Deferred Reasoning", "Suspended chains", "/runtime/deferred-reasoning", "deferred_reasoning", "SQLite-backed deferred reasoning persistence and recovery."),
    ("continuity-forecast", "Continuity Forecast", "Tomorrow's work", "/runtime/continuity-forecast", "continuity_forecasting", "Predict bottlenecks, abandoned workflows, and operator focus."),
    ("morning-briefing", "Morning Briefing", "Startup summary", "/runtime/morning-briefing", "morning_briefing", "Executive summary, overnight findings, and focus recommendations."),
    ("cognitive-maintenance", "Cog Maintenance", "Compaction", "/runtime/cognitive-maintenance", "cognitive_maintenance", "Memory consolidation, stream compression, and runtime stabilization."),
    ("idle-engineering", "Idle Engineering", "Passive analysis", "/runtime/idle-engineering/report", "idle_engineering", "Supervised repo analysis with no auto-deploy or patch apply."),
    ("overnight-summary", "Overnight Summary", "Cycle report", "/runtime/overnight/summary", "overnight_cognition", "Overnight cognition cycle summary and checkpoint state."),
    ("unfinished-work", "Unfinished Work", "Abandoned items", "/runtime/unfinished-work", "continuity_forecasting", "Detect abandoned workflows and unfinished priorities."),
    ("reasoning-recovery", "Reasoning Recovery", "Restore chains", "/runtime/reasoning-recovery", "deferred_reasoning", "Restore interrupted reasoning chains and deferred objectives."),
    ("repo-drift", "Repo Drift", "Architecture scan", "/runtime/idle-engineering/report", "idle_engineering", "Passive architecture drift and refactor candidate detection."),
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
