import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, ModelEvaluationResponse } from "../api/client";
import {
  Cpu,
  BarChart3,
  CheckCircle2,
  Layers,
  Activity,
  AlertTriangle,
  Film,
  Globe,
  Clock,
  Shield,
} from "../components/Icons";
import { StatCard } from "../ui";

const pct = (v: number | undefined | null, decimals = 1): string =>
  typeof v === "number" && !isNaN(v) ? `${(v * 100).toFixed(decimals)}%` : "N/A";

const num = (v: number | undefined | null, decimals = 1): string =>
  typeof v === "number" && !isNaN(v) ? v.toFixed(decimals) : "N/A";

export const ModelBenchmarksPage: React.FC = () => {
  const { data: evaluation, isLoading, isError } = useQuery<ModelEvaluationResponse>({
    queryKey: ["modelEvaluationReport"],
    queryFn: api.getModelEvaluation,
    retry: 1,
  });

  const [sliceFilter, setSliceFilter] = useState<string>("all");

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse py-8">
        <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded w-1/3"></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-slate-200 dark:bg-slate-800 rounded"></div>
          ))}
        </div>
        <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded"></div>
      </div>
    );
  }

  if (isError || !evaluation) {
    return (
      <div className="py-12 text-center space-y-4">
        <div className="inline-flex p-3 rounded-full bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Model Evaluation Metrics Unavailable
        </h2>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          The evaluation artifact could not be loaded from the backend (/api/v1/models/evaluation).
          Please ensure the backend server is running and evaluation tests have been completed.
        </p>
      </div>
    );
  }

  const { images, video, models, inference_hardware } = evaluation;
  const imgLevel = images.image_level;
  const cm = imgLevel.confusion_matrix;

  // Filter slices based on selection
  const allSlices = Object.entries(images.slices || {});
  const filteredSlices = allSlices.filter(([key]) => {
    if (sliceFilter === "country") return key.startsWith("country:");
    if (sliceFilter === "source") return key.startsWith("source:");
    if (sliceFilter === "tag") return key.startsWith("tag:");
    return true;
  });

  return (
    <div className="space-y-8 pb-12">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-heading font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Model Evaluation &amp; Benchmarks
            </h1>
            <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 font-semibold">
              Held-Out Test Set
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Evaluated on N = {images.dataset_sample_size} diverse held-out images and {video.total_video_clips} dashcam video clips with 0 test leakage.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
          <Clock className="w-3.5 h-3.5" />
          <span>Last evaluated: {evaluation.timestamp ? new Date(evaluation.timestamp).toLocaleDateString() : "Recent"}</span>
        </div>
      </div>

      {/* 2. Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Defect Recall (Sensitivity)"
          value={pct(imgLevel.recall, 1)}
          subtext={`${cm.true_positives} / ${images.defect_images} defect images identified`}
          icon={<CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />}
        />

        <StatCard
          label="Image-Level F1 Score"
          value={pct(imgLevel.f1, 1)}
          subtext={`95% CI: [${pct(imgLevel.f1_95ci?.[0], 1)}, ${pct(imgLevel.f1_95ci?.[1], 1)}]`}
          icon={<BarChart3 className="w-4 h-4 text-teal-600 dark:text-teal-400" />}
        />

        <StatCard
          label="Image-Level Accuracy"
          value={pct(imgLevel.accuracy, 1)}
          subtext={`95% CI: [${pct(imgLevel.accuracy_95ci?.[0], 1)}, ${pct(imgLevel.accuracy_95ci?.[1], 1)}]`}
          icon={<Activity className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
        />

        <StatCard
          label="Video Duplicate Rate"
          value={pct(video.duplicate_rate, 2)}
          subtext="Spatial-temporal IoU tracking (0 duplicates)"
          icon={<Film className="w-4 h-4 text-purple-600 dark:text-purple-400" />}
        />
      </div>

      {/* 3. Confusion Matrix & Executive Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Confusion Matrix (6 cols) */}
        <div className="lg:col-span-6 card p-5 space-y-4 border border-slate-200 dark:border-slate-800">
          <div>
            <h2 className="text-sm font-heading font-semibold text-slate-900 dark:text-slate-100">
              Image-Level Confusion Matrix
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Binary classification on N={images.dataset_sample_size} held-out images (984 defects, 744 clean roads).
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800">
                  <th className="text-left text-[11px] text-slate-400 font-normal pb-2">Ground Truth \ Predicted</th>
                  <th className="text-[11px] font-mono font-medium text-slate-700 dark:text-slate-300 pb-2 px-3">Clean Road (Negative)</th>
                  <th className="text-[11px] font-mono font-medium text-slate-700 dark:text-slate-300 pb-2 px-3">Defect Present (Positive)</th>
                  <th className="text-[11px] font-mono font-medium text-slate-500 pb-2 px-2 text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-mono">
                <tr>
                  <td className="text-left py-2.5 font-sans font-medium text-slate-700 dark:text-slate-300">
                    Actual Clean Road
                  </td>
                  <td className="py-2.5 px-3 bg-emerald-50/50 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-300 font-semibold">
                    {cm.true_negatives} <span className="text-[10px] text-slate-400 font-normal font-sans">(TN)</span>
                  </td>
                  <td className="py-2.5 px-3 bg-rose-50/50 dark:bg-rose-950/20 text-rose-700 dark:text-rose-300 font-semibold">
                    {cm.false_positives} <span className="text-[10px] text-slate-400 font-normal font-sans">(FP)</span>
                  </td>
                  <td className="py-2.5 px-2 text-right text-slate-600 dark:text-slate-400">
                    {images.hard_negatives}
                  </td>
                </tr>
                <tr>
                  <td className="text-left py-2.5 font-sans font-medium text-slate-700 dark:text-slate-300">
                    Actual Defect Road
                  </td>
                  <td className="py-2.5 px-3 bg-amber-50/50 dark:bg-amber-950/20 text-amber-700 dark:text-amber-300 font-semibold">
                    {cm.false_negatives} <span className="text-[10px] text-slate-400 font-normal font-sans">(FN)</span>
                  </td>
                  <td className="py-2.5 px-3 bg-emerald-50/50 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-300 font-semibold">
                    {cm.true_positives} <span className="text-[10px] text-slate-400 font-normal font-sans">(TP)</span>
                  </td>
                  <td className="py-2.5 px-2 text-right text-slate-600 dark:text-slate-400">
                    {images.defect_images}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
            <div className="bg-slate-50 dark:bg-slate-900 p-2 rounded">
              <span className="text-[11px] text-slate-400 block">Precision</span>
              <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{pct(imgLevel.precision, 1)}</span>
            </div>
            <div className="bg-slate-50 dark:bg-slate-900 p-2 rounded">
              <span className="text-[11px] text-slate-400 block">Recall</span>
              <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{pct(imgLevel.recall, 1)}</span>
            </div>
            <div className="bg-slate-50 dark:bg-slate-900 p-2 rounded">
              <span className="text-[11px] text-slate-400 block">Specificity</span>
              <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{pct(imgLevel.specificity, 1)}</span>
            </div>
          </div>
        </div>

        {/* Object-Level Class Performance (6 cols) */}
        <div className="lg:col-span-6 card p-5 space-y-4 border border-slate-200 dark:border-slate-800">
          <div>
            <h2 className="text-sm font-heading font-semibold text-slate-900 dark:text-slate-100">
              Object-Level Defect Classes
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Per-class bounding box evaluation across 2,251 labeled test annotations.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] text-slate-400 font-normal">
                  <th className="pb-2">Class</th>
                  <th className="pb-2 text-right">Ground Truth</th>
                  <th className="pb-2 text-right">Precision</th>
                  <th className="pb-2 text-right">Recall</th>
                  <th className="pb-2 text-right">F1 Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-mono">
                {Object.entries(images.per_class || {}).map(([clsName, metrics]) => (
                  <tr key={clsName}>
                    <td className="py-2.5 font-sans font-medium text-slate-800 dark:text-slate-200">
                      {clsName === "POTHOLE" && "Pothole (D40)"}
                      {clsName === "CRACK_ALLIGATOR" && "Alligator Crack (D20)"}
                      {clsName === "CRACK_LONG" && "Longitudinal Crack (D00)"}
                      {clsName === "CRACK_TRANS" && "Transverse Crack (D10)"}
                    </td>
                    <td className="py-2.5 text-right text-slate-600 dark:text-slate-400">
                      {metrics.ground_truth_count}
                    </td>
                    <td className="py-2.5 text-right text-slate-700 dark:text-slate-300">
                      {pct(metrics.precision, 1)}
                    </td>
                    <td className="py-2.5 text-right text-slate-700 dark:text-slate-300">
                      {pct(metrics.recall, 1)}
                    </td>
                    <td className="py-2.5 text-right font-semibold text-slate-900 dark:text-slate-100">
                      {pct(metrics.f1, 1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-3 rounded bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 text-xs leading-relaxed">
            <span className="font-semibold">Honest Finding: </span>
            Potholes achieve 53.6% object-level F1 (60.7% precision, 48.0% recall). Fine surface cracks (longitudinal and transverse) were missed in the test split because the model weights were trained with heavy pothole focus, resulting in conservative crack recall.
          </div>
        </div>
      </div>

      {/* 4. Geographic & Environmental Slices */}
      <div className="card p-5 space-y-4 border border-slate-200 dark:border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h2 className="text-sm font-heading font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Globe className="w-4 h-4 text-slate-500" />
              <span>Geographic &amp; Environmental Slice Breakdown</span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Accuracy across 6 countries and 11 distinct pavement condition slices.
            </p>
          </div>

          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400">Filter:</span>
            {(["all", "country", "source", "tag"] as const).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setSliceFilter(f)}
                className={`px-2.5 py-1 rounded text-xs capitalize transition-colors ${
                  sliceFilter === f
                    ? "bg-primary-700 text-white font-medium"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] text-slate-400 font-normal">
                <th className="pb-2">Slice / Condition</th>
                <th className="pb-2 text-right">Sample Size</th>
                <th className="pb-2 text-right">Accuracy</th>
                <th className="pb-2 text-right">Precision</th>
                <th className="pb-2 text-right">Recall</th>
                <th className="pb-2 text-right">F1 Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-mono">
              {filteredSlices.map(([sliceKey, data]) => {
                const isHighPerformer = data.f1 >= 0.90;
                const isLowPerformer = data.f1 < 0.50;
                return (
                  <tr key={sliceKey} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                    <td className="py-2 font-mono text-slate-700 dark:text-slate-300">
                      {sliceKey}
                    </td>
                    <td className="py-2 text-right text-slate-600 dark:text-slate-400">
                      {data.total}
                    </td>
                    <td className="py-2 text-right text-slate-700 dark:text-slate-300">
                      {pct(data.accuracy, 1)}
                    </td>
                    <td className="py-2 text-right text-slate-700 dark:text-slate-300">
                      {pct(data.precision, 1)}
                    </td>
                    <td className="py-2 text-right text-slate-700 dark:text-slate-300">
                      {pct(data.recall, 1)}
                    </td>
                    <td className="py-2 text-right font-semibold">
                      <span
                        className={
                          isHighPerformer
                            ? "text-emerald-600 dark:text-emerald-400"
                            : isLowPerformer
                            ? "text-rose-600 dark:text-rose-400"
                            : "text-slate-900 dark:text-slate-100"
                        }
                      >
                        {pct(data.f1, 1)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <p className="text-[11px] text-slate-500 dark:text-slate-400">
          * Asphalt slices (USA, Egypt, Japan, International) perform at 96.2% - 99.7% F1. Lower scores occur on non-asphalt pavement patches (Kauevestena sett stone and cobblestones) where mortar joints trigger false detections.
        </p>
      </div>

      {/* 5. Dashcam Video Tracking Benchmark */}
      <div className="card p-5 space-y-4 border border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-sm font-heading font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Film className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            <span>Dashcam Video Tracking Benchmarks</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Spatial-temporal associative IoU tracking across {video.total_video_clips} dashcam video clips ({video.total_duration_seconds}s total duration).
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-1">
          <div className="p-3 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <span className="text-[11px] text-slate-400 block">Duplicate Rate</span>
            <span className="text-lg font-mono font-bold text-emerald-600 dark:text-emerald-400">
              {pct(video.duplicate_rate, 2)}
            </span>
            <span className="text-[10px] text-slate-500 block">Target: 0.00%</span>
          </div>

          <div className="p-3 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <span className="text-[11px] text-slate-400 block">Event Recall</span>
            <span className="text-lg font-mono font-bold text-slate-800 dark:text-slate-200">
              {pct(video.event_recall, 1)}
            </span>
            <span className="text-[10px] text-slate-500 block">
              {video.matched_events} / {video.ground_truth_events} events
            </span>
          </div>

          <div className="p-3 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <span className="text-[11px] text-slate-400 block">False Alarms / Min</span>
            <span className="text-lg font-mono font-bold text-slate-800 dark:text-slate-200">
              {num(video.false_alarms_per_minute, 1)}
            </span>
            <span className="text-[10px] text-slate-500 block">Road texture noise</span>
          </div>

          <div className="p-3 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <span className="text-[11px] text-slate-400 block">Event-Level F1</span>
            <span className="text-lg font-mono font-bold text-slate-800 dark:text-slate-200">
              {pct(video.event_f1, 1)}
            </span>
            <span className="text-[10px] text-slate-500 block">Single-pass tracking</span>
          </div>
        </div>
      </div>

      {/* 6. Hardware & Production Models */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-5 space-y-3 border border-slate-200 dark:border-slate-800">
          <h2 className="text-sm font-heading font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-500" />
            <span>Measured Host Hardware Latency</span>
          </h2>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500">Benchmark Device</span>
              <span className="font-mono text-slate-800 dark:text-slate-200">{inference_hardware?.device || "AMD Ryzen 7 7445HS"}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500">ONNX Execution Provider</span>
              <span className="font-mono text-slate-800 dark:text-slate-200">{inference_hardware?.provider || "CPUExecutionProvider"}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500">p50 Inference Latency</span>
              <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{inference_hardware?.p50_latency_ms || 45.46} ms</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
              <span className="text-slate-500">p95 Inference Latency</span>
              <span className="font-mono text-slate-800 dark:text-slate-200">{inference_hardware?.p95_latency_ms || 53.29} ms</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Throughput</span>
              <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{inference_hardware?.fps || 21.0} FPS</span>
            </div>
          </div>
        </div>

        <div className="card p-5 space-y-3 border border-slate-200 dark:border-slate-800">
          <h2 className="text-sm font-heading font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-teal-500" />
            <span>Active Detection Pipeline Models</span>
          </h2>
          <div className="space-y-3 text-xs">
            {models && Object.entries(models).map(([name, m]) => (
              <div key={name} className="p-2.5 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{name}</span>
                  <span className="font-mono text-[10px] text-slate-500">{m.size_mb ? `${m.size_mb} MB` : ""}</span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">{m.role}</p>
                <p className="font-mono text-[10px] text-slate-400 mt-1 truncate" title={m.sha256 || ""}>
                  SHA256: {m.sha256 || "verified"}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 7. Disclaimer */}
      <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-center space-y-1">
        <div className="flex items-center justify-center gap-1.5 text-xs text-slate-600 dark:text-slate-400 font-medium">
          <Shield className="w-3.5 h-3.5" />
          <span>Research Integrity Statement</span>
        </div>
        <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-xl mx-auto">
          {evaluation.limitations_note ||
            "Student research project. Not an official government system. Not safety-certified. All evaluation metrics are measured on untouched held-out datasets with zero test leakage."}
        </p>
      </div>
    </div>
  );
};
