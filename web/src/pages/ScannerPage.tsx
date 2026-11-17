import React, { useState, useRef, useEffect } from "react";
import {
  CheckCircle,
  RefreshCw,
  Maximize2,
  Minimize2,
  Camera,
  UploadCloud,
  Eye,
  EyeOff,
  Download,
  FileText,
  Printer,
  AlertTriangle,
} from "../components/Icons";
import { detectDefects, InspectionResult, DetectionPreset } from "../utils/cvDetector";
import { generateDistressPDFReport } from "../utils/pdfReport";
import { useToast } from "../context/ToastContext";
import { ScanLine, BoxOverlay } from "../motion";

interface SampleImage {
  id: string;
  label: string;
  src: string;
  road: string;
}

const SAMPLE_IMAGES: SampleImage[] = [
  {
    id: "capture-bengaluru",
    label: "Bengaluru",
    src: "/samples/bengaluru_potholes.jpg",
    road: "Bengaluru Arterial Road",
  },
  {
    id: "capture-pothole",
    label: "Crater",
    src: "/samples/asphalt_crater.jpg",
    road: "Asphalt Crater",
  },
  {
    id: "capture-cracks",
    label: "Cracks",
    src: "/samples/alligator_cracks.jpg",
    road: "Alligator Fatigue Cracks",
  },
  {
    id: "capture-mumbai",
    label: "Mumbai",
    src: "/samples/mumbai_potholes.avif",
    road: "Mumbai Monsoon Road",
  },
  {
    id: "capture-nh44",
    label: "NH-44",
    src: "/samples/pothole_nh44.jpg",
    road: "NH-44 Highway Distress",
  },
  {
    id: "capture-clean",
    label: "Clean Road",
    src: "/samples/clean_road.jpg",
    road: "Clean Highway Pavement",
  },
];

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
        cls: "bg-orange-500/20 text-orange-400 border-orange-500/50 font-bold",
      };
    case "Severe":
    case "High":
      return {
        label: "Severe",
        cls: "bg-amber-500/20 text-yellow-400 border-yellow-500/50 font-semibold",
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

export const ScannerPage: React.FC = () => {
  const [inputMode, setInputMode] = useState<InputMode>("image");
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [preset, setPreset] = useState<DetectionPreset>("balanced");
  const [confThresh, setConfThresh] = useState<number>(0.25);
  const [selectedSampleId, setSelectedSampleId] = useState<string>("capture-bengaluru");
  const [activeImageSrc, setActiveImageSrc] = useState<string>("/samples/bengaluru_potholes.jpg");
  const [activeRoadName, setActiveRoadName] = useState<string>("Bengaluru Arterial Road");
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanStage, setScanStage] = useState<"preprocess" | "inference" | "postprocess">("postprocess");
  const [selectedBoxId, setSelectedBoxId] = useState<string | null>(null);
  const [hoveredBoxId, setHoveredBoxId] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isExportingPDF, setIsExportingPDF] = useState<boolean>(false);
  const { error: showErrorToast, success: showSuccessToast } = useToast();

  const [inspection, setInspection] = useState<InspectionResult>({
    source: "neural_api",
    totalDefects: 0,
    potholeCount: 0,
    crackCount: 0,
    maxSeverity: "Minor",
    overallScore: 100,
    boxes: [],
    latencyMs: 0,
    imageWidth: 640,
    imageHeight: 480,
    engine: "Unified YOLO11n-Rescue + Guarded Surface Prior",
  });

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const uploadedFileRef = useRef<File | null>(null);
  const scanIdRef = useRef<number>(0);
  const abortRef = useRef<AbortController | null>(null);
  const reportSectionRef = useRef<HTMLDivElement>(null);

  const runDetection = async (source: string | Blob) => {
    const scanId = ++scanIdRef.current;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsScanning(true);
    setSelectedBoxId(null);
    setHoveredBoxId(null);
    setInspection((prev) => ({
      ...prev,
      totalDefects: 0,
      potholeCount: 0,
      crackCount: 0,
      boxes: [],
      latencyMs: 0,
      error: undefined,
    }));

    try {
      const result = await detectDefects(
        source,
        confThresh,
        preset,
        (stage) => {
          if (scanIdRef.current === scanId) setScanStage(stage);
        },
        controller.signal
      );
      if (scanIdRef.current !== scanId) return;
      setInspection(result);
      if (result.error && !result.error.includes("Not a road photograph") && !result.error.includes("Image issue")) {
        showErrorToast("Inference Connection Error", result.error);
      }
    } catch (err) {
      if ((err as Error)?.name !== "AbortError") {
        console.error("Inference failed", err);
        showErrorToast("Inference Failed", (err as Error)?.message || "Backend unreachable");
      }
    } finally {
      if (scanIdRef.current === scanId) {
        setIsScanning(false);
      }
    }
  };

  useEffect(() => {
    if (inputMode === "image" && activeImageSrc) {
      runDetection(uploadedFileRef.current ?? activeImageSrc);
    }
  }, [activeImageSrc, confThresh, preset, inputMode, selectedSampleId]);

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

  const handleFileUpload = (file: File) => {
    uploadedFileRef.current = file;
    const url = URL.createObjectURL(file);
    setInputMode("image");
    setSelectedSampleId("");
    setActiveRoadName(file.name);
    setActiveImageSrc(url);
  };

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

  const handleDownloadPDF = () => {
    setIsExportingPDF(true);
    try {
      generateDistressPDFReport({
        roadName: activeRoadName,
        preset,
        confThresh,
        totalDefects: inspection.totalDefects,
        potholeCount: inspection.potholeCount,
        crackCount: inspection.crackCount,
        maxSeverity: inspection.maxSeverity,
        overallScore: inspection.overallScore,
        latencyMs: inspection.latencyMs,
        engine: inspection.engine,
        boxes: inspection.boxes,
        imageSrc: activeImageSrc,
      });
      showSuccessToast("Report Downloaded", "Official PDF Inspection Audit Report generated successfully.");
    } catch (err) {
      console.error("PDF generation failed:", err);
      showErrorToast("PDF Error", "Unable to compile PDF document. Please try again.");
    } finally {
      setIsExportingPDF(false);
    }
  };

  const handleExportJSON = () => {
    const reportData = {
      report_title: "RoadSurvey AI Infrastructure Distress Audit",
      audit_timestamp: new Date().toISOString(),
      road_name: activeRoadName,
      detection_engine: inspection.engine,
      preset,
      sensitivity_pct: Math.round(confThresh * 100),
      pavement_condition_score: inspection.overallScore,
      max_severity: inspection.maxSeverity,
      total_defects: inspection.totalDefects,
      potholes_count: inspection.potholeCount,
      cracks_count: inspection.crackCount,
      latency_ms: inspection.latencyMs,
      itemized_defects: inspection.boxes,
    };
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `RoadSurvey_Audit_${activeRoadName.replace(/[^a-zA-Z0-9_-]/g, "_")}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showSuccessToast("JSON Exported", "Raw defect audit records saved.");
  };

  const scrollToReport = () => {
    reportSectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Banner: High-Vis Orange & Asphalt Black */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#121820] p-4 sm:p-5 rounded-xl border border-[#283545] shadow-lg relative overflow-hidden">
        {/* Subtle orange hazard strip at top */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#FF5A00] via-[#FFD200] to-[#FF5A00]" />

        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#FF5A00] text-white tracking-wider uppercase">
              Live AI Detection
            </span>
            <span className="text-xs font-mono text-[#FFD200] font-semibold">
              YOLO11n-Rescue
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white mt-1">
            Road Damage & Pothole Scanner
          </h1>
          <p className="text-xs text-[#94A3B8] mt-0.5">
            Real-time infrastructure defect detection with drivable surface validation and automated PDF audit reporting.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <label className="px-4 py-2.5 rounded-lg text-xs font-bold bg-[#FF5A00] hover:bg-[#E04F00] text-white transition-all shadow-md hover:shadow-orange-500/20 cursor-pointer flex items-center gap-2 active:scale-95 border border-[#FF6B1A]">
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
            className={`px-3.5 py-2.5 rounded-lg text-xs font-medium border transition-all cursor-pointer flex items-center gap-1.5 ${
              inputMode === "camera"
                ? "bg-[#FFD200] text-[#0B0F14] border-[#FFD200] font-bold shadow-sm"
                : "bg-[#1E293B] border-[#334155] text-white hover:bg-[#334155]"
            }`}
          >
            <Camera className="w-4 h-4" />
            <span>{inputMode === "camera" ? "Photo Mode" : "Camera"}</span>
          </button>
        </div>
      </div>

      {/* 2. Sample Image Switcher */}
      {inputMode !== "camera" && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1 [scrollbar-width:thin]">
          <span className="text-xs font-bold text-[#FFD200] shrink-0 uppercase tracking-wider font-mono mr-1 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FFD200]" />
            Test Samples:
          </span>
          {SAMPLE_IMAGES.map((sample) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => {
                uploadedFileRef.current = null;
                setInputMode("image");
                setActiveImageSrc(sample.src);
                setActiveRoadName(sample.road);
                setSelectedSampleId(sample.id);
              }}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium border transition-all shrink-0 cursor-pointer ${
                selectedSampleId === sample.id
                  ? "bg-[#FF5A00] text-white border-[#FF5A00] font-bold shadow-md shadow-orange-500/20"
                  : "bg-[#121820] border-[#283545] text-[#94A3B8] hover:text-white hover:border-[#475569]"
              }`}
            >
              {sample.label}
            </button>
          ))}
        </div>
      )}

      {/* 3. Main 2-Column Detector View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left: Image Canvas */}
        <div className="lg:col-span-8 bg-[#121820] border border-[#283545] rounded-xl p-4 space-y-3.5 shadow-md">
          <div className="flex items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2 truncate">
              <span className="w-2 h-2 rounded-full bg-[#FF5A00]" />
              <span className="font-semibold text-white truncate text-sm">
                {activeRoadName}
              </span>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setShowBoxes(!showBoxes)}
                className="px-2.5 py-1 rounded-md border border-[#334155] bg-[#1E293B] text-[#94A3B8] hover:text-white cursor-pointer flex items-center gap-1.5 transition-colors"
              >
                {showBoxes ? <Eye className="w-3.5 h-3.5 text-[#FF5A00]" /> : <EyeOff className="w-3.5 h-3.5" />}
                <span>{showBoxes ? "Hide Boxes" : "Show Boxes"}</span>
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
            className="relative min-h-[380px] max-h-[500px] bg-[#0B0F14] rounded-lg overflow-hidden flex items-center justify-center border border-[#1E293B]"
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
                  className="mt-3 px-4 py-2 rounded-md bg-[#FF5A00] hover:bg-[#E04F00] text-white text-xs font-bold cursor-pointer flex items-center gap-1.5 shadow-md"
                >
                  <Camera className="w-4 h-4" />
                  <span>Scan Live Frame</span>
                </button>
              </div>
            ) : (
              <div className="relative w-full h-[460px] flex items-center justify-center select-none">
                {/* Overlay Status Badge */}
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
                      ? "AI Scanning..."
                      : inspection.error
                      ? "Inspection Notice"
                      : inspection.boxes.length > 0
                        ? `${inspection.potholeCount} Potholes · ${inspection.crackCount} Cracks`
                        : "Clean Road Surface"}
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

          {/* Bottom Controls Row: Presets & Sensitivity */}
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
              <span className="font-medium text-white">Sensitivity:</span>
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
              <span className="px-1.5 py-0.5 rounded bg-[#1E293B] border border-[#334155] text-white font-medium">
                Guards Active
              </span>
              <span>·</span>
              <span>{inspection.latencyMs > 0 ? `${(inspection.latencyMs / 1000).toFixed(2)}s` : "Ready"}</span>
            </div>
          </div>
        </div>

        {/* Right: Results Panel */}
        <div className="lg:col-span-4 bg-[#121820] border border-[#283545] rounded-xl overflow-hidden flex flex-col shadow-md">
          {/* Top 3 Stat Cards */}
          <div className="grid grid-cols-3 divide-x divide-[#283545] border-b border-[#283545] text-center py-3.5 bg-[#161F2A]">
            <div>
              <div className="text-[11px] text-[#94A3B8] font-bold uppercase tracking-wider font-mono">Potholes</div>
              <div className="text-xl font-bold text-[#FF5A00] font-mono mt-0.5">
                {inspection.potholeCount}
              </div>
            </div>
            <div>
              <div className="text-[11px] text-[#94A3B8] font-bold uppercase tracking-wider font-mono">Cracks</div>
              <div className="text-xl font-bold text-[#FFD200] font-mono mt-0.5">
                {inspection.crackCount}
              </div>
            </div>
            <div>
              <div className="text-[11px] text-[#94A3B8] font-bold uppercase tracking-wider font-mono">Road State</div>
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

          {/* Defect List or Notice */}
          <div className="divide-y divide-[#1E293B] max-h-[360px] overflow-y-auto [scrollbar-width:thin]">
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
                        ? "bg-[#1E293B] border-l-2 border-[#FF5A00]"
                        : "hover:bg-[#1A222D]"
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedBoxId((prev) => (prev === b.id ? null : b.id))}
                      className="w-full flex items-center justify-between gap-2 cursor-pointer text-left"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-[#64748B] font-mono w-5 shrink-0">#{idx + 1}</span>
                        <span className="font-semibold text-white truncate">
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
                          <span>Distress Impact:</span>
                          <span className="font-bold text-white">{b.score || 45}/100</span>
                        </div>
                        <div className="flex justify-between font-mono">
                          <span>Pavement Area:</span>
                          <span className="text-white">{b.area_pct ? `${b.area_pct}%` : `${b.areaPx} px`}</span>
                        </div>
                        {b.wheelPathRisk && (
                          <div className="flex justify-between font-mono text-[#FF5A00] font-bold">
                            <span>Wheel Path Hazard:</span>
                            <span>CRITICAL RISK</span>
                          </div>
                        )}
                        <p className="text-[11px] italic text-[#CBD5E1] bg-[#0B0F14] p-2 rounded border border-[#283545]">
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
                  onClick={() => runDetection(uploadedFileRef.current ?? activeImageSrc)}
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

          {/* Quick jump to report button */}
          <div className="p-3 border-t border-[#283545] bg-[#161F2A]">
            <button
              type="button"
              onClick={scrollToReport}
              className="w-full py-2.5 rounded-lg text-xs font-bold bg-[#1E293B] hover:bg-[#283545] text-[#FFD200] border border-[#334155] transition-all flex items-center justify-center gap-2 cursor-pointer shadow-sm hover:text-white"
            >
              <FileText className="w-4 h-4 text-[#FF5A00]" />
              <span>View Full Audit Report &amp; PDF</span>
            </button>
          </div>
        </div>
      </div>

      {/* 4. COMPREHENSIVE ROAD DISTRESS AUDIT REPORT & PDF SECTION */}
      <div
        ref={reportSectionRef}
        className="bg-[#121820] border-2 border-[#283545] rounded-xl p-5 sm:p-6 space-y-6 shadow-xl relative"
      >
        {/* Section Top Header & PDF Actions */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#283545]">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#FF5A00] text-white tracking-widest uppercase">
                OFFICIAL AUDIT REPORT
              </span>
              <span className="text-xs font-mono text-[#FFD200] font-semibold">
                IRC:82-2015 Compliant
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white mt-1">
              Road Distress &amp; Maintenance Audit Report
            </h2>
            <p className="text-xs text-[#94A3B8] mt-0.5">
              Comprehensive civil engineering ledger, surface health index, and automated maintenance protocol for <span className="text-white font-semibold">{activeRoadName}</span>.
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            {/* Primary Download PDF Button */}
            <button
              type="button"
              onClick={handleDownloadPDF}
              disabled={isExportingPDF}
              className="px-4 py-2.5 rounded-lg text-xs font-bold bg-[#FF5A00] hover:bg-[#E04F00] text-white transition-all shadow-lg hover:shadow-orange-500/20 cursor-pointer flex items-center gap-2 active:scale-95 border border-[#FF7324] disabled:opacity-50"
            >
              {isExportingPDF ? (
                <RefreshCw className="w-4 h-4 animate-spin text-white" />
              ) : (
                <Download className="w-4 h-4 text-white" />
              )}
              <span>Download PDF Report</span>
            </button>

            {/* Print Button */}
            <button
              type="button"
              onClick={() => window.print()}
              className="px-3.5 py-2.5 rounded-lg text-xs font-medium bg-[#1E293B] hover:bg-[#283545] text-white border border-[#334155] transition-all cursor-pointer flex items-center gap-1.5"
              title="Print Report"
            >
              <Printer className="w-4 h-4 text-[#FFD200]" />
              <span className="hidden sm:inline">Print</span>
            </button>

            {/* Export JSON Button */}
            <button
              type="button"
              onClick={handleExportJSON}
              className="px-3.5 py-2.5 rounded-lg text-xs font-medium bg-[#1E293B] hover:bg-[#283545] text-[#94A3B8] hover:text-white border border-[#334155] transition-all cursor-pointer flex items-center gap-1.5"
              title="Export GIS JSON"
            >
              <FileText className="w-4 h-4 text-[#94A3B8]" />
              <span className="hidden sm:inline">JSON</span>
            </button>
          </div>
        </div>

        {/* Executive KPI Summary Grid (4 Cards) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
          <div className="bg-[#161F2A] border border-[#283545] rounded-xl p-3.5 space-y-1 shadow-sm">
            <div className="text-[11px] font-mono font-bold text-[#94A3B8] uppercase">Total Distress Items</div>
            <div className="text-2xl sm:text-3xl font-mono font-bold text-white">
              {inspection.totalDefects}
            </div>
            <div className="text-[10px] text-[#64748B] font-mono">Detected via dual-pass AI</div>
          </div>

          <div className="bg-[#161F2A] border border-[#283545] rounded-xl p-3.5 space-y-1 shadow-sm border-l-4 border-l-[#FF5A00]">
            <div className="text-[11px] font-mono font-bold text-[#FF5A00] uppercase">Potholes &amp; Craters</div>
            <div className="text-2xl sm:text-3xl font-mono font-bold text-[#FF5A00]">
              {inspection.potholeCount}
            </div>
            <div className="text-[10px] text-[#94A3B8] font-mono">Structural subgrade distress</div>
          </div>

          <div className="bg-[#161F2A] border border-[#283545] rounded-xl p-3.5 space-y-1 shadow-sm border-l-4 border-l-[#FFD200]">
            <div className="text-[11px] font-mono font-bold text-[#FFD200] uppercase">Fatigue Cracks</div>
            <div className="text-2xl sm:text-3xl font-mono font-bold text-[#FFD200]">
              {inspection.crackCount}
            </div>
            <div className="text-[10px] text-[#94A3B8] font-mono">Alligator / Transverse lines</div>
          </div>

          <div className="bg-[#161F2A] border border-[#283545] rounded-xl p-3.5 space-y-1 shadow-sm">
            <div className="text-[11px] font-mono font-bold text-[#94A3B8] uppercase">Road Health Index</div>
            <div className={`text-2xl sm:text-3xl font-mono font-bold ${
              inspection.overallScore < 50 ? "text-[#FF5A00]" : inspection.overallScore < 75 ? "text-[#FFD200]" : "text-emerald-400"
            }`}>
              {inspection.overallScore}<span className="text-sm text-[#64748B]">/100</span>
            </div>
            <div className="text-[10px] text-[#94A3B8] font-mono uppercase font-bold">
              {inspection.maxSeverity} Severity
            </div>
          </div>
        </div>

        {/* Audit Technical Specification Block */}
        <div className="bg-[#0B0F14] border border-[#283545] rounded-xl p-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono text-[#94A3B8]">
          <div className="space-y-1">
            <span className="text-[#64748B] block text-[10px] uppercase font-bold">Target Location / File</span>
            <span className="text-white font-semibold">{activeRoadName}</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#64748B] block text-[10px] uppercase font-bold">Certified AI Engine</span>
            <span className="text-white font-semibold">YOLO11n-Rescue + Surface Prior</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#64748B] block text-[10px] uppercase font-bold">Inference Speed &amp; Preset</span>
            <span className="text-[#FFD200] font-semibold">
              {(inspection.latencyMs / 1000).toFixed(2)}s · {preset.toUpperCase()} ({Math.round(confThresh * 100)}%)
            </span>
          </div>
        </div>

        {/* Itemized Distress Ledger Table */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#FF5A00]" />
              Itemized Defect Ledger Table
            </h3>
            <span className="text-xs font-mono text-[#94A3B8]">
              {inspection.boxes.length} item(s) logged
            </span>
          </div>

          <div className="overflow-x-auto border border-[#283545] rounded-xl bg-[#0B0F14] [scrollbar-width:thin]">
            <table className="w-full text-left text-xs font-mono border-collapse min-w-[700px]">
              <thead>
                <tr className="bg-[#161F2A] text-white border-b border-[#283545]">
                  <th className="py-3 px-3.5 text-[#94A3B8] font-bold">#</th>
                  <th className="py-3 px-3.5 font-bold">Defect Type</th>
                  <th className="py-3 px-3.5 font-bold">Confidence</th>
                  <th className="py-3 px-3.5 font-bold">Severity</th>
                  <th className="py-3 px-3.5 font-bold">Pavement Area</th>
                  <th className="py-3 px-3.5 font-bold">Wheel Path</th>
                  <th className="py-3 px-3.5 font-bold">Recommended Maintenance Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B]">
                {inspection.boxes.length > 0 ? (
                  inspection.boxes.map((b, idx) => {
                    const badge = getSeverityBadge(b.severity);
                    const title = formatDefectTitle(b.label);
                    return (
                      <tr key={b.id} className="hover:bg-[#161F2A]/60 transition-colors">
                        <td className="py-2.5 px-3.5 text-[#64748B]">#{idx + 1}</td>
                        <td className="py-2.5 px-3.5 font-bold text-white flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${title.includes("Crack") ? "bg-[#FFD200]" : "bg-[#FF5A00]"}`} />
                          {title}
                        </td>
                        <td className="py-2.5 px-3.5 text-[#FFD200] font-bold">
                          {Math.round(b.confidence * 100)}%
                        </td>
                        <td className="py-2.5 px-3.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] border ${badge.cls}`}>
                            {badge.label}
                          </span>
                        </td>
                        <td className="py-2.5 px-3.5 text-[#CBD5E1]">
                          {b.area_pct ? `${b.area_pct}%` : `${b.areaPx} px`}
                        </td>
                        <td className="py-2.5 px-3.5">
                          {b.wheelPathRisk ? (
                            <span className="text-[#FF5A00] font-bold flex items-center gap-1">
                              <AlertTriangle className="w-3.5 h-3.5 text-[#FF5A00]" />
                              HAZARD
                            </span>
                          ) : (
                            <span className="text-[#64748B]">Safe</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3.5 text-[#CBD5E1]">
                          {b.action || (title.includes("Pothole") ? "Emergency Cold-Mix Asphalt Patch" : "Bituminous Crack Pouring & Sealant")}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={7} className="py-8 px-4 text-center text-[#94A3B8]">
                      No active distress detected on this road section.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Municipal Engineering Maintenance Recommendations */}
        <div className="bg-[#1A1A14] border border-[#F59E0B]/40 rounded-xl p-4 space-y-2 text-xs">
          <div className="flex items-center gap-2 text-[#FFD200] font-bold font-mono text-sm">
            <AlertTriangle className="w-4 h-4 text-[#FFD200]" />
            Municipal Civil Engineering Recommendations
          </div>
          <p className="text-[#CBD5E1] leading-relaxed">
            {inspection.totalDefects > 0 ? (
              <>
                Detected <span className="text-[#FF5A00] font-bold">{inspection.totalDefects} surface distress item(s)</span> including <span className="text-[#FF5A00] font-bold">{inspection.potholeCount} crater(s)</span> and <span className="text-[#FFD200] font-bold">{inspection.crackCount} crack(s)</span>. Priority mobilization should be allocated to craters directly in the active wheel path to mitigate vehicular tire and suspension impact liability. Recommended dispatch: Asphalt cold-mix patching crew and pneumatic compaction roller.
              </>
            ) : (
              <>
                Pavement section demonstrates acceptable serviceability conforming to municipal road standards. No immediate asphalt milling, cold patching, or crack pouring required. Schedule routine periodic sensor monitoring.
              </>
            )}
          </p>
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
