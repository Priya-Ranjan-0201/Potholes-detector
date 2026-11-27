import React, { useState, useRef, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Globe } from "./Icons";
import { useLanguage, LANGUAGES } from "../context/LanguageContext";
import { ThemeToggle } from "./ThemeToggle";
import { api } from "../api/client";

export const Navbar: React.FC = () => {
  const { language, setLanguage, currentOption, t } = useLanguage();
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);
  const [serverHealthy, setServerHealthy] = useState<boolean | null>(null);
  const langDropdownRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

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
    const interval = setInterval(check, 10000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { key: "navHome", path: "/", match: (p: string) => p === "/" || p === "/overview" },
    { key: "navDetect", path: "/detect", match: (p: string) => p === "/detect" || p === "/scanner" || p === "/scan" },
    { key: "navRecords", path: "/records", match: (p: string) => p === "/records" || p === "/report" },
    { key: "navReview", path: "/review", match: (p: string) => p === "/review" },
    { key: "navBenchmarks", path: "/benchmarks", match: (p: string) => p === "/benchmarks" },
    { key: "navMethod", path: "/method", match: (p: string) => p === "/method" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-surface/95 border-b border-rule backdrop-blur-sm select-none transition-colors">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 gap-2 sm:gap-4">
          {/* Brand Logo & Name */}
          <Link to="/" className="flex items-center gap-2 shrink-0 group">
            <span className="font-serif font-bold text-lg tracking-tight text-text">
              ScamRoad
            </span>
            <span className="hidden sm:inline-block text-[11px] font-mono px-1.5 py-0.5 rounded-[4px] bg-accent/15 text-text border border-accent/30 font-medium">
              Pilot
            </span>
          </Link>

          {/* Top Bar Navigation: Home | Detect | Records | Review | Benchmarks | Method */}
          <nav className="flex items-center gap-0.5 sm:gap-1 overflow-x-auto py-1 scrollbar-none" aria-label="Main Navigation">
            {navItems.map((item) => {
              const isActive = item.match(location.pathname);
              return (
                <Link
                  key={item.key}
                  to={item.path}
                  className={`px-2.5 sm:px-3 py-1 rounded-[4px] text-xs font-sans font-medium whitespace-nowrap transition-colors ${
                    isActive
                      ? "bg-text text-bg font-semibold shadow-xs"
                      : "text-muted hover:text-text hover:bg-surface-raised"
                  }`}
                >
                  {t(item.key)}
                </Link>
              );
            })}
          </nav>

          {/* Right Controls: Status + Language + Theme */}
          <div className="flex items-center gap-2 shrink-0">
            {/* System Status Pill */}
            <div
              className="hidden lg:flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[11px] font-mono border border-rule bg-surface-raised text-muted"
              title={serverHealthy === true ? "ML inference service healthy" : "ML inference service disconnected"}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  serverHealthy === true
                    ? "bg-[#10B981]"
                    : serverHealthy === false
                    ? "bg-[#D55E00]"
                    : "bg-[#E8B100]"
                }`}
              />
              <span>{serverHealthy === true ? "ML2 Live" : serverHealthy === false ? "Offline" : "Checking"}</span>
            </div>

            {/* Language Selector */}
            <div className="relative" ref={langDropdownRef}>
              <button
                type="button"
                onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                className="flex items-center gap-1 px-2 py-1 rounded-[4px] text-xs font-mono bg-surface-raised hover:bg-rule/40 border border-rule text-text transition-colors cursor-pointer"
                title="Switch language"
                aria-label="Select language"
              >
                <Globe className="w-3.5 h-3.5 text-muted" />
                <span className="font-medium">{currentOption.nativeName}</span>
              </button>

              {langDropdownOpen && (
                <div className="absolute right-0 mt-1 w-36 bg-surface border border-rule rounded-[4px] shadow-lg py-1 z-50 text-xs font-mono">
                  {LANGUAGES.map((opt) => (
                    <button
                      key={opt.code}
                      type="button"
                      onClick={() => {
                        setLanguage(opt.code);
                        setLangDropdownOpen(false);
                      }}
                      className={`w-full px-3 py-1 text-left flex items-center justify-between hover:bg-surface-raised transition-colors cursor-pointer ${
                        language === opt.code
                          ? "font-bold text-accent bg-surface-raised"
                          : "text-text"
                      }`}
                    >
                      <span>{opt.nativeName}</span>
                      <span className="text-[10px] text-muted uppercase">{opt.code}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
};
