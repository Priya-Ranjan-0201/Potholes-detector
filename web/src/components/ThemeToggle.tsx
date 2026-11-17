import React, { useState, useRef, useEffect } from "react";
import { Sun, Moon } from "./Icons";
import { useTheme, PaletteTheme } from "../context/ThemeContext";

interface ThemeToggleProps {
  className?: string;
}

const PALETTES: { id: PaletteTheme; label: string; swatch: string }[] = [
  { id: "gauge-green", label: "Gauge & Green", swatch: "#1F6F54" },
  { id: "concrete-blue", label: "Concrete & Blue", swatch: "#1E3A8A" },
];

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = "" }) => {
  const { theme, toggleTheme, palette, setPalette } = useTheme();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const isDark = theme === "dark";

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className={`relative flex items-center gap-1.5 ${className}`} ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="px-2 py-1.5 rounded-md bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white text-xs flex items-center gap-1.5 cursor-pointer shadow-sm"
        title="Choose color palette"
      >
        <span
          className="w-2.5 h-2.5 rounded-full shrink-0"
          style={{
            backgroundColor: palette === "gauge-green" ? "#1F6F54" : "#1E3A8A",
          }}
        />
        <span className="hidden xl:inline text-[11px] font-medium">
          {palette === "gauge-green" ? "Gauge Green" : "Signal Blue"}
        </span>
      </button>

      {dropdownOpen && (
        <div className="absolute right-0 top-full mt-1.5 w-44 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md shadow-lg py-1 z-50 text-xs">
          <div className="px-3 py-1 text-[10px] uppercase tracking-wider font-semibold text-slate-400 font-mono">
            Infrastructure Palette
          </div>
          {PALETTES.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => {
                setPalette(p.id);
                setDropdownOpen(false);
              }}
              className={`w-full px-3 py-1.5 text-left flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer ${
                palette === p.id
                  ? "text-orange-600 dark:text-orange-400 font-semibold bg-orange-50 dark:bg-orange-500/10"
                  : "text-slate-700 dark:text-slate-300"
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.swatch }} />
                <span>{p.label}</span>
              </div>
              {palette === p.id && <span className="text-[10px] font-mono">✓</span>}
            </button>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={toggleTheme}
        className="p-1.5 rounded-md bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer shadow-sm"
        title={isDark ? "Switch to light mode" : "Switch to dark mode"}
        aria-label="Toggle light/dark theme"
      >
        {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
      </button>
    </div>
  );
};

