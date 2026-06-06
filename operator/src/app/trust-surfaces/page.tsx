"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Trust Surfaces" subtitle="Operator trust" endpoint="/runtime/trust-surfaces" rootKey="trust_surfaces" description="Transparent operator trust estimation and governance confidence." />;
}
