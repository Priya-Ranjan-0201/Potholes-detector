import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { Globe } from "./Icons";
import { useLanguage, LANGUAGES } from "../context/LanguageContext";
import { ThemeToggle } from "./ThemeToggle";
import { Logo } from "./Logo";
import { api } from "../api/client";

export const Navbar: React.FC = () => {
  const { language, setLanguage, currentOption } = useLanguage();
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);
  const [serverHealthy, setServerHealthy] = useState<boolean | null>(null);
  const langDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (langDropdownRef.current && !langDropdownRef.current.contains(e.target as Node)) {
        setLangDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    let active = true;
    const check = () => {
      api
        .health()
        .then(() => {
          if (active) setServerHealthy(true);
        })
        .catch(() => {
          if (active) setServerHealthy(false);
        });
    };
    check();
    const interval = setInterval(check, 8000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full bg-white/90 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 backdrop-blur-md">
      <div className="w-full max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14 gap-4">
          {/* Brand Logo & Title */}
          <Link to="/" className="flex items-center gap-2.5 shrink-0 select-none">
            <Logo showWordmark={false} size="sm" />
            <div className="flex items-baseline gap-2">
              <span className="font-serif font-bold text-base tracking-tight text-slate-900 dark:text-white">
                RoadSurvey AI
              </span>
              <span className="hidden sm:inline-block text-[11px] font-medium text-slate-500 dark:text-slate-400">
                Road Damage Detector
              </span>
            </div>
          </Link>

          {/* Center Engine Status Badge */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
            <span
              className={`w-2 h-2 rounded-full ${
                serverHealthy === true
                  ? "bg-emerald-500 animate-pulse"
                  : serverHealthy === false
                  ? "bg-rose-500"
                  : "bg-amber-500"
              }`}
            />
            <span className="text-[11px] text-slate-700 dark:text-slate-300">
              {serverHealthy === true
                ? "AI Engine Live (YOLO11n-Rescue)"
                : serverHealthy === false
                ? "Backend Offline"
                : "Connecting..."}
            </span>
          </div>

          {/* Right Controls: Language & Theme */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="relative" ref={langDropdownRef}>
              <button
                type="button"
                onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
                title="Switch language"
              >
                <Globe className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
                <span className="font-medium hidden sm:inline">{currentOption.nativeName}</span>
              </button>

              {langDropdownOpen && (
                <div className="absolute right-0 mt-1.5 w-40 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md shadow-lg py-1 z-50 text-xs">
                  {LANGUAGES.map((opt) => (
                    <button
                      key={opt.code}
                      type="button"
                      onClick={() => {
                        setLanguage(opt.code);
                        setLangDropdownOpen(false);
                      }}
                      className={`w-full px-3 py-1.5 text-left flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer ${
                        language === opt.code
                          ? "text-blue-600 dark:text-blue-400 font-semibold bg-blue-50 dark:bg-blue-500/10"
                          : "text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      <span>{opt.nativeName}</span>
                      <span className="text-[10px] text-slate-400 font-mono uppercase">{opt.code}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
};
