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
  action?: string;
  wheelPathRisk?: boolean;
  depthIndicator?: "Shallow" | "Medium" | "Deep";
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

/**
 * Runs defect detection on an image File, Blob, or URL.
 */
export async function detectDefects(
  imageSource: File | Blob | string,
  confThresh: number = 0.30,
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

    const apiRes = await fetch(`/api/v1/infer?conf_thresh=${confThresh}`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

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
        action: d.action,
        wheelPathRisk: d.wheel_path_risk,
        depthIndicator: d.depth_indicator,
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
        engine: data.engine || "Calibrated Multi-Model Ensemble",
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
        ? "ScamRoad inference backend not reached on port 8000. Ensure the server is running."
        : apiRes.status === 422
        ? `Image issue: ${detail}`
        : `Backend error (HTTP ${apiRes.status}): ${detail || apiRes.statusText}`;

    console.error("[ScamRoad AI] Inference API error:", apiRes.status, detail);
    return {
      source: "neural_api",
      totalDefects: 0,
      potholeCount: 0,
      crackCount: 0,
      maxSeverity: "Minor",
      overallScore: 100,
      boxes: [],
      latencyMs: Math.round(performance.now() - startTime),
      engine: "Calibrated Multi-Model Ensemble",
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

    console.warn("[ScamRoad AI] Inference API connection issue:", err);
    return {
      source: "neural_api",
      totalDefects: 0,
      potholeCount: 0,
      crackCount: 0,
      maxSeverity: "Minor",
      overallScore: 100,
      boxes: [],
      latencyMs: Math.round(performance.now() - startTime),
      engine: "Calibrated Multi-Model Ensemble",
      error: message,
    };
  }
}
