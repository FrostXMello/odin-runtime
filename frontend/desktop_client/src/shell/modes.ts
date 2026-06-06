export type DesktopMode = "compact" | "balanced" | "immersive" | "cinematic";

export const FPS_CAPS: Record<DesktopMode, number> = {
  compact: 15,
  balanced: 30,
  immersive: 45,
  cinematic: 60,
};

export function modeLabel(mode: DesktopMode): string {
  return `${mode} (${FPS_CAPS[mode]} fps cap)`;
}
