import React, { useState, useEffect } from "react";
import { api } from "../api/client";

export const Footer: React.FC = () => {
  const [isOnline, setIsOnline] = useState<boolean>(true);

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
    <footer className="mt-auto border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-500 dark:text-slate-400 text-xs py-5">
      <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              isOnline ? "bg-emerald-500" : "bg-rose-500"
            }`}
          />
          <span className="font-semibold text-slate-800 dark:text-slate-200">
            RoadSurvey AI
          </span>
          <span className="text-slate-400 dark:text-slate-500">·</span>
          <span className="text-[11px] text-slate-500 dark:text-slate-400">
            High-Precision Road & Infrastructure Distress Detection
          </span>
        </div>
        <div className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
          Unified Detector · Calibrated Surface Priors · False Alarm Blocker
        </div>
      </div>
    </footer>
  );
};
