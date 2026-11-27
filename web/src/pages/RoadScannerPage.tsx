import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Maximize2,
  Minimize2,
  Camera,
  UploadCloud,
  Eye,
  EyeOff,
} from "../components/Icons";
import { useInspection } from "../context/InspectionContext";
import { ScanLine, BoxOverlay } from "../motion";

type InputMode = "image" | "camera";

const formatDefectTitle = (label: string) => {
  const upper = (label || "").toUpperCase();
  if (upper.includes("WATER")) return "Water-filled Pothole";
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
        cls: "bg-[#D55E00]/15 text-[#D55E00] border-[#D55E00]/40 font-bold",
      };
    case "Severe":
    case "High":
      return {
        label: "Severe",
        cls: "bg-[#E8B100]/20 text-accent border-[#E8B100]/40 font-semibold",
      };
    case "Moderate":
      return {
        label: "Moderate",
        cls: "bg-rule/40 text-muted border-rule font-medium",
      };
    default:
      return {
        label: "Minor",
        cls: "bg-surface text-muted border-rule font-normal",
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

  // Generate a concise, non-clipping one-sentence result summary
  const getResultSummary = (): string => {
    if (isScanning) {
      return "Analyzing frame through input gate classifier, drivable surface mask, and YOLO11 detector...";
    }
    if (inspection.error) {
      return `Inspection Notice: ${inspection.error}`;
    }
    if (inspection.boxes.length === 0) {
      return "No pavement distress detected; bituminous drivable surface verified with 0 candidate anomalies.";
    }
    const potholeText =
      inspection.potholeCount > 0
        ? `${inspection.potholeCount} ${inspection.potholeCount === 1 ? "pothole" : "potholes"}`
        : "";
    const crackText =
      inspection.crackCount > 0
        ? `${inspection.crackCount} ${inspection.crackCount === 1 ? "crack" : "cracks"}`
        : "";
    const joined = [potholeText, crackText].filter(Boolean).join(" and ");
    return `Detected ${joined} on ${activeRoadName} (${activeChainage}) with maximum severity evaluated as ${inspection.maxSeverity}.`;
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Toolbar */}
      <div className="border border-rule rounded-[4px] bg-surface p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-serif font-bold text-text">Pavement Distress Detector</h1>
            <span className="text-[11px] font-mono px-1.5 py-0.5 rounded-[3px] border border-rule text-muted">
              YOLO11 + Drivable Mask
            </span>
          </div>
          <p className="text-xs text-muted mt-0.5">
            Dashcam / smartphone image analysis with road surface overlap and non-road gate filters.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <label className="px-3 py-1.5 rounded-[4px] text-xs font-sans font-semibold bg-text text-bg hover:opacity-90 transition-opacity cursor-pointer flex items-center gap-1.5">
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload Road Photo</span>
            <input
              type="file"
              accept="image/*,.avif,.webp"
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
            className={`px-3 py-1.5 rounded-[4px] text-xs font-mono border transition-colors cursor-pointer flex items-center gap-1.5 ${
              inputMode === "camera"
                ? "bg-text text-bg border-text font-bold"
                : "bg-surface border-rule text-text hover:bg-surface-raised"
            }`}
          >
            <Camera className="w-3.5 h-3.5" />
            <span>{inputMode === "camera" ? "Photo Mode" : "Camera"}</span>
          </button>
        </div>
      </div>

      {/* 2. One-Sentence Result Summary (Never Clips) */}
      <div
        className="p-3 border border-rule rounded-[4px] bg-surface text-xs font-sans text-text break-words leading-relaxed flex items-start gap-2.5"
        role="status"
        aria-live="polite"
      >
        <span
          className={`w-2 h-2 rounded-full mt-1 shrink-0 ${
            inspection.error
              ? "bg-[#D55E00]"
              : inspection.boxes.length > 0
              ? "bg-accent"
              : "bg-[#10B981]"
          }`}
        />
        <div className="flex-1 font-medium">{getResultSummary()}</div>
        <div className="text-[11px] font-mono text-muted shrink-0">
          {(inspection.latencyMs / 1000).toFixed(2)}s
        </div>
      </div>

      {/* 3. Main Workspace: Image Canvas & Defect Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Canvas Area */}
        <div className="lg:col-span-8 border border-rule rounded-[4px] bg-surface p-3 space-y-3">
          <div className="flex items-center justify-between text-xs border-b border-rule pb-2">
            <div className="flex items-center gap-2 truncate">
              <span className="font-serif font-bold text-text truncate">{activeRoadName}</span>
              <span className="text-[11px] font-mono text-muted">({activeChainage})</span>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setShowBoxes(!showBoxes)}
                className="px-2 py-1 rounded-[4px] border border-rule text-muted hover:text-text text-xs font-mono cursor-pointer transition-colors flex items-center gap-1"
              >
                {showBoxes ? <Eye className="w-3 h-3 text-accent" /> : <EyeOff className="w-3 h-3" />}
                <span>{showBoxes ? "Hide Boxes" : "Show Boxes"}</span>
              </button>

              <button
                type="button"
                onClick={() => setIsFullscreen(true)}
                className="p-1 rounded-[4px] border border-rule text-muted hover:text-text cursor-pointer transition-colors"
                title="Fullscreen View"
                aria-label="Fullscreen View"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Canvas Container */}
          <div className="relative min-h-[380px] max-h-[500px] bg-[#121311] rounded-[4px] overflow-hidden flex items-center justify-center border border-rule">
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
                  className="mt-3 px-4 py-2 rounded-[4px] bg-text text-bg text-xs font-bold font-sans cursor-pointer flex items-center gap-2"
                >
                  <Camera className="w-4 h-4" />
                  <span>Capture Frame</span>
                </button>
              </div>
            ) : (
              <div className="relative w-full h-[460px] flex items-center justify-center select-none">
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
                      detections={inspection.boxes.slice(0, 30)}
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

          {/* Presets Control Bar (From PR Curve: High Precision / Balanced / High Recall; NO raw slider) */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs border-t border-rule pt-3">
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-xs uppercase text-muted font-bold">Preset:</span>
              <button
                type="button"
                onClick={() => {
                  setPreset("high_precision");
                  setConfThresh(0.40);
                }}
                className={`px-2.5 py-1 rounded-[4px] text-xs font-mono border transition-colors cursor-pointer ${
                  preset === "high_precision"
                    ? "bg-text text-bg border-text font-bold"
                    : "bg-surface border-rule text-muted hover:text-text"
                }`}
                title="High Precision (conf >= 0.40): lowest false alarm rate (99.87% clean specificity)"
              >
                High Precision
              </button>
              <button
                type="button"
                onClick={() => {
                  setPreset("balanced");
                  setConfThresh(0.25);
                }}
                className={`px-2.5 py-1 rounded-[4px] text-xs font-mono border transition-colors cursor-pointer ${
                  preset === "balanced"
                    ? "bg-text text-bg border-text font-bold"
                    : "bg-surface border-rule text-muted hover:text-text"
                }`}
                title="Balanced (conf >= 0.25): calibrated optimal F1 across all defect types"
              >
                Balanced (Default)
              </button>
              <button
                type="button"
                onClick={() => {
                  setPreset("high_recall");
                  setConfThresh(0.15);
                }}
                className={`px-2.5 py-1 rounded-[4px] text-xs font-mono border transition-colors cursor-pointer ${
                  preset === "high_recall"
                    ? "bg-text text-bg border-text font-bold"
                    : "bg-surface border-rule text-muted hover:text-text"
                }`}
                title="High Recall (conf >= 0.15): catches faint low-contrast fissures"
              >
                High Recall
              </button>
            </div>

            <div className="text-[11px] font-mono text-muted flex items-center gap-2">
              <span>Threshold: {(confThresh * 100).toFixed(0)}%</span>
              <span>·</span>
              <span>WBF Fusion</span>
              <span>·</span>
              <span>Road Mask &ge; 35%</span>
            </div>
          </div>
        </div>

        {/* Right: Defect Listing Console */}
        <div className="lg:col-span-4 border border-rule rounded-[4px] bg-surface overflow-hidden flex flex-col">
          {/* Top Counts */}
          <div className="grid grid-cols-3 divide-x divide-rule border-b border-rule text-center py-3 bg-surface-raised">
            <div>
              <div className="text-[10px] font-mono uppercase text-muted font-bold">Potholes</div>
              <div className="text-xl font-mono font-bold text-[#D55E00] mt-0.5">
                {inspection.potholeCount}
              </div>
            </div>
            <div>
              <div className="text-[10px] font-mono uppercase text-muted font-bold">Cracks</div>
              <div className="text-xl font-mono font-bold text-[#0072B2] mt-0.5">
                {inspection.crackCount}
              </div>
            </div>
            <div>
              <div className="text-[10px] font-mono uppercase text-muted font-bold">Severity</div>
              <div className="text-xs font-mono font-bold text-text mt-1">
                {inspection.error ? "Notice" : inspection.boxes.length === 0 ? "Good" : inspection.maxSeverity}
              </div>
            </div>
          </div>

          {/* Defect List */}
          <div className="divide-y divide-rule max-h-[380px] overflow-y-auto">
            {inspection.boxes.length > 0 ? (
              inspection.boxes.map((b, idx) => {
                const isSelected = selectedBoxId === b.id;
                const badge = getSeverityBadge(b.severity);
                return (
                  <div
                    key={b.id}
                    onMouseEnter={() => setHoveredBoxId(b.id)}
                    onMouseLeave={() => setHoveredBoxId(null)}
                    className={`p-3 space-y-1 text-xs transition-colors ${
                      isSelected ? "bg-surface-raised border-l-2 border-accent" : "hover:bg-surface-raised/40"
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedBoxId((prev) => (prev === b.id ? null : b.id))}
                      className="w-full flex items-center justify-between gap-2 cursor-pointer text-left"
                    >
                      <div className="flex items-center gap-1.5 min-w-0">
                        <span className="font-mono text-muted text-[11px]">#{idx + 1}</span>
                        <span className="font-medium text-text truncate">
                          {formatDefectTitle(b.label)}
                        </span>
                        <span className={`font-mono text-[10px] px-1 py-0.2 rounded-[2px] border ${badge.cls}`}>
                          {badge.label}
                        </span>
                      </div>
                      <span className="font-mono font-bold text-text shrink-0">
                        {Math.round(b.confidence * 100)}%
                      </span>
                    </button>

                    {isSelected && (
                      <div className="pt-2 border-t border-rule space-y-1 text-[11px] text-muted font-mono">
                        <div className="flex justify-between">
                          <span>Box Area:</span>
                          <span className="text-text">{b.area_pct ? `${b.area_pct}%` : `${b.areaPx} px`}</span>
                        </div>
                        {b.wheelPathRisk && (
                          <div className="flex justify-between text-[#D55E00] font-bold">
                            <span>Wheelpath Impact:</span>
                            <span>HIGH RISK</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            ) : inspection.error ? (
              <div className="p-6 text-center text-xs space-y-2">
                <div className="font-bold text-[#D55E00]">Input Filter Notice</div>
                <p className="text-muted leading-relaxed">{inspection.error}</p>
                <button
                  type="button"
                  onClick={() => runDetection()}
                  className="px-3 py-1 rounded-[4px] text-xs font-mono border border-rule bg-surface text-text hover:bg-surface-raised cursor-pointer mt-2"
                >
                  Retry Inspection
                </button>
              </div>
            ) : (
              <div className="p-8 text-center text-xs space-y-1 text-muted">
                <div className="font-serif font-medium text-text">Pristine Road Section</div>
                <p>No bounding boxes detected on drivable road surface.</p>
              </div>
            )}
          </div>

          {/* Action Links */}
          <div className="p-3 border-t border-rule bg-surface-raised space-y-2">
            <Link
              to="/records"
              className="block w-full py-2 px-3 rounded-[4px] text-center text-xs font-sans font-semibold bg-text text-bg hover:opacity-90 transition-opacity"
            >
              Export Chainage Report &amp; PDF
            </Link>
            <Link
              to="/review"
              className="block w-full py-1.5 px-3 rounded-[4px] text-center text-xs font-mono border border-rule bg-surface text-muted hover:text-text transition-colors"
            >
              Open Review Queue ({inspection.boxes.filter((b) => b.confidence >= 0.25 && b.confidence < 0.65).length} candidates)
            </Link>
          </div>
        </div>
      </div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-[#121311]/95 flex flex-col p-4 backdrop-blur-xs">
          <div className="flex items-center justify-between pb-3 border-b border-rule text-sm">
            <span className="font-serif font-bold text-white">{activeRoadName} ({activeChainage})</span>
            <button
              type="button"
              onClick={() => setIsFullscreen(false)}
              className="p-1 rounded-[4px] bg-surface text-text border border-rule cursor-pointer"
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
