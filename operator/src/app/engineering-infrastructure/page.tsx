"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Engineering Infra" subtitle="V3 oversight" endpoint="/runtime/engineering-infrastructure" rootKey="engineering_infrastructure_v3" description="Repository-wide engineering oversight with supervised patch lifecycles." />;
}
