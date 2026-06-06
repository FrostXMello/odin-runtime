"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Architecture Forecast" subtitle="Long horizon" endpoint="/runtime/engineering-infrastructure" rootKey="engineering_infrastructure_v3" description="Long-horizon architecture forecasting with approval checkpoints." />;
}
