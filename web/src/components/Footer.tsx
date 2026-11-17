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
    <footer className="mt-auto border-t border-[#283545] bg-[#0B0F14] text-[#94A3B8] text-xs py-5">
      <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              isOnline ? "bg-[#10B981] shadow-sm shadow-emerald-500/50" : "bg-[#FF5A00] shadow-sm shadow-orange-500/50"
            }`}
          />
          <span className="font-bold text-white tracking-wide">
            RoadSurvey AI
          </span>
          <span className="text-[#64748B]">·</span>
          <span className="text-[11px] text-[#CBD5E1]">
            High-Precision Infrastructure Distress &amp; Pothole Detection
          </span>
        </div>
        <div className="text-[11px] font-mono text-[#94A3B8] flex items-center gap-2">
          <span className="text-[#FF5A00] font-bold">YOLO11n-Rescue</span>
          <span>·</span>
          <span className="text-[#FFD200]">Drivable Surface Prior</span>
          <span>·</span>
          <span>False Alarm Blocker</span>
        </div>
      </div>
    </footer>
  );
};
