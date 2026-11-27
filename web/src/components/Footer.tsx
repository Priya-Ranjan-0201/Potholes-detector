import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

export const Footer: React.FC = () => {
  const { t } = useLanguage();
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
    <footer className="mt-auto border-t border-rule bg-surface text-muted text-xs py-4 transition-colors">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
        <div className="flex flex-col sm:flex-row items-center gap-2">
          <div className="flex items-center gap-1.5 font-medium text-text">
            <span
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                isOnline ? "bg-[#10B981]" : "bg-[#D55E00]"
              }`}
            />
            <span className="font-serif font-bold">ScamRoad</span>
          </div>
          <span className="hidden sm:inline text-rule">|</span>
          <p className="text-[12px] text-muted">
            {t("footerNotice") || "Student research project. Not an official government system. Not safety-certified."}
          </p>
        </div>

        <div className="text-[11px] font-mono text-muted flex items-center gap-2">
          <span>YOLO11 + Drivable Mask</span>
          <span>·</span>
          <span>WBF Fusion</span>
          <span>·</span>
          <span>NH-44 Pilot</span>
        </div>
      </div>
    </footer>
  );
};
