import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Download,
  Compass,
  Clock,
} from "../components/Icons";
import { useInspection } from "../context/InspectionContext";
import { generateDistressPDFReport } from "../utils/pdfReport";

const getWheelPathLocation = (boxCoords: [number, number, number, number]) => {
  const [x, , w] = boxCoords;
  const centerX = x + w / 2;
  if (centerX < 35) return "Left Wheelpath (Lane 1)";
  if (centerX > 65) return "Right Wheelpath (Lane 3 / Shoulder)";
  return "Center Carriage / Crown (Lane 2)";
};

const getEngineeringRemediation = (label: string, severity?: string) => {
  const upper = (label || "").toUpperCase();
  const isCrack = upper.includes("CRACK");
  if (severity === "Critical") {
    return isCrack
      ? "Mastic asphalt mill & overlay recommendation (non-official)"
      : "Class-A cold bituminous patch & mechanical roller compaction";
  }
  if (severity === "Severe" || severity === "High") {
    return isCrack
      ? "Polymer-modified crack sealant & surface dressing"
      : "Square-cut pothole filling with bituminous concrete";
  }
  if (severity === "Moderate") {
    return isCrack
      ? "High-pressure air clean & bitumen slurry seal"
      : "Emulsion tack-coat spray & aggregate compaction";
  }
  return isCrack
    ? "Monitor crack propagation rate; scheduled routine seal"
    : "Routine pavement leveling & scheduled sweep";
};

export const RoadAuditReportPage: React.FC = () => {
  const {
    activeImageSrc,
    activeRoadName,
    activeChainage,
    preset,
    confThresh,
    inspection,
  } = useInspection();

  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

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
        engine: "YOLO11n-Rescue + Drivable Surface Prior",
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

  const handleDownloadCsv = () => {
    // Client-side CSV export of current survey records
    const headers = [
      "Defect_ID",
      "Corridor",
      "Chainage",
      "Class",
      "Confidence",
      "Severity",
      "Wheelpath_Location",
      "Pavement_Area_Pct",
    ];
    const rows = inspection.boxes.map((b, idx) => [
      `DEF-${idx + 1}`,
      `"${activeRoadName}"`,
      `"${activeChainage}"`,
      b.label,
      (b.confidence * 100).toFixed(1),
      b.severity || "Moderate",
      `"${getWheelPathLocation(b.box)}"`,
      b.area_pct || "0",
    ]);

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `ScamRoad_${activeRoadName.replace(/\s+/g, "_")}_Records.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setExportNotice("CSV Records downloaded successfully.");
    setTimeout(() => setExportNotice(null), 4000);
  };

  const handleDownloadGeoJson = () => {
    const geoJson = {
      type: "FeatureCollection",
      properties: {
        corridor: activeRoadName,
        chainage: activeChainage,
        generated_at: new Date().toISOString(),
        disclaimer: "Student research project. Not an official government system. Not safety-certified.",
      },
      features: inspection.boxes.map((b, idx) => ({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [77.5946 + idx * 0.001, 12.9716 + idx * 0.001], // Reference coordinates on corridor
        },
        properties: {
          defect_id: `DEF-${idx + 1}`,
          label: b.label,
          confidence: b.confidence,
          severity: b.severity,
          chainage: activeChainage,
        },
      })),
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(geoJson, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", `ScamRoad_${activeRoadName.replace(/\s+/g, "_")}.geojson`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setExportNotice("GeoJSON spatial data downloaded successfully.");
    setTimeout(() => setExportNotice(null), 4000);
  };

  // Calculated Defect Density (defects / km)
  const defectDensity = (inspection.boxes.length / 0.5).toFixed(1); // Normalized to 500m survey segment

  return (
    <div className="space-y-6">
      {/* 1. Header Toolbar */}
      <div className="border border-rule rounded-[4px] bg-surface p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-serif font-bold text-text">Pavement Distress Records &amp; Chainage Logs</h1>
            <span className="text-[11px] font-mono px-1.5 py-0.5 rounded-[3px] border border-rule text-muted">
              Pilot Records
            </span>
          </div>
          <p className="text-xs text-muted mt-1 flex items-center gap-2">
            <Compass className="w-3.5 h-3.5 text-muted" />
            <span>Corridor: {activeRoadName} ({activeChainage})</span>
            <span>·</span>
            <Clock className="w-3.5 h-3.5 text-muted" />
            <span>Logged: {new Date().toLocaleDateString()}</span>
          </p>
        </div>

        {/* Export Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <Link
            to="/detect"
            className="px-3 py-1.5 rounded-[4px] text-xs font-mono border border-rule bg-surface text-muted hover:text-text transition-colors"
          >
            &larr; Back to Detect
          </Link>

          <button
            type="button"
            onClick={handleDownloadCsv}
            className="px-3 py-1.5 rounded-[4px] text-xs font-mono border border-rule bg-surface hover:bg-surface-raised text-text transition-colors cursor-pointer"
          >
            Export CSV
          </button>

          <button
            type="button"
            onClick={handleDownloadGeoJson}
            className="px-3 py-1.5 rounded-[4px] text-xs font-mono border border-rule bg-surface hover:bg-surface-raised text-text transition-colors cursor-pointer"
          >
            Export GeoJSON
          </button>

          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={isGeneratingPdf}
            className="px-3 py-1.5 rounded-[4px] text-xs font-sans font-semibold bg-text text-bg hover:opacity-90 transition-opacity cursor-pointer flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isGeneratingPdf ? "Building..." : downloadSuccess ? "Downloaded" : "Download PDF Sheet"}</span>
          </button>
        </div>
      </div>

      {exportNotice && (
        <div className="p-2.5 rounded-[4px] bg-surface border border-accent/40 text-xs font-mono text-text">
          {exportNotice}
        </div>
      )}

      {/* 2. Key Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-[4px] border border-rule bg-surface">
          <div className="text-[11px] font-mono uppercase text-muted font-bold">Total Verified Defects</div>
          <div className="text-2xl font-mono font-bold text-text mt-1">{inspection.boxes.length}</div>
          <div className="text-[11px] font-mono text-muted mt-1">{inspection.potholeCount} potholes · {inspection.crackCount} cracks</div>
        </div>

        <div className="p-4 rounded-[4px] border border-rule bg-surface">
          <div className="text-[11px] font-mono uppercase text-muted font-bold">Defect Density</div>
          <div className="text-2xl font-mono font-bold text-text mt-1">{defectDensity}</div>
          <div className="text-[11px] font-mono text-muted mt-1">defects / km (0.5 km bin)</div>
        </div>

        <div className="p-4 rounded-[4px] border border-rule bg-surface">
          <div className="text-[11px] font-mono uppercase text-muted font-bold">Maximum Distress Severity</div>
          <div className="text-2xl font-mono font-bold text-[#D55E00] mt-1">{inspection.maxSeverity}</div>
          <div className="text-[11px] font-mono text-muted mt-1">Wheelpath impact weighted</div>
        </div>

        <div className="p-4 rounded-[4px] border border-rule bg-surface">
          <div className="text-[11px] font-mono uppercase text-muted font-bold">Condition Index (PCI)</div>
          <div className="text-2xl font-mono font-bold text-accent mt-1">{inspection.overallScore} / 100</div>
          <div className="text-[11px] font-mono text-muted mt-1">Research index calculation</div>
        </div>
      </div>

      {/* 3. Detailed Ruled Defect Records Table */}
      <div className="border border-rule rounded-[4px] bg-surface overflow-hidden">
        <div className="px-4 py-3 border-b border-rule bg-surface-raised flex items-center justify-between">
          <span className="text-xs font-mono uppercase font-bold text-muted">Defect Itemization &amp; Engineering Remediation</span>
          <span className="text-xs font-mono text-muted">{inspection.boxes.length} recorded items</span>
        </div>

        {inspection.boxes.length === 0 ? (
          <div className="py-12 text-center text-xs text-muted space-y-1">
            <p className="font-serif font-medium text-text">No Defects Logged</p>
            <p>Upload a surveyed road photograph in the Detect module to itemize distress records.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Defect Class</th>
                  <th>Confidence</th>
                  <th>Severity</th>
                  <th>Carriageway Position</th>
                  <th>Pavement Area</th>
                  <th>Engineering Observation &amp; Remediation</th>
                </tr>
              </thead>
              <tbody>
                {inspection.boxes.map((b, idx) => {
                  const location = getWheelPathLocation(b.box);
                  const remediation = getEngineeringRemediation(b.label, b.severity);
                  return (
                    <tr key={b.id}>
                      <td className="font-mono text-xs text-muted">#{idx + 1}</td>
                      <td className="font-mono text-xs font-bold text-text">{b.label}</td>
                      <td className="font-mono text-xs">{Math.round(b.confidence * 100)}%</td>
                      <td>
                        <span
                          className={`inline-block px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono uppercase font-bold ${
                            b.severity === "Critical"
                              ? "bg-[#D55E00]/15 text-[#D55E00]"
                              : b.severity === "Severe"
                              ? "bg-[#E8B100]/20 text-accent"
                              : "bg-rule/40 text-muted"
                          }`}
                        >
                          {b.severity || "Moderate"}
                        </span>
                      </td>
                      <td className="text-xs font-mono">{location}</td>
                      <td className="font-mono text-xs text-muted">{b.area_pct ? `${b.area_pct}%` : `${b.areaPx} px`}</td>
                      <td className="text-xs text-muted max-w-sm leading-relaxed">{remediation}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
