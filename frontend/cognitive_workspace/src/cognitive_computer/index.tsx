import { CognitionHUD, CognitionPulse, ContinuityTimeline, EnvironmentMap, MemoryField, ReasoningRiver, AttentionSurface } from "./CognitiveComputer";

type Props = { mode: string };

export function CognitiveComputerShell({ mode }: Props) {
  return (
    <section className="cognitive-computer" data-mode={mode}>
      <CognitionHUD tick={1} familiarity={0.42} />
      <MemoryField nodes={["episodic", "semantic", "engineering"]} />
      <ReasoningRiver tokens={["observe", "reason", "assist"]} />
      <AttentionSurface />
      <ContinuityTimeline events={["session restored", "memory linked", "kernel tick"]} />
      <EnvironmentMap zones={["editor", "terminal", "browser"]} />
      <CognitionPulse />
    </section>
  );
}
