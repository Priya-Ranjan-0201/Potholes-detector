/**
 * ScamRoad Computer Vision API Detector Client
 * Sends road frames to the FastAPI 70/30 ensemble inference endpoint.
 */

export interface DefectBox {
  id: string;
  label: string;
  confidence: number;
  box: [number, number, number, number]; // [x%, y%, w%, h%]
  polygon?: [number, number][]; // [[x%, y%], ...] non-intersecting contour
  severity: "Critical" | "Severe" | "Moderate" | "Minor";
  score: number;
  areaPx: number;
  area_pct?: number;
  action?: string;
  wheelPathRisk?: boolean;
  depthIndicator?: "Shallow" | "Medium" | "Deep";
  severity_breakdown?: string;
  repair_status?: string;
  priority_score?: number;
  modelSource?: string;
}

export interface InspectionResult {
  source: "neural_api" | "edge_cv";
  totalDefects: number;
  potholeCount: number;
  crackCount: number;
  maxSeverity: "Critical" | "Severe" | "Moderate" | "Minor";
  overallScore: number;
  boxes: DefectBox[];
  latencyMs: number;
  imageWidth?: number;
  imageHeight?: number;
  engine?: string;
  error?: string;
}

export type DetectionPreset = "balanced" | "high_precision" | "high_recall";

/**
 * Runs defect detection on an image File, Blob, or URL.
 */
export async function detectDefects(
  imageSource: File | Blob | string,
  confThresh: number = 0.25,
  preset: DetectionPreset = "balanced",
  onStageChange?: (stage: "preprocess" | "inference" | "postprocess") => void,
  externalSignal?: AbortSignal
): Promise<InspectionResult> {
  const startTime = performance.now();
  onStageChange?.("preprocess");

  try {
    let blob: Blob;
    if (typeof imageSource === "string") {
      const res = await fetch(imageSource, { signal: externalSignal });
      if (!res.ok) {
        throw new Error(`Failed to load image (${res.status} ${res.statusText})`);
      }
      blob = await res.blob();
    } else {
      blob = imageSource;
    }

    const fileName =
      imageSource instanceof File && imageSource.name ? imageSource.name : "upload.jpg";
    const formData = new FormData();
    formData.append("file", blob, fileName);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 35000);
    if (externalSignal) {
      if (externalSignal.aborted) {
        controller.abort();
      } else {
        externalSignal.addEventListener("abort", () => controller.abort(), { once: true });
      }
    }

    onStageChange?.("inference");

    let apiRes: Response | null = null;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        apiRes = await fetch(`/api/v1/infer?conf_thresh=${confThresh}&preset=${preset}`, {
          method: "POST",
          body: formData,
          signal: controller.signal,
        });
        if (apiRes.ok || apiRes.status === 422) {
          break;
        }
        if (attempt === 0 && apiRes.status >= 500) {
          await new Promise((r) => setTimeout(r, 350));
        }
      } catch (err: any) {
        if (attempt === 0 && err?.name !== "AbortError") {
          await new Promise((r) => setTimeout(r, 350));
          continue;
        }
        throw err;
      }
    }
    clearTimeout(timeoutId);

    if (!apiRes) {
      throw new Error("No response received from inference backend.");
    }

    onStageChange?.("postprocess");

    if (apiRes.ok) {
      const data = await apiRes.json();
      const latency = data.latency_ms ?? Math.round(performance.now() - startTime);

      const boxes: DefectBox[] = (data.detections || []).map((d: any) => ({
        id: d.id,
        label: d.label,
        confidence: d.confidence,
        box: d.box as [number, number, number, number],
        polygon: d.polygon as [number, number][] | undefined,
        severity: d.severity,
        score: d.score,
        areaPx: d.areaPx,
        area_pct: d.area_pct,
        action: d.action,
        wheelPathRisk: d.wheel_path_risk,
        depthIndicator: d.depth_indicator,
        severity_breakdown: d.severity_breakdown,
        repair_status: d.repair_status,
        priority_score: d.priority_score,
        modelSource: d.model_source,
      }));

      return {
        source: "neural_api",
        totalDefects: data.total_defects ?? boxes.length,
        potholeCount:
          data.pothole_count ?? boxes.filter((b) => (b.label || "").includes("POTHOLE")).length,
        crackCount:
          data.crack_count ?? boxes.filter((b) => (b.label || "").includes("CRACK")).length,
        maxSeverity: data.max_severity || (boxes.length > 0 ? boxes[0].severity : "Minor"),
        overallScore: data.overall_health_score ?? (boxes.length > 0 ? boxes[0].score : 100),
        boxes,
        latencyMs: latency,
        imageWidth: data.image_width,
        imageHeight: data.image_height,
        engine: data.engine || "Unified YOLO11n-Rescue + Guarded Surface Prior",
      };
    }

    let detail = "";
    try {
      const errJson = await apiRes.json();
      detail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      detail = await apiRes.text().catch(() => "");
    }

    const errorMsg =
      apiRes.status === 404
        ? "RoadSurvey AI inference backend not reached on port 8000. Ensure python scripts/serve_inference.py is running."
        : apiRes.status === 422
        ? `Image issue: ${detail}`
        : `Backend error (HTTP ${apiRes.status}): ${detail || apiRes.statusText}`;

    console.error("[RoadSurvey AI] Inference API error:", apiRes.status, detail);
    return {
      source: "neural_api",
      totalDefects: 0,
      potholeCount: 0,
      crackCount: 0,
      maxSeverity: "Minor",
      overallScore: 100,
      boxes: [],
      latencyMs: Math.round(performance.now() - startTime),
      engine: "Unified YOLO11n-Rescue + Guarded Surface Prior",
      error: errorMsg,
    };
  } catch (err: any) {
    if (err?.name === "AbortError") {
      throw err;
    }
    const message =
      err?.message?.includes("Failed to fetch") || err?.name === "TypeError"
        ? "Cannot connect to backend server on port 8000. Is python scripts/serve_inference.py running?"
        : err?.message || "Inference failed due to a network connection issue.";

    console.warn("[RoadSurvey AI] Inference API connection issue:", err);
    return {
      source: "neural_api",
      totalDefects: 0,
      potholeCount: 0,
      crackCount: 0,
      maxSeverity: "Minor",
      overallScore: 100,
      boxes: [],
      latencyMs: Math.round(performance.now() - startTime),
      engine: "Unified YOLO11n-Rescue + Guarded Surface Prior",
      error: message,
    };
  }
}
