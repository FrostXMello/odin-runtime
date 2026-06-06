"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Recovery Authorization" subtitle="Supervised rollback authorization" endpoint="/runtime/recovery-authorization" rootKey="operator_veto" description="Recovery chain authorization with veto chain management." />;
}
