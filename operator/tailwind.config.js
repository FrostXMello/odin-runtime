/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        odin: {
          bg: "#07090f",
          panel: "#0d111c",
          border: "#1a2236",
          accent: "#3b82f6",
          cyan: "#22d3ee",
          violet: "#8b5cf6",
          amber: "#f59e0b",
          rose: "#f43f5e",
          emerald: "#10b981",
          muted: "#64748b",
        },
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(59, 130, 246, 0.35)",
        panel: "0 4px 24px rgba(0, 0, 0, 0.45)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
