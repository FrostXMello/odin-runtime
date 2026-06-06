"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Regression Forecast" subtitle="Risk forecasting" endpoint="/runtime/engineering-evolution-v2" rootKey="engineering_evolution_v2" description="Regression forecasting with mandatory rollback plans." />;
}
