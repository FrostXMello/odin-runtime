export type WorkspaceMode = "minimal" | "operator" | "engineering" | "immersive" | "cinematic";
export type ResourceProfile = "ultra_light" | "balanced" | "immersive" | "cinematic";

export const FPS: Record<ResourceProfile, number> = {
  ultra_light: 15,
  balanced: 30,
  immersive: 45,
  cinematic: 60,
};
