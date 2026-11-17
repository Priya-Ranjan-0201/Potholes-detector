import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  CheckCircle,
  RefreshCw,
  Maximize2,
  Minimize2,
  Camera,
  UploadCloud,
  Eye,
  EyeOff,
  FileText,
} from "../components/Icons";
import { useInspection } from "../context/InspectionContext";
import { ScanLine, BoxOverlay } from "../motion";

type InputMode = "image" | "camera";

const formatDefectTitle = (label: string) => {
  const upper = (label || "").toUpperCase();
  if (upper.includes("ALLIGATOR")) return "Alligator Crack";
  if (upper.includes("LONGITUDINAL")) return "Longitudinal Crack";
  if (upper.includes("TRANSVERSE")) return "Transverse Crack";
  if (upper.includes("CRACK")) return "Road Crack";
  return "Pothole";
};

const getSeverityBadge = (severity?: string) => {
  switch (severity) {
    case "Critical":
      return {
        label: "Critical",
        cls: "bg-[#FF5A00]/20 text-[#FF5A00] border-[#FF5A00]/50 font-bold",
      };
    case "Severe":
    case "High":
      return {
        label: "Severe",
        cls: "bg-[#FFD200]/20 text-[#FFD200] border-[#FFD200]/50 font-semibold",
      };
    case "Moderate":
      return {
        label: "Moderate",
        cls: "bg-yellow-500/20 text-yellow-300 border-yellow-400/40 font-medium",
      };
    default:
      return {
        label: "Minor",
        cls: "bg-slate-700/40 text-slate-300 border-slate-600 font-normal",
      };
  }
};

export const RoadScannerPage: React.FC = () => {
  const {
    activeImageSrc,
    activeRoadName,
    activeChainage,
    preset,
    confThresh,
    inspection,
    isScanning,
    scanStage,
    selectedBoxId,
    hoveredBoxId,
    showBoxes,
    setPreset,
    setConfThresh,
    setShowBoxes,
    setSelectedBoxId,
    setHoveredBoxId,
    handleFileUpload,
    runDetection,
  } = useInspection();

  const [inputMode, setInputMode] = useState<InputMode>("image");
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (inputMode === "camera") {
      navigator.mediaDevices
        ?.getUserMedia({ video: { facingMode: "environment" } })
        .then((stream) => {
          streamRef.current = stream;
          if (videoRef.current) videoRef.current.srcObject = stream;
        })
        .catch((err) => console.warn("Camera unavailable:", err));
    } else if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }

    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, [inputMode]);

  const captureFrameAndScan = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) runDetection(blob);
      });
    }
  };

  return (
    <div className="space-y-5">
      {/* 1. Highway Roadwork HUD Header */}
      <div className="bg-[#121820] border-2 border-[#283545] rounded-xl p-4 sm:p-5 shadow-2xl relative overflow-hidden">
        {/* Road Hazard Caution Top Stripe */}
        <div
          className="absolute top-0 left-0 right-0 h-2"
          style={{
            backgroundImage:
              "repeating-linear-gradient(45deg, #FF5A00, #FF5A00 14px, #0B0F14 14px, #0B0F14 28px)",
          }}
        />

        <div className="flex flex-wrap items-center justify-between gap-4 pt-1">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#FF5A00] text-white tracking-widest uppercase flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                PAGE 1 · ROAD DAMAGE SCANNER
              </span>
              <span className="text-xs font-mono font-bold text-[#FFD200] flex items-center gap-1">
                🛣️ HIGHWAY DISTRESS HUD
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-white mt-1.5 flex items-center gap-2.5">
              <span>Road Pavement &amp; Infrastructure Distress Scanner</span>
            </h1>
            <p className="text-xs text-[#94A3B8] mt-0.5 font-mono">
              Bituminous surface audit with AI vehicle occlusion guards &amp; drivable surface mask.
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            <label className="px-4 py-2.5 rounded-lg text-xs font-bold bg-[#FF5A00] hover:bg-[#E04F00] text-white transition-all shadow-lg hover:shadow-orange-500/20 cursor-pointer flex items-center gap-2 active:scale-95 border border-[#FF7324]">
              <UploadCloud className="w-4 h-4 text-white" />
              <span>Upload Road Photo</span>
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onClick={(e) => {
                  (e.target as HTMLInputElement).value = "";
                }}
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFileUpload(f);
                }}
              />
            </label>

            <button
              type="button"
              onClick={() => setInputMode(inputMode === "camera" ? "image" : "camera")}
              className={`px-3.5 py-2.5 rounded-lg text-xs font-mono font-bold border transition-all cursor-pointer flex items-center gap-1.5 ${
                inputMode === "camera"
                  ? "bg-[#FFD200] text-[#0B0F14] border-[#FFD200] shadow-md"
                  : "bg-[#1E293B] border-[#334155] text-white hover:bg-[#283545]"
              }`}
            >
              <Camera className="w-4 h-4" />
              <span>{inputMode === "camera" ? "Photo Mode" : "Camera"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Main 2-Column Asphalt Inspection Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left: Road Canvas */}
        <div className="lg:col-span-8 bg-[#121820] border-2 border-[#283545] rounded-xl p-4 space-y-3.5 shadow-xl relative">
          <div className="flex items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2 truncate">
              <span className="w-2.5 h-2.5 rounded-full bg-[#FF5A00] animate-pulse" />
              <span className="font-bold text-white truncate text-sm">
                {activeRoadName}
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded bg-[#1E293B] text-[10px] font-mono text-[#FFD200] border border-[#334155]">
                {activeChainage}
              </span>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setShowBoxes(!showBoxes)}
                className="px-2.5 py-1.5 rounded-md border border-[#334155] bg-[#1E293B] text-[#94A3B8] hover:text-white cursor-pointer flex items-center gap-1.5 font-mono text-xs transition-colors"
              >
                {showBoxes ? <Eye className="w-3.5 h-3.5 text-[#FF5A00]" /> : <EyeOff className="w-3.5 h-3.5" />}
                <span>{showBoxes ? "Hide Markers" : "Show Markers"}</span>
              </button>

              <button
                type="button"
                onClick={() => setIsFullscreen(true)}
                className="p-1.5 rounded-md border border-[#334155] bg-[#1E293B] text-[#94A3B8] hover:text-white cursor-pointer transition-colors"
                title="Fullscreen View"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Canvas Container with Asphalt Road Texture & Markings */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              e.stopPropagation();
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.stopPropagation();
              const f = e.dataTransfer.files?.[0];
              if (f) handleFileUpload(f);
            }}
            className="relative min-h-[380px] max-h-[500px] bg-[#090D12] rounded-lg overflow-hidden flex items-center justify-center border-2 border-[#1E293B] shadow-inner"
          >
            {inputMode === "camera" ? (
              <div className="relative w-full h-full flex flex-col items-center justify-center p-4">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full max-h-[420px] object-contain rounded"
                />
                <canvas ref={canvasRef} className="hidden" />
                <button
                  type="button"
                  onClick={captureFrameAndScan}
                  className="mt-3 px-5 py-2.5 rounded-lg bg-[#FF5A00] hover:bg-[#E04F00] text-white text-xs font-bold cursor-pointer flex items-center gap-2 shadow-lg"
                >
                  <Camera className="w-4 h-4" />
                  <span>Scan Road Frame</span>
                </button>
              </div>
            ) : (
              <div className="relative w-full h-[460px] flex items-center justify-center select-none">
                {/* HUD Road Badge Overlay */}
                <div className="absolute top-3 right-3 z-20 px-3 py-1.5 rounded-md bg-[#0B0F14]/90 border border-[#334155] text-white text-xs font-mono font-medium pointer-events-none flex items-center gap-2 max-w-[85%] shadow-md backdrop-blur-sm">
                  <span
                    className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                      inspection.error
                        ? "bg-rose-500 animate-pulse"
                        : inspection.boxes.length > 0
                        ? "bg-[#FF5A00]"
                        : "bg-emerald-400"
                    }`}
                  />
                  <span className="truncate">
                    {isScanning
                      ? "AI Scanning Road Surface..."
                      : inspection.error
                      ? "Inspection Notice"
                      : inspection.boxes.length > 0
                        ? `${inspection.potholeCount} Potholes · ${inspection.crackCount} Cracks`
                        : "Clean Road Section"}
                  </span>
                </div>

                <div className="relative inline-block leading-none max-w-full max-h-full">
                  <img
                    src={activeImageSrc}
                    alt={activeRoadName}
                    className="block max-w-full select-none"
                    style={{ maxHeight: "460px", width: "auto", height: "auto" }}
                  />
                  <ScanLine isScanning={isScanning} stage={scanStage} />
                  {showBoxes && (
                    <BoxOverlay
                      detections={inspection.boxes.slice(0, 25)}
                      activeId={hoveredBoxId ?? selectedBoxId}
                      onHover={(id) => setHoveredBoxId(id)}
                      onSelect={(id) => setSelectedBoxId((prev) => (prev === id ? null : id))}
                      viewMode="boxes"
                    />
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sensitivity & Presets Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-[#94A3B8] pt-2.5 border-t border-[#283545]">
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-xs uppercase text-[#94A3B8] font-bold">Preset:</span>
              <button
                type="button"
                onClick={() => {
                  setPreset("high_precision");
                  setConfThresh(0.40);
                }}
                className={`px-2.5 py-1 rounded-md text-xs font-mono transition-all cursor-pointer ${
                  preset === "high_precision"
                    ? "bg-[#FF5A00] text-white font-bold shadow-sm"
                    : "bg-[#1E293B] hover:bg-[#334155] text-slate-300"
                }`}
                title="High Precision (conf >= 0.40): lowest false alarms"
              >
                High Precision
              </button>
              <button
                type="button"
                onClick={() => {
                  setPreset("balanced");
                  setConfThresh(0.25);
                }}
                className={`px-2.5 py-1 rounded-md text-xs font-mono transition-all cursor-pointer ${
                  preset === "balanced"
                    ? "bg-[#FF5A00] text-white font-bold shadow-sm"
                    : "bg-[#1E293B] hover:bg-[#334155] text-slate-300"
                }`}
                title="Balanced (conf >= 0.25): optimal F1 across all defect types"
              >
                Balanced
              </button>
              <button
                type="button"
                onClick={() => {
                  setPreset("high_recall");
                  setConfThresh(0.15);
                }}
                className={`px-2.5 py-1 rounded-md text-xs font-mono transition-all cursor-pointer ${
                  preset === "high_recall"
                    ? "bg-[#FF5A00] text-white font-bold shadow-sm"
                    : "bg-[#1E293B] hover:bg-[#334155] text-slate-300"
                }`}
                title="High Recall (conf >= 0.15): catches faint distress"
              >
                High Recall
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-medium text-white font-mono">Sensitivity:</span>
              <input
                type="range"
                min="0.10"
                max="0.80"
                step="0.05"
                value={confThresh}
                onChange={(e) => setConfThresh(parseFloat(e.target.value))}
                className="w-20 cursor-pointer accent-[#FF5A00]"
              />
              <span className="font-mono font-bold text-[#FFD200] w-8">
                {Math.round(confThresh * 100)}%
              </span>
            </div>

            <div className="flex items-center gap-2 font-mono text-[11px] text-[#94A3B8]">
              <span className="px-1.5 py-0.5 rounded bg-orange-950/40 text-[#FF5A00] border border-orange-800/60 font-bold">
                YOLO11n-Rescue
              </span>
              <span>·</span>
              <span className="text-white font-medium">Guards Active</span>
              <span>·</span>
              <span>{(inspection.latencyMs / 1000).toFixed(2)}s</span>
            </div>
          </div>
        </div>

        {/* Right: Roadside Detection Console */}
        <div className="lg:col-span-4 bg-[#121820] border-2 border-[#283545] rounded-xl overflow-hidden flex flex-col shadow-xl">
          {/* Top 3 Road Distress Stats */}
          <div className="grid grid-cols-3 divide-x divide-[#283545] border-b border-[#283545] text-center py-3.5 bg-[#161F2A]">
            <div>
              <div className="text-[11px] text-[#94A3B8] font-bold uppercase tracking-wider font-mono">Potholes</div>
              <div className="text-2xl font-bold text-[#FF5A00] font-mono mt-0.5">
                {inspection.potholeCount}
              </div>
            </div>
            <div>
              <div className="text-[11px] text-[#94A3B8] font-bold uppercase tracking-wider font-mono">Cracks</div>
              <div className="text-2xl font-bold text-[#FFD200] font-mono mt-0.5">
                {inspection.crackCount}
              </div>
            </div>
            <div>
              <div className="text-[11px] text-[#94A3B8] font-bold uppercase tracking-wider font-mono">Pavement</div>
              <div
                className={`text-sm font-bold mt-1 font-mono ${
                  inspection.error
                    ? "text-rose-400"
                    : inspection.boxes.length === 0
                      ? "text-emerald-400"
                      : inspection.maxSeverity === "Critical"
                        ? "text-[#FF5A00]"
                        : "text-[#FFD200]"
                }`}
              >
                {inspection.error
                  ? "Notice"
                  : inspection.boxes.length === 0
                    ? "Good"
                    : inspection.maxSeverity}
              </div>
            </div>
          </div>

          {/* Scrollable Defect List */}
          <div className="divide-y divide-[#1E293B] max-h-[340px] overflow-y-auto [scrollbar-width:thin]">
            {inspection.boxes.length > 0 ? (
              inspection.boxes.map((b, idx) => {
                const isSelected = selectedBoxId === b.id;
                const badge = getSeverityBadge(b.severity);
                return (
                  <div
                    key={b.id}
                    onMouseEnter={() => setHoveredBoxId(b.id)}
                    onMouseLeave={() => setHoveredBoxId(null)}
                    className={`w-full text-left px-3.5 py-2.5 space-y-1.5 text-xs transition-colors ${
                      isSelected
                        ? "bg-[#1E293B] border-l-4 border-[#FF5A00]"
                        : "hover:bg-[#18212C]"
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedBoxId((prev) => (prev === b.id ? null : b.id))}
                      className="w-full flex items-center justify-between gap-2 cursor-pointer text-left"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-[#64748B] font-mono w-5 shrink-0">#{idx + 1}</span>
                        <span className="font-bold text-white truncate">
                          {formatDefectTitle(b.label)}
                        </span>
                        <span className={`font-mono text-[10px] px-1.5 py-0.5 rounded border ${badge.cls}`}>
                          {badge.label}
                        </span>
                      </div>

                      <span className="font-mono text-[#FFD200] shrink-0 font-bold">
                        {Math.round(b.confidence * 100)}%
                      </span>
                    </button>

                    {isSelected && (
                      <div className="pt-2 border-t border-[#283545] space-y-1 text-[11px] text-[#94A3B8]">
                        <div className="flex justify-between font-mono">
                          <span>Pavement Area:</span>
                          <span className="text-white">{b.area_pct ? `${b.area_pct}%` : `${b.areaPx} px`}</span>
                        </div>
                        {b.wheelPathRisk && (
                          <div className="flex justify-between font-mono text-[#FF5A00] font-bold">
                            <span>Wheel Path Risk:</span>
                            <span>CRITICAL HAZARD</span>
                          </div>
                        )}
                        <p className="text-[11px] italic text-[#CBD5E1] bg-[#090D12] p-2 rounded border border-[#283545]">
                          {b.severity_breakdown || "Localized road pavement distress."}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })
            ) : inspection.error ? (
              <div className="py-8 px-4 text-center text-xs flex flex-col items-center gap-3 bg-rose-950/20 m-3 rounded-lg border border-rose-900/50">
                <div className="w-8 h-8 rounded-full bg-rose-900/50 flex items-center justify-center text-rose-400 font-bold text-base">
                  !
                </div>
                <div className="space-y-1">
                  <div className="font-semibold text-rose-300">
                    {inspection.error.includes("Not a road photograph") || inspection.error.includes("Image issue")
                      ? "Image Inspection Notice"
                      : "Inference Server Offline"}
                  </div>
                  <p className="text-slate-400 text-[11px] max-w-xs leading-relaxed">
                    {inspection.error}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => runDetection()}
                  className="px-3 py-1.5 rounded-md text-xs font-bold bg-[#FF5A00] hover:bg-[#E04F00] text-white transition-colors cursor-pointer flex items-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Retry Inspection</span>
                </button>
              </div>
            ) : (
              <div className="py-12 px-4 text-center text-slate-400 text-xs flex flex-col items-center gap-2">
                <CheckCircle className="w-6 h-6 text-emerald-400" />
                <span className="font-medium text-white">Clean Road Pavement — No distress detected.</span>
              </div>
            )}
          </div>

          {/* Primary CTA: Navigate to Page 2 (Road Audit Report) */}
          <div className="p-3.5 border-t-2 border-[#283545] bg-[#161F2A] space-y-2">
            <Link
              to="/report"
              className="w-full py-3 px-4 rounded-xl text-xs font-bold bg-[#FF5A00] hover:bg-[#E04F00] text-white transition-all shadow-lg hover:shadow-orange-500/20 flex items-center justify-center gap-2 cursor-pointer border border-[#FF7324] active:scale-95 text-center"
            >
              <FileText className="w-4 h-4 text-white" />
              <span>Go to Page 2: Audit Report &amp; PDF →</span>
            </Link>
            <div className="text-[10px] text-center font-mono text-[#94A3B8]">
              IRC:82-2015 Road Distress Compliance &amp; Engineering Ledger
            </div>
          </div>
        </div>
      </div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-[#0B0F14]/95 flex flex-col p-4 backdrop-blur-md">
          <div className="flex items-center justify-between pb-3 border-b border-[#283545] text-sm">
            <span className="font-bold text-white font-mono">{activeRoadName}</span>
            <button
              type="button"
              onClick={() => setIsFullscreen(false)}
              className="p-1.5 rounded-md bg-[#1E293B] text-slate-300 hover:text-white cursor-pointer"
            >
              <Minimize2 className="w-4 h-4" />
            </button>
          </div>
          <div className="flex-1 flex items-center justify-center overflow-hidden mt-3">
            <div className="relative inline-block leading-none">
              <img
                src={activeImageSrc}
                alt={activeRoadName}
                className="block select-none"
                style={{ maxHeight: "calc(100vh - 100px)", maxWidth: "calc(100vw - 40px)" }}
              />
              {showBoxes && (
                <BoxOverlay
                  detections={inspection.boxes}
                  activeId={hoveredBoxId ?? selectedBoxId}
                  onHover={(id) => setHoveredBoxId(id)}
                  onSelect={(id) => setSelectedBoxId((prev) => (prev === id ? null : id))}
                  viewMode="boxes"
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
