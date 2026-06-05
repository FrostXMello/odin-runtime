/** @type {import('tailwindcss').Config} */
export default {
  content: ["./react/index.html", "./react/src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        odin: {
          bg: "#0a0e17",
          panel: "#111827",
          border: "#1e293b",
          accent: "#38bdf8",
          gold: "#f59e0b",
          muted: "#64748b",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};
