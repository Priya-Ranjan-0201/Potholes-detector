/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"Inter"',
          '"Plus Jakarta Sans"',
          '-apple-system',
          'BlinkMacSystemFont',
          'sans-serif',
        ],
        heading: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        bg: "var(--bg)",
        "bg-subtle": "var(--bg-subtle)",
        "bg-raised": "var(--bg-raised)",
        surface: "var(--surface)",
        "surface-solid": "var(--surface-solid)",
        border: "var(--border)",
        "border-strong": "var(--border-strong)",
        text: "var(--text)",
        muted: "var(--muted)",
        faint: "var(--faint)",
        primary: {
          DEFAULT: "var(--primary)",
          hover: "var(--primary-hover)",
          contrast: "var(--primary-contrast)",
        },
        sky: {
          accent: "var(--accent-sky)",
        },
        status: {
          success: "var(--success)",
          warn: "var(--warn)",
          danger: "var(--danger)",
          info: "var(--info)",
        },
        severity: {
          minor: "var(--sev-minor)",
          moderate: "var(--sev-moderate)",
          severe: "var(--sev-severe)",
          critical: "var(--sev-critical)",
        },
        theme: {
          canvas: "var(--theme-bg)",
          surface: "var(--theme-surface)",
          surface2: "var(--theme-surface-2)",
          border: "var(--theme-border)",
          text: "var(--theme-text)",
          muted: "var(--theme-muted)",
          primary: "var(--theme-primary)",
        },
      },
    },
  },
  plugins: [],
};
