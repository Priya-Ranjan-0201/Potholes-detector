import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

export const Footer: React.FC = () => {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const { t } = useLanguage();

  useEffect(() => {
    let mounted = true;
    api
      .health()
      .then(() => {
        if (mounted) setIsOnline(true);
      })
      .catch(() => {
        if (mounted) setIsOnline(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <footer className="mt-auto border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-500 dark:text-slate-400 text-xs py-6">
      <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                isOnline ? "bg-emerald-500 shadow-sm" : "bg-rose-500 shadow-sm"
              }`}
              title={isOnline ? "API Online" : "API Offline"}
            />
            <span className="font-heading font-semibold text-slate-800 dark:text-slate-200">
              RoadSurvey AI
            </span>
            <span className="text-[11px] text-slate-400">· Road &amp; Infrastructure Damage Detection</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-1 text-[11px]">
            <Link to="/about" className="hover:text-primary-700 dark:hover:text-primary-400 transition-colors">
              About Project
            </Link>
            <Link to="/benchmarks" className="hover:text-primary-700 dark:hover:text-primary-400 transition-colors">
              Benchmarks
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="hover:text-primary-700 dark:hover:text-primary-400 transition-colors"
            >
              GitHub
            </a>
            <Link to="/about#license" className="hover:text-primary-700 dark:hover:text-primary-400 transition-colors">
              License (AGPL-3.0)
            </Link>
            <Link to="/about#privacy" className="hover:text-primary-700 dark:hover:text-primary-400 transition-colors">
              Privacy
            </Link>
            <Link to="/about#contact" className="hover:text-primary-700 dark:hover:text-primary-400 transition-colors">
              Contact
            </Link>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 dark:border-slate-900 text-center">
          <p className="text-[11px] text-slate-400 dark:text-slate-500 leading-normal">
            {t("footerNotice")}
          </p>
        </div>
      </div>
    </footer>
  );
};
