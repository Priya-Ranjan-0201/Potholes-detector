import { jsPDF } from "jspdf";
import { DefectBox } from "./cvDetector";

export interface ReportPayload {
  roadName: string;
  preset: string;
  confThresh: number;
  totalDefects: number;
  potholeCount: number;
  crackCount: number;
  maxSeverity: string;
  overallScore: number;
  latencyMs: number;
  engine?: string;
  boxes: DefectBox[];
  imageSrc?: string;
}

export function generateDistressPDFReport(data: ReportPayload): void {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const now = new Date();
  const reportId = `RSAI-${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}-${Math.floor(1000 + Math.random() * 9000)}`;

  // Colors:
  // Deep Asphalt Black: [11, 15, 20]
  // Slate Charcoal: [30, 41, 59]
  // High-Visibility Safety Orange: [255, 90, 0]
  // Bright Hazard Yellow: [255, 210, 0]
  // Crisp White: [255, 255, 255]
  // Slate Gray: [100, 116, 139]
  // Light Slate Row: [241, 245, 249]

  // Top Asphalt Banner
  doc.setFillColor(11, 15, 20);
  doc.rect(0, 0, pageWidth, 28, "F");

  // High-Visibility Safety Orange Accent Stripe
  doc.setFillColor(255, 90, 0);
  doc.rect(0, 28, pageWidth, 2.5, "F");

  // Bright Hazard Yellow Line
  doc.setFillColor(255, 210, 0);
  doc.rect(0, 30.5, pageWidth, 1, "F");

  // Header Titles
  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.text("ROADSURVEY AI — INFRASTRUCTURE DAMAGE AUDIT REPORT", 14, 12);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.5);
  doc.setTextColor(255, 210, 0);
  doc.text("MUNICIPAL PAVEMENT DEFECT ASSESSMENT & REPAIR ACTION LEDGER", 14, 19);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7.5);
  doc.setTextColor(203, 213, 225);
  doc.text(`REPORT ID: ${reportId}   |   GENERATED: ${now.toLocaleString()}`, 14, 25);

  let y = 38;

  // Metadata Block Card
  doc.setFillColor(248, 250, 252);
  doc.setDrawColor(203, 213, 225);
  doc.roundedRect(14, y, pageWidth - 28, 26, 2, 2, "FD");

  doc.setTextColor(15, 23, 42);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  doc.text("INSPECTION AUDIT METADATA", 18, y + 6);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7.5);
  doc.setTextColor(51, 65, 85);
  doc.text(`Location / Road: ${data.roadName}`, 18, y + 12);
  doc.text(`AI Detection Engine: ${data.engine || "YOLO11n-Rescue + Surface Guards"}`, 18, y + 17);
  doc.text(`Operational Preset: ${data.preset.toUpperCase()} (Sensitivity: ${Math.round(data.confThresh * 100)}%)`, 18, y + 22);

  doc.text(`Inference Latency: ${(data.latencyMs / 1000).toFixed(2)}s`, 120, y + 12);
  doc.text(`Distress Health Score: ${data.overallScore}/100`, 120, y + 17);
  doc.text(`Severity Rating: ${data.maxSeverity.toUpperCase()}`, 120, y + 22);

  y += 32;

  // Key Metrics Summary Cards (4 Columns)
  const colWidth = (pageWidth - 28 - 9) / 4;
  const metrics = [
    { label: "TOTAL DEFECTS", value: String(data.totalDefects), color: [11, 15, 20] },
    { label: "POTHOLES", value: String(data.potholeCount), color: [255, 90, 0] },
    { label: "ROAD CRACKS", value: String(data.crackCount), color: [217, 119, 6] },
    { label: "ROAD STATUS", value: data.maxSeverity, color: data.maxSeverity === "Critical" ? [220, 38, 38] : [16, 185, 129] },
  ];

  metrics.forEach((m, idx) => {
    const x = 14 + idx * (colWidth + 3);
    doc.setFillColor(241, 245, 249);
    doc.setDrawColor(203, 213, 225);
    doc.roundedRect(x, y, colWidth, 18, 1.5, 1.5, "FD");

    doc.setFont("helvetica", "bold");
    doc.setFontSize(6.5);
    doc.setTextColor(100, 116, 139);
    doc.text(m.label, x + 4, y + 6);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(m.color[0], m.color[1], m.color[2]);
    doc.text(m.value, x + 4, y + 14);
  });

  y += 24;

  // Section Heading: Itemized Ledger
  doc.setFont("helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(11, 15, 20);
  doc.text("ITEMIZED ROAD DISTRESS LEDGER & ACTION PROTOCOL", 14, y);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7);
  doc.setTextColor(100, 116, 139);
  doc.text("Every candidate bounding box verified by drivable surface prior and vehicle/pedestrian occlusion blocker.", 14, y + 4.5);

  y += 8;

  // Table Header (Deep Asphalt Charcoal with Crisp White text)
  doc.setFillColor(15, 23, 42);
  doc.rect(14, y, pageWidth - 28, 7, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(7);
  doc.setTextColor(255, 255, 255);

  const headers = [
    { title: "#", x: 17 },
    { title: "Defect Type", x: 26 },
    { title: "Conf.", x: 62 },
    { title: "Severity", x: 77 },
    { title: "Area Px / %", x: 97 },
    { title: "Wheel Path", x: 125 },
    { title: "Recommended Maintenance Action", x: 148 },
  ];

  headers.forEach((h) => doc.text(h.title, h.x, y + 4.8));

  y += 7;

  // Table Body Rows
  if (data.boxes.length === 0) {
    doc.setFillColor(248, 250, 252);
    doc.rect(14, y, pageWidth - 28, 12, "F");
    doc.setDrawColor(226, 232, 240);
    doc.line(14, y + 12, pageWidth - 14, y + 12);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(22, 101, 52);
    doc.text("NO ACTIVE SURFACE DISTRESS DETECTED — ROAD PAVEMENT SATISFACTORY", 20, y + 7.5);
    y += 16;
  } else {
    data.boxes.forEach((b, idx) => {
      // Page break check
      if (y > pageHeight - 22) {
        doc.addPage();
        y = 16;
        // Repeat table header
        doc.setFillColor(15, 23, 42);
        doc.rect(14, y, pageWidth - 28, 7, "F");
        doc.setFont("helvetica", "bold");
        doc.setFontSize(7);
        doc.setTextColor(255, 255, 255);
        headers.forEach((h) => doc.text(h.title, h.x, y + 4.8));
        y += 7;
      }

      // Alternating row background
      const isAlt = idx % 2 === 1;
      doc.setFillColor(isAlt ? 248 : 255, isAlt ? 250 : 255, isAlt ? 252 : 255);
      doc.rect(14, y, pageWidth - 28, 6.5, "F");
      doc.setDrawColor(226, 232, 240);
      doc.line(14, y + 6.5, pageWidth - 14, y + 6.5);

      doc.setFont("helvetica", "normal");
      doc.setFontSize(7);
      doc.setTextColor(51, 65, 85);

      // Index
      doc.text(String(idx + 1), 17, y + 4.5);

      // Defect Type
      const labelUpper = (b.label || "").toUpperCase();
      const defectType = labelUpper.includes("ALLIGATOR")
        ? "Alligator Crack"
        : labelUpper.includes("LONGITUDINAL")
        ? "Long. Crack"
        : labelUpper.includes("TRANSVERSE")
        ? "Trans. Crack"
        : labelUpper.includes("CRACK")
        ? "Road Crack"
        : "Pothole";

      doc.setFont("helvetica", "bold");
      doc.setTextColor(defectType.includes("Crack") ? 180 : 220, defectType.includes("Crack") ? 83 : 38, defectType.includes("Crack") ? 9 : 38);
      doc.text(defectType, 26, y + 4.5);

      // Confidence %
      doc.setFont("helvetica", "normal");
      doc.setTextColor(51, 65, 85);
      doc.text(`${Math.round(b.confidence * 100)}%`, 62, y + 4.5);

      // Severity Badge
      doc.setFont("helvetica", "bold");
      const sevColor = b.severity === "Critical" ? [220, 38, 38] : b.severity === "Severe" ? [234, 88, 12] : b.severity === "Moderate" ? [217, 119, 6] : [71, 85, 105];
      doc.setTextColor(sevColor[0], sevColor[1], sevColor[2]);
      doc.text(b.severity || "Minor", 77, y + 4.5);

      // Area
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 116, 139);
      const areaText = b.area_pct ? `${b.area_pct}%` : `${b.areaPx} px`;
      doc.text(areaText, 97, y + 4.5);

      // Wheel Path Risk
      if (b.wheelPathRisk) {
        doc.setFont("helvetica", "bold");
        doc.setTextColor(220, 38, 38);
        doc.text("HAZARD", 125, y + 4.5);
      } else {
        doc.setFont("helvetica", "normal");
        doc.setTextColor(100, 116, 139);
        doc.text("Safe", 125, y + 4.5);
      }

      // Recommended Maintenance Action
      doc.setFont("helvetica", "normal");
      doc.setTextColor(30, 41, 59);
      const actionText = b.action || (defectType === "Pothole" ? (b.severity === "Critical" ? "Emergency Cold-Mix Asphalt Patch" : "Standard Asphalt Tamping & Patch") : "Bituminous Crack Pouring & Sealant");
      doc.text(actionText.substring(0, 36), 148, y + 4.5);

      y += 6.5;
    });
  }

  // Engineering Recommendations Box
  y += 5;
  if (y > pageHeight - 32) {
    doc.addPage();
    y = 16;
  }

  doc.setFillColor(254, 243, 199); // Soft hazard yellow alert
  doc.setDrawColor(245, 158, 11);
  doc.roundedRect(14, y, pageWidth - 28, 18, 1.5, 1.5, "FD");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(7.5);
  doc.setTextColor(146, 64, 14);
  doc.text("MUNICIPAL CIVIL ENGINEERING RECOMMENDATIONS:", 18, y + 5.5);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7);
  doc.setTextColor(180, 83, 9);
  const recText = data.totalDefects > 0
    ? `Identified ${data.totalDefects} surface defect(s) including ${data.potholeCount} crater(s) and ${data.crackCount} crack distress area(s). Immediate repair prioritization assigned to defects located within vehicle wheel paths to prevent vehicular rim/tire impact claims.`
    : "Pavement surface demonstrates acceptable serviceability. No immediate patching or crack sealing required. Continue routine periodic sensor monitoring.";
  doc.text(recText, 18, y + 10.5, { maxWidth: pageWidth - 36 });

  y += 24;

  // Official Seal / Digital Signature Line
  const footerY = pageHeight - 12;
  doc.setDrawColor(203, 213, 225);
  doc.line(14, footerY - 4, pageWidth - 14, footerY - 4);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(6.5);
  doc.setTextColor(148, 163, 184);
  doc.text("RoadSurvey AI Autonomous Infrastructure Inspection System | Compliant with IRC:82-2015 Road Distress Standards", 14, footerY);
  doc.text(`Page 1 of 1`, pageWidth - 28, footerY);

  // Save the PDF
  const cleanName = data.roadName.replace(/[^a-zA-Z0-9_-]/g, "_");
  doc.save(`RoadSurvey_Audit_Report_${cleanName}_${now.getTime()}.pdf`);
}
