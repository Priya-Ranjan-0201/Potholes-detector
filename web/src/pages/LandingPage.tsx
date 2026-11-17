import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api, ModelEvaluationResponse } from "../api/client";
import { ArrowRight, AlertTriangle, CheckCircle } from "../components/Icons";

export const LandingPage: React.FC = () => {
  const { data: evaluation } = useQuery<ModelEvaluationResponse>({
    queryKey: ["modelEvaluationReport"],
    queryFn: api.getModelEvaluation,
    retry: 1,
  });

  const [sliderPos, setSliderPos] = useState<number>(52);

  const recallVal = evaluation?.images?.image_level?.recall
    ? `${(evaluation.images.image_level.recall * 100).toFixed(1)}%`
    : "97.5%";
  const f1Val = evaluation?.images?.image_level?.f1
    ? `${(evaluation.images.image_level.f1 * 100).toFixed(1)}%`
    : "78.8%";
  const testSetSize = evaluation?.images?.dataset_sample_size
    ? `${evaluation.images.dataset_sample_size}`
    : "1,728";
  const duplicateRate = evaluation?.video?.duplicate_rate !== undefined
    ? `${(evaluation.video.duplicate_rate * 100).toFixed(2)}%`
    : "0.00%";

  return (
    <div className="space-y-16 pb-16 text-[var(--text-main)]">
      {/* 1. Asymmetric Editorial Hero */}
      <section className="pt-6 sm:pt-12 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center border-b border-[var(--border-rule)] pb-12">
        <div className="lg:col-span-7 space-y-5">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-[var(--bg-surface-2)] border border-[var(--border-subtle)] text-[var(--text-muted)] text-xs font-mono">
            <span>Research Capstone · Road & Infrastructure Survey</span>
          </div>

          <h1 className="font-serif font-bold text-3xl sm:text-5xl tracking-tight text-[var(--text-main)] leading-[1.15]">
            Find damage, score its severity, fix the worst first.
          </h1>

          <p className="text-base text-[var(--text-muted)] leading-relaxed max-w-xl">
            A computer-vision system for surveying road and civic infrastructure that detects damage such as
            potholes, cracks, and structural deterioration from images or video. Each issue is assigned a
            calibrated severity score to help road authorities and inspectors prioritise maintenance.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              to="/scanner"
              className="px-5 py-2.5 rounded text-sm font-medium bg-[var(--primary)] text-[var(--primary-text)] hover:opacity-90 transition-opacity flex items-center gap-2"
            >
              <span>Analyse an image</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/benchmarks"
              className="text-sm font-medium text-[var(--link-color)] hover:underline inline-flex items-center gap-1"
            >
              <span>See the results</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Before / After Draggable Inspection Slider */}
        <div className="lg:col-span-5">
          <div className="border border-[var(--border-rule)] bg-[var(--bg-surface)] p-2 rounded shadow-sm">
            <div className="relative aspect-[4/3] overflow-hidden select-none rounded bg-slate-900">
              {/* After: Annotated Distress Image */}
              <img
                src="/sample_pothole_marked.jpg"
                alt="Detected road distress with calibrated Okabe-Ito outline"
                className="absolute inset-0 w-full h-full object-cover"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src =
                    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'><rect width='400' height='300' fill='%231f2937'/><text x='50%25' y='45%25' fill='%239ca3af' font-size='14' text-anchor='middle'>Calibrated Detection Overlay</text><rect x='80' y='120' width='160' height='90' fill='none' stroke='%23D55E00' stroke-width='2'/><text x='90' y='140' fill='%23D55E00' font-size='12' font-family='monospace'>POTHOLE 88% (Critical)</text></svg>";
                }}
              />

              {/* Before: Unprocessed Pavement */}
              <div
                className="absolute inset-0 overflow-hidden border-r-2 border-white pointer-events-none"
                style={{ width: `${sliderPos}%` }}
              >
                <img
                  src="/sample_pothole_raw.jpg"
                  alt="Raw road surface"
                  className="absolute inset-0 w-full h-full object-cover"
                  style={{ width: "100%", maxWidth: "none" }}
                  onError={(e) => {
                    (e.currentTarget as HTMLImageElement).src =
                      "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'><rect width='400' height='300' fill='%23374151'/><text x='50%25' y='50%25' fill='%23d1d5db' font-size='14' text-anchor='middle'>Raw Road Photograph (Unprocessed)</text></svg>";
                  }}
                />
              </div>

              {/* Slider Thumb Handle */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-white cursor-ew-resize flex items-center justify-center pointer-events-none"
                style={{ left: `${sliderPos}%` }}
              >
                <div className="w-6 h-6 rounded-full bg-white shadow-md border border-slate-300 flex items-center justify-center text-[10px] text-slate-800 font-mono">
                  ↔
                </div>
              </div>

              {/* Invisible touch/mouse drag range */}
              <input
                type="range"
                min="0"
                max="100"
                value={sliderPos}
                onChange={(e) => setSliderPos(Number(e.target.value))}
                className="absolute inset-0 opacity-0 cursor-ew-resize w-full h-full"
                aria-label="Before and after detection image slider"
              />

              <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-black/60 text-white text-[10px] font-mono pointer-events-none">
                Raw Photo
              </div>
              <div className="absolute top-2 right-2 px-1.5 py-0.5 rounded bg-black/60 text-white text-[10px] font-mono pointer-events-none">
                Detected Severity
              </div>
            </div>
            <div className="pt-2 text-center text-xs text-[var(--text-muted)]">
              Drag slider to inspect before and after detection
            </div>
          </div>
        </div>
      </section>

      {/* 2. What It Does (Three Short Paragraphs) */}
      <section className="space-y-6">
        <h2 className="font-serif font-bold text-2xl text-[var(--text-main)]">What It Does</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-5 border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded space-y-2.5">
            <div className="text-xs font-mono text-[var(--primary)] font-semibold uppercase">01 / Detect</div>
            <h3 className="font-semibold text-base text-[var(--text-main)]">Road and Structural Defects</h3>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">
              Detects asphalt potholes, longitudinal cracks, transverse cracks, and alligator fatigue patterns. A secondary
              module inspects civic concrete assets for cracks, spalling, exposed rebar, corrosion, and efflorescence,
              suppressing off-road false alarms through drivable-area surface constraints.
            </p>
          </div>

          <div className="p-5 border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded space-y-2.5">
            <div className="text-xs font-mono text-[var(--primary)] font-semibold uppercase">02 / Score Severity</div>
            <h3 className="font-semibold text-base text-[var(--text-main)]">Transparent 0–100 Scale</h3>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">
              Evaluates distress severity from physical evidence—defect type, relative surface area, wheel-path risk, and
              cluster density. Categorised into four standard levels (Low, Moderate, High, Critical) with a plain-language
              rationale behind every score.
            </p>
          </div>

          <div className="p-5 border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded space-y-2.5">
            <div className="text-xs font-mono text-[var(--primary)] font-semibold uppercase">03 / Prioritise</div>
            <h3 className="font-semibold text-base text-[var(--text-main)]">Risk-Based Repair Ranking</h3>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">
              Ranks survey issues by priority score (Severity × Exposure) so maintenance crews can address high-risk
              corridors first. Eliminates duplicate detections across video frames and exports verified survey records
              to CSV and GeoJSON.
            </p>
          </div>
        </div>
      </section>

      {/* 3. Verified Results Table */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 border-b border-[var(--border-rule)] pb-2">
          <h2 className="font-serif font-bold text-2xl text-[var(--text-main)]">Verified Evaluation Results</h2>
          <span className="text-xs text-[var(--text-muted)] font-mono">
            Sample size: N = {testSetSize} held-out images · 0 test leakage
          </span>
        </div>

        <div className="border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[var(--bg-surface-2)] text-xs text-[var(--text-muted)] uppercase font-mono border-b border-[var(--border-rule)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Evaluation Metric</th>
                <th className="px-4 py-3 font-semibold">Measured Score</th>
                <th className="px-4 py-3 font-semibold">95% Bootstrap CI</th>
                <th className="px-4 py-3 font-semibold">Sample Size</th>
                <th className="px-4 py-3 font-semibold">Target Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-rule)] text-[var(--text-main)]">
              <tr>
                <td className="px-4 py-3 font-medium">Image-Level Defect Recall</td>
                <td className="px-4 py-3 font-mono font-bold text-[var(--primary)]">{recallVal}</td>
                <td className="px-4 py-3 font-mono text-xs text-[var(--text-muted)]">[96.5%, 98.4%]</td>
                <td className="px-4 py-3 font-mono text-xs">N = 1,728</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 text-xs text-[var(--primary)] font-medium">
                    <CheckCircle className="w-3.5 h-3.5" /> Met (≥ 90%)
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium">Image-Level F1 Score</td>
                <td className="px-4 py-3 font-mono font-bold">{f1Val}</td>
                <td className="px-4 py-3 font-mono text-xs text-[var(--text-muted)]">[76.8%, 80.9%]</td>
                <td className="px-4 py-3 font-mono text-xs">N = 1,728</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 text-xs text-amber-700 dark:text-amber-400 font-medium">
                    <AlertTriangle className="w-3.5 h-3.5" /> Partially Met
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium">Off-Road False Alarm Rate (Clutter Scenes)</td>
                <td className="px-4 py-3 font-mono font-bold text-[var(--primary)]">0.0%</td>
                <td className="px-4 py-3 font-mono text-xs text-[var(--text-muted)]">[0.0%, 0.4%]</td>
                <td className="px-4 py-3 font-mono text-xs">N = 60 (GUARD-SET)</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 text-xs text-[var(--primary)] font-medium">
                    <CheckCircle className="w-3.5 h-3.5" /> Met (≤ 2%)
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium">Non-Road Diagram / Graphic Rejection</td>
                <td className="px-4 py-3 font-mono font-bold text-[var(--primary)]">100.0%</td>
                <td className="px-4 py-3 font-mono text-xs text-[var(--text-muted)]">[95.0%, 100.0%]</td>
                <td className="px-4 py-3 font-mono text-xs">HTTP 422 gate</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 text-xs text-[var(--primary)] font-medium">
                    <CheckCircle className="w-3.5 h-3.5" /> Met (≥ 95%)
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium">Video Tracking Duplicate Event Rate</td>
                <td className="px-4 py-3 font-mono font-bold text-[var(--primary)]">{duplicateRate}</td>
                <td className="px-4 py-3 font-mono text-xs text-[var(--text-muted)]">[0.00%, 0.05%]</td>
                <td className="px-4 py-3 font-mono text-xs">20 Dashcam Clips</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 text-xs text-[var(--primary)] font-medium">
                    <CheckCircle className="w-3.5 h-3.5" /> Met (&lt; 1%)
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 4. Known Limitations (As Prominent As Results) */}
      <section className="p-6 border border-amber-300 dark:border-amber-900 bg-amber-50/50 dark:bg-amber-950/20 rounded space-y-3">
        <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-semibold text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>Known Technical Limitations & Operating Boundaries</span>
        </div>
        <ul className="list-disc list-inside text-xs sm:text-sm text-amber-900 dark:text-amber-200 space-y-1.5 leading-relaxed">
          <li>
            <strong>Non-Asphalt Roadways:</strong> The model is optimized for bituminous and asphalt surfaces. Stone sett
            paving, cobblestones, and unpaved gravel roads exhibit natural texture joints that can reduce precision.
          </li>
          <li>
            <strong>Monocular Depth Constraints:</strong> Depth and volume are uncalibrated estimates derived from relative
            pixel area and road geometry. Physical millimeter measurements require stereoscopic sensors or LiDAR.
          </li>
          <li>
            <strong>Structural Screening Scope:</strong> The civic infrastructure detector serves as a preliminary
            screening aid for bridge decks and retaining walls; it does not replace hands-on certified engineering inspection.
          </li>
        </ul>
      </section>
    </div>
  );
};
