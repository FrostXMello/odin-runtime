/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        odin: {
          bg: "#07090f",
          graphite: "#050608",
          panel: "#0d111c",
          border: "#1a2236",
          accent: "#3b82f6",
          cyan: "#22d3ee",
          violet: "#8b5cf6",
          amber: "#d4a853",
          rose: "#e87986",
          emerald: "#34d399",
          muted: "#64748b",
          glass: "rgba(13, 17, 28, 0.72)",
          "glass-strong": "rgba(10, 14, 22, 0.85)",
        },
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(59, 130, 246, 0.35)",
        panel: "0 4px 24px rgba(0, 0, 0, 0.45)",
        "odin-glow": "0 0 60px -20px rgba(34, 211, 238, 0.25)",
        "odin-command": "0 8px 32px -8px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255,255,255,0.04)",
        "odin-orb": "0 24px 48px -12px rgba(34, 211, 238, 0.15)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "breath-field": "breath-field 4s cubic-bezier(0.22, 1, 0.36, 1) infinite",
        "pulse-bar": "pulse-bar 2s cubic-bezier(0.22, 1, 0.36, 1) infinite",
        "flicker-accent": "flicker-accent 3s ease-in-out infinite",
      },
      keyframes: {
        "breath-field": {
          "0%, 100%": { opacity: "0.35", transform: "scale(1)" },
          "50%": { opacity: "0.55", transform: "scale(1.04)" },
        },
        "pulse-bar": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "0.9" },
        },
        "flicker-accent": {
          "0%, 100%": { opacity: "0.3" },
          "50%": { opacity: "0.6" },
        },
      },
      transitionTimingFunction: {
        intelligence: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
};
