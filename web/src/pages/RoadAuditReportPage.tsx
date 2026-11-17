import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  FileText,
  Download,
  Printer,
  ArrowLeft,
  CheckCircle,
  Activity,
  ShieldCheck,
  Compass,
  Layers,
  Clock,
} from "../components/Icons";
import { useInspection } from "../context/InspectionContext";
import { generateDistressPDFReport } from "../utils/pdfReport";
import { BoxOverlay } from "../motion/BoxOverlay";

const getWheelPathLocation = (boxCoords: [number, number, number, number]) => {
  const [x, , w] = boxCoords;
  const centerX = x + w / 2;
  if (centerX < 35) return "Left Wheelpath (High Impact)";
  if (centerX > 65) return "Right Wheelpath (High Impact)";
  return "Center Lane / Crown (Medium Impact)";
};

const getEngineeringAction = (label: string, severity?: string) => {
  const upper = (label || "").toUpperCase();
  const isCrack = upper.includes("CRACK");
  if (severity === "Critical") {
    return isCrack
      ? "Full-depth mastic asphalt mill & overlay (IRC:SP:20)"
      : "Immediate Class-A cold/warm bituminous patch & roller compaction";
  }
  if (severity === "Severe" || severity === "High") {
    return isCrack
      ? "Polymer-modified asphalt crack sealant & surface dressing"
      : "Mechanical square-cut pothole filling with bituminous concrete";
  }
  if (severity === "Moderate") {
    return isCrack
      ? "High-pressure clean & pressurized bitumen slurry seal"
      : "Emulsion tack-coat spray & aggregate compaction";
  }
  return isCrack
    ? "Monitor crack propagation rate; scheduled routine seal"
    : "Surface level patch & routine pavement leveling";
};

export const RoadAuditReportPage: React.FC = () => {
  const {
    activeImageSrc,
    activeRoadName,
    activeChainage,
    preset,
    confThresh,
    inspection,
    selectedBoxId,
    hoveredBoxId,
    setSelectedBoxId,
    setHoveredBoxId,
  } = useInspection();

  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownloadPdf = () => {
    setIsGeneratingPdf(true);
    try {
      generateDistressPDFReport({
        roadName: `${activeRoadName} (${activeChainage})`,
        preset,
        confThresh,
        totalDefects: inspection.totalDefects,
        potholeCount: inspection.potholeCount,
        crackCount: inspection.crackCount,
        maxSeverity: inspection.maxSeverity,
        overallScore: inspection.overallScore,
        latencyMs: inspection.latencyMs,
        engine: inspection.engine || "Unified YOLO11n-Rescue + Surface Guards",
        boxes: inspection.boxes,
        imageSrc: activeImageSrc,
      });
      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 4000);
    } catch (err) {
      console.error("PDF generation failed:", err);
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  // PCI calculation & interpretation
  const pci = inspection.overallScore;
  const pciRating =
    pci >= 85
      ? { label: "Good Condition", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30", bar: "bg-emerald-500" }
      : pci >= 65
      ? { label: "Satisfactory / Fair", color: "text-[#FFD200]", bg: "bg-[#FFD200]/10 border-[#FFD200]/30", bar: "bg-[#FFD200]" }
      : pci >= 45
      ? { label: "Poor / Distressed", color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30", bar: "bg-amber-500" }
      : { label: "Critical Surface Failure", color: "text-[#FF5A00]", bg: "bg-[#FF5A00]/10 border-[#FF5A00]/30", bar: "bg-[#FF5A00]" };

  return (
    <div className="space-y-6 pb-16 font-sans">
      {/* Road Hazard Caution Top Header */}
      <div className="relative overflow-hidden rounded-2xl bg-[#121820] border-2 border-[#283545] shadow-xl">
        <div
          className="h-2.5 w-full"
          style={{
            backgroundImage:
              "repeating-linear-gradient(45deg, #FF5A00, #FF5A00 14px, #0B0F14 14px, #0B0F14 28px)",
          }}
        />

        <div className="p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wide uppercase bg-[#FF5A00] text-white">
                Official Road Audit Report
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wide uppercase bg-[#1E293B] text-[#FFD200] border border-[#334155]">
                ASTM D6433 / IRC Standard
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <span>{activeRoadName}</span>
            </h1>
            <p className="text-xs md:text-sm font-mono text-slate-400 flex items-center gap-2">
              <Compass className="w-4 h-4 text-[#FFD200]" />
              <span>Chainage: {activeChainage}</span>
              <span className="text-slate-600">|</span>
              <Clock className="w-4 h-4 text-slate-400" />
              <span>Timestamp: {new Date().toLocaleDateString()} · {new Date().toLocaleTimeString()}</span>
            </p>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-mono font-bold text-white bg-[#1E293B] hover:bg-[#283545] border border-[#334155] transition-all"
            >
              <ArrowLeft className="w-4 h-4 text-[#FFD200]" />
              <span>← Back to Scanner</span>
            </Link>

            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-mono font-bold text-slate-300 hover:text-white bg-[#1E293B] hover:bg-[#283545] border border-[#334155] transition-all cursor-pointer"
              title="Print Road Report"
            >
              <Printer className="w-4 h-4 text-slate-400" />
              <span>Print</span>
            </button>

            <button
              onClick={handleDownloadPdf}
              disabled={isGeneratingPdf}
              className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-mono font-bold text-white shadow-lg cursor-pointer transition-all ${
                downloadSuccess
                  ? "bg-emerald-600 hover:bg-emerald-500 shadow-emerald-900/30"
                  : "bg-[#FF5A00] hover:bg-[#FF5A00]/90 hover:scale-[1.02] shadow-[#FF5A00]/30"
              }`}
            >
              <Download className="w-4 h-4" />
              <span>{downloadSuccess ? "PDF Report Downloaded!" : isGeneratingPdf ? "Building PDF..." : "Download Official PDF Report"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Road Condition Index (PCI) & Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* PCI Health Meter Card */}
        <div className="md:col-span-2 p-5 rounded-xl bg-[#121820] border border-[#283545] space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#FF5A00]" />
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                Pavement Condition Index (PCI)
              </span>
            </div>
            <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${pciRating.bg} ${pciRating.color}`}>
              {pciRating.label}
            </span>
          </div>

          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-extrabold font-mono text-white tracking-tight">
              {pci}
            </span>
            <span className="text-sm font-mono text-slate-400">/ 100</span>
          </div>

          {/* Progress Bar */}
          <div className="space-y-1.5">
            <div className="h-2.5 w-full bg-[#1E293B] rounded-full overflow-hidden p-0.5 border border-[#334155]">
              <div
                className={`h-full rounded-full transition-all duration-700 ${pciRating.bar}`}
                style={{ width: `${Math.max(5, pci)}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] font-mono text-slate-500">
              <span>0 (Failed Pavement)</span>
              <span>50 (Critical Cutoff)</span>
              <span>100 (Flawless Asphalt)</span>
            </div>
          </div>
        </div>

        {/* Potholes Detected */}
        <div className="p-5 rounded-xl bg-[#121820] border border-[#283545] flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Potholes / Craters
            </span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#FF5A00]" />
          </div>
          <div className="mt-3">
            <div className="text-3xl font-extrabold font-mono text-[#FF5A00]">
              {inspection.potholeCount}
            </div>
            <p className="text-[11px] font-mono text-slate-400 mt-1">
              Structural pavement voids
            </p>
          </div>
        </div>

        {/* Cracks Detected */}
        <div className="p-5 rounded-xl bg-[#121820] border border-[#283545] flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Road Surface Cracks
            </span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#FFD200]" />
          </div>
          <div className="mt-3">
            <div className="text-3xl font-extrabold font-mono text-[#FFD200]">
              {inspection.crackCount}
            </div>
            <p className="text-[11px] font-mono text-slate-400 mt-1">
              Alligator &amp; longitudinal
            </p>
          </div>
        </div>
      </div>

      {/* Visual Road Audit Canvas Preview */}
      <div className="rounded-xl bg-[#121820] border border-[#283545] p-5 space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#283545] pb-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#FF5A00]" />
              <span>Annotated Pavement Visual Audit</span>
            </h2>
            <p className="text-xs font-mono text-slate-400 mt-0.5">
              Defect bounding coordinates verified by asphalt drivability filter &amp; surface occlusion guards
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs font-mono">
            <span className="inline-flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-3 rounded-sm bg-[#FF5A00]/20 border border-[#FF5A00]" />
              Potholes ({inspection.potholeCount})
            </span>
            <span className="inline-flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-3 rounded-sm bg-[#FFD200]/20 border border-[#FFD200]" />
              Cracks ({inspection.crackCount})
            </span>
          </div>
        </div>

        {/* Asphalt Canvas Frame */}
        <div className="relative rounded-lg overflow-hidden bg-[#0B0F14] border border-[#283545] max-h-[480px] flex items-center justify-center p-2">
          <div className="relative inline-block leading-none">
            <img
              src={activeImageSrc}
              alt={activeRoadName}
              className="block max-h-[460px] max-w-full object-contain select-none rounded"
            />

            <BoxOverlay
              detections={inspection.boxes.slice(0, 30)}
              activeId={hoveredBoxId ?? selectedBoxId}
              onHover={(id) => setHoveredBoxId(id)}
              onSelect={(id) => setSelectedBoxId((prev) => (prev === id ? null : id))}
              viewMode="boxes"
            />
          </div>
        </div>
      </div>

      {/* Itemized Defect Ledger Table */}
      <div className="rounded-xl bg-[#121820] border border-[#283545] overflow-hidden shadow-sm">
        <div className="p-5 border-b border-[#283545] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#FFD200]" />
              <span>Itemized Road Distress Ledger &amp; Remediation Protocol</span>
            </h2>
            <p className="text-xs font-mono text-slate-400 mt-0.5">
              ASTM D6433 compliant defect register for municipal public works &amp; maintenance contractors
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-[#1E293B] text-slate-300 border border-[#334155] self-start sm:self-auto">
            {inspection.boxes.length} {inspection.boxes.length === 1 ? "Defect" : "Defects"} Identified
          </span>
        </div>

        {inspection.boxes.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <CheckCircle className="w-10 h-10 text-emerald-400 mx-auto" />
            <h3 className="text-base font-bold text-white">No Surface Defects Detected</h3>
            <p className="text-xs font-mono text-slate-400 max-w-md mx-auto">
              This pavement corridor meets surface safety standards. No immediate pothole patching or crack sealing required.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#1E293B] text-slate-300 border-b border-[#283545] uppercase text-[11px]">
                <tr>
                  <th className="py-3 px-4 font-bold text-white">#</th>
                  <th className="py-3 px-4 font-bold text-white">Defect Type</th>
                  <th className="py-3 px-4 font-bold text-white">AI Confidence</th>
                  <th className="py-3 px-4 font-bold text-white">Severity</th>
                  <th className="py-3 px-4 font-bold text-white">Pavement Area</th>
                  <th className="py-3 px-4 font-bold text-white">Wheel Path Zone</th>
                  <th className="py-3 px-4 font-bold text-white">Civil Engineering Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#283545]">
                {inspection.boxes.map((box, index) => {
                  const upper = (box.label || "").toUpperCase();
                  const isCrack = upper.includes("CRACK");
                  const areaPct = box.area_pct ? `${box.area_pct}%` : `${box.areaPx} px`;
                  const wheelPath = getWheelPathLocation(box.box);
                  const action = box.action || getEngineeringAction(box.label, box.severity);

                  return (
                    <tr
                      key={box.id || index}
                      onMouseEnter={() => setHoveredBoxId(box.id)}
                      onMouseLeave={() => setHoveredBoxId(null)}
                      onClick={() => setSelectedBoxId((prev) => (prev === box.id ? null : box.id))}
                      className={`hover:bg-[#1E293B]/80 transition-colors cursor-pointer ${
                        selectedBoxId === box.id ? "bg-[#1E293B] border-l-4 border-[#FF5A00]" : ""
                      }`}
                    >
                      <td className="py-3 px-4 font-bold text-slate-400">
                        {String(index + 1).padStart(2, "0")}
                      </td>
                      <td className="py-3 px-4 font-bold">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] ${
                            isCrack
                              ? "bg-[#FFD200]/15 text-[#FFD200] border border-[#FFD200]/40"
                              : "bg-[#FF5A00]/15 text-[#FF5A00] border border-[#FF5A00]/40"
                          }`}
                        >
                          {isCrack ? "Road Crack" : "Pothole"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-white font-bold">
                        {Math.round(box.confidence * 100)}%
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            box.severity === "Critical"
                              ? "bg-[#FF5A00] text-white"
                              : box.severity === "Severe"
                              ? "bg-[#FFD200] text-[#0B0F14]"
                              : "bg-slate-700 text-slate-200"
                          }`}
                        >
                          {box.severity || "Moderate"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-300">
                        {areaPct}
                      </td>
                      <td className="py-3 px-4 text-slate-300">
                        <span className="flex items-center gap-1.5">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              wheelPath.includes("High Impact")
                                ? "bg-[#FF5A00]"
                                : "bg-[#FFD200]"
                            }`}
                          />
                          {wheelPath}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-200 font-sans text-xs">
                        {action}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Engineering Maintenance & Repair Protocol Box */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-[#121820] border border-[#283545] space-y-3 shadow-sm">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <ShieldCheck className="w-4 h-4 text-[#FF5A00]" />
            <span>Pavement Preservation Standards</span>
          </div>
          <p className="text-xs font-mono text-slate-400 leading-relaxed">
            All defect classifications are mapped to IRC:SP:20 and ASTM D6433 standard defect dictionaries. Potholes occurring within high-impact wheel paths represent active vehicle suspension hazard and tire puncture risk, mandating prioritized cold-mix bituminous repair within 48 hours.
          </p>
          <div className="pt-2 border-t border-[#283545] flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span>IRC Guidelines for Rural Roads &amp; Urban Arterials</span>
            <span className="text-[#FFD200]">Code: IRC 82-2015</span>
          </div>
        </div>

        {/* Dedicated PDF Download Card */}
        <div className="p-5 rounded-xl bg-gradient-to-br from-[#1E293B] to-[#121820] border-2 border-[#FF5A00]/40 flex flex-col justify-between shadow-lg">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Download className="w-4 h-4 text-[#FF5A00]" />
              <span className="text-xs font-mono uppercase font-bold tracking-wider text-white">
                Download Official PDF Audit Report
              </span>
            </div>
            <p className="text-xs font-sans text-slate-300 leading-relaxed">
              Generate a vector-formatted PDF document including municipal road header, inspection metadata, full defect ledger table, and civil repair protocols.
            </p>
          </div>

          <div className="pt-4 flex items-center gap-3">
            <button
              onClick={handleDownloadPdf}
              disabled={isGeneratingPdf}
              className={`w-full py-3 px-4 rounded-xl text-xs font-mono font-bold text-white shadow-lg cursor-pointer transition-all flex items-center justify-center gap-2 ${
                downloadSuccess
                  ? "bg-emerald-600 hover:bg-emerald-500"
                  : "bg-[#FF5A00] hover:bg-[#FF5A00]/90 hover:scale-[1.01]"
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>{downloadSuccess ? "PDF Report Downloaded!" : isGeneratingPdf ? "Generating PDF..." : "Download PDF Report Now"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
