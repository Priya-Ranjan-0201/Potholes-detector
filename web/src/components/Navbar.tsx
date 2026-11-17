import React, { useState, useRef, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
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
    const interval = setInterval(check, 8000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const isOverviewActive = location.pathname === "/" || location.pathname === "/overview" || location.pathname === "/about";
  const isScannerActive = location.pathname === "/scanner" || location.pathname === "/scan";
  const isReportActive = location.pathname === "/report";

  return (
    <header className="sticky top-0 z-50 w-full bg-[#121820]/95 border-b border-[#283545] shadow-xl backdrop-blur-md select-none">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-3 sm:gap-6">
          {/* Brand Logo & Original Name ScamRoad */}
          <Link to="/" className="flex items-center gap-2.5 shrink-0 group">
            <div className="p-1.5 rounded-lg bg-[#FF5A00] text-white shadow-md shadow-orange-500/20 group-hover:scale-105 transition-transform">
              <Logo showWordmark={false} size="sm" />
            </div>
            <div className="flex flex-col sm:flex-row sm:items-baseline sm:gap-2">
              <span className="font-sans font-black text-lg tracking-tight text-white group-hover:text-[#FFD200] transition-colors">
                ScamRoad
              </span>
              <span className="text-[10px] sm:text-[11px] font-mono font-bold text-[#FFD200] tracking-wide">
                AI Road Vision
              </span>
            </div>
          </Link>

          {/* Center Navigation Bar (Spacious, Never Wrapping) */}
          <nav className="flex items-center p-1 rounded-xl bg-[#0B0F14] border border-[#283545] shadow-inner shrink-0">
            <Link
              to="/"
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold whitespace-nowrap transition-all ${
                isOverviewActive
                  ? "bg-[#FF5A00] text-white shadow-md shadow-orange-500/25 font-extrabold"
                  : "text-slate-300 hover:text-white hover:bg-[#1E293B]"
              }`}
            >
              <span>⚡ Overview</span>
            </Link>

            <Link
              to="/scanner"
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold whitespace-nowrap transition-all ${
                isScannerActive
                  ? "bg-[#FF5A00] text-white shadow-md shadow-orange-500/25 font-extrabold"
                  : "text-slate-300 hover:text-white hover:bg-[#1E293B]"
              }`}
            >
              <span>🛣️ Road Scanner</span>
            </Link>

            <Link
              to="/report"
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold whitespace-nowrap transition-all ${
                isReportActive
                  ? "bg-[#FF5A00] text-white shadow-md shadow-orange-500/25 font-extrabold"
                  : "text-slate-300 hover:text-white hover:bg-[#1E293B]"
              }`}
            >
              <span>📋 Audit Report &amp; PDF</span>
            </Link>
          </nav>

          {/* Right Controls: AI Engine Status + Language + Theme */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {/* AI Engine Status Badge */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono bg-[#1E293B] border border-[#334155] shrink-0">
              <span
                className={`w-2 h-2 rounded-full ${
                  serverHealthy === true
                    ? "bg-[#10B981] animate-pulse"
                    : serverHealthy === false
                    ? "bg-[#FF5A00]"
                    : "bg-[#FFD200]"
                }`}
              />
              <span className="text-[11px] text-white font-medium whitespace-nowrap">
                {serverHealthy === true
                  ? "AI Live (YOLO11n)"
                  : serverHealthy === false
                  ? "Backend Offline"
                  : "Connecting..."}
              </span>
            </div>

            {/* Language Selector */}
            <div className="relative" ref={langDropdownRef}>
              <button
                type="button"
                onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs bg-[#1E293B] hover:bg-[#283545] border border-[#334155] text-white hover:border-[#FF5A00] transition-colors cursor-pointer font-mono"
                title="Switch language"
              >
                <Globe className="w-3.5 h-3.5 text-[#FFD200]" />
                <span className="font-medium hidden sm:inline">{currentOption.nativeName}</span>
              </button>

              {langDropdownOpen && (
                <div className="absolute right-0 mt-1.5 w-40 bg-[#121820] border border-[#334155] rounded-lg shadow-2xl py-1 z-50 text-xs font-mono">
                  {LANGUAGES.map((opt) => (
                    <button
                      key={opt.code}
                      type="button"
                      onClick={() => {
                        setLanguage(opt.code);
                        setLangDropdownOpen(false);
                      }}
                      className={`w-full px-3 py-1.5 text-left flex items-center justify-between hover:bg-[#1E293B] transition-colors cursor-pointer ${
                        language === opt.code
                          ? "text-[#FF5A00] font-bold bg-[#1E293B]"
                          : "text-slate-300"
                      }`}
                    >
                      <span>{opt.nativeName}</span>
                      <span className="text-[10px] text-slate-400 uppercase">{opt.code}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle (Clean Sun/Moon) */}
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
};
