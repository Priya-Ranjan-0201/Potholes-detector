import React from "react";
import { Sun, Moon } from "./Icons";
import { useTheme } from "../context/ThemeContext";

interface ThemeToggleProps {
  className?: string;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = "" }) => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`p-2 rounded-lg bg-[#1E293B] hover:bg-[#283545] border border-[#334155] text-slate-300 hover:text-white transition-all cursor-pointer shadow-sm ${className}`}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label="Toggle light/dark theme"
    >
      {isDark ? <Sun className="w-4 h-4 text-[#FFD200]" /> : <Moon className="w-4 h-4 text-slate-300" />}
    </button>
  );
};
