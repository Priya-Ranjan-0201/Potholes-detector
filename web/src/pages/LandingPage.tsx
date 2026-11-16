import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api, ModelEvaluationResponse } from "../api/client";
import {
  Camera,
  ArrowRight,
  Layers,
  Activity,
  CheckCircle,
  AlertTriangle,
} from "../components/Icons";

export const LandingPage: React.FC = () => {
  const { data: evaluation } = useQuery<ModelEvaluationResponse>({
    queryKey: ["modelEvaluationReport"],
    queryFn: api.getModelEvaluation,
    retry: 1,
  });

  // Slider position (0 - 100%) for interactive before/after comparison
  const [sliderPos, setSliderPos] = useState<number>(50);

  // Derive metrics with honest held-out defaults
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

  const steps = [
    {
      step: "01",
      title: "Capture",
      desc: "Upload road photos or dashcam clips from a smartphone or patrol camera. Wide format support with EXIF orientation correction and privacy face/plate blurring.",
      icon: Camera,
    },
    {
      step: "02",
      title: "Detect",
      desc: "Calibrated multi-model ONNX neural network identifies potholes and surface distress. Obstacle filtering blocks false alarms over vehicles and pedestrians.",
      icon: Activity,
    },
    {
      step: "03",
      title: "Coordinate",
      desc: "Spatial-temporal associative tracking groups repeat dashcam sightings into unique defect events (0.00% duplicates) and manages repair work orders.",
      icon: Layers,
    },
  ];

  return (
    <div className="space-y-16 pb-16 text-slate-900 dark:text-slate-100">
      {/* 1. Hero Section */}
      <section className="pt-8 sm:pt-14 text-center max-w-3xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-950/40 border border-primary-200 dark:border-primary-800 text-primary-800 dark:text-primary-300 text-xs font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-primary-600 dark:bg-primary-400 animate-pulse" />
          <span>Open-Source Road Defect Intelligence · Capstone Research</span>
        </div>

        <h1 className="font-heading font-bold text-3xl sm:text-5xl lg:text-6xl tracking-tight text-slate-900 dark:text-white leading-[1.12]">
          Open-source road defect <span className="text-primary-700 dark:text-primary-400">intelligence</span>
        </h1>

        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Autonomous computer vision detection, video defect tracking, and municipal repair workflows
          for asphalt potholes and surface cracking. Built as an open student research project.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <Link
            to="/scanner"
            className="px-5 py-2.5 rounded-lg text-sm font-medium bg-primary-700 hover:bg-primary-800 text-white transition-colors flex items-center gap-2 shadow-sm"
          >
            <span>Open Scanner</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/benchmarks"
            className="px-5 py-2.5 rounded-lg text-sm font-medium bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 transition-colors shadow-sm"
          >
            <span>View Benchmarks</span>
          </Link>
        </div>
      </section>

      {/* 2. Live Metrics Strip */}
      <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-6 shadow-sm">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 text-xs text-slate-500">
          <span className="font-semibold text-slate-700 dark:text-slate-300">
            Verified Held-Out Evaluation Metrics
          </span>
          <span className="font-mono text-[11px]">
            {evaluation ? "Connected to backend /models/evaluation" : "Held-out test set baseline"}
          </span>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 pt-5 text-center">
          <div className="space-y-1">
            <p className="font-mono text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
              {recallVal}
            </p>
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Defect Recall
            </p>
            <p className="text-[11px] text-slate-500 font-mono">
              959 / 984 defect images detected
            </p>
          </div>

          <div className="space-y-1">
            <p className="font-mono text-3xl font-bold text-teal-700 dark:text-teal-400 tracking-tight">
              {f1Val}
            </p>
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Image-Level F1
            </p>
            <p className="text-[11px] text-slate-500 font-mono">
              95% CI: [77.1%, 80.7%]
            </p>
          </div>

          <div className="space-y-1">
            <p className="font-mono text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
              {testSetSize}
            </p>
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Test Set Size
            </p>
            <p className="text-[11px] text-slate-500 font-mono">
              6 countries · 11 datasets · 0 leakage
            </p>
          </div>

          <div className="space-y-1">
            <p className="font-mono text-3xl font-bold text-emerald-600 dark:text-emerald-400 tracking-tight">
              {duplicateRate}
            </p>
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Video Duplicate Rate
            </p>
            <p className="text-[11px] text-slate-500 font-mono">
              Spatial-temporal tracking across 20 clips
            </p>
          </div>
        </div>
      </section>

      {/* 3. Interactive Before / After Defect Comparison */}
      <section className="space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="font-heading font-bold text-2xl tracking-tight text-slate-900 dark:text-white">
            Repair Verification &amp; Inspection
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400">
            Compare initial defect observation against physical asphalt restoration.
          </p>
        </div>

        <div className="max-w-3xl mx-auto card p-4 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="font-medium text-slate-700 dark:text-slate-300">
              Interactive Defect Pair: Asphalt Pothole (Before vs Repaired)
            </span>
            <span className="font-mono text-[11px]">Slider: {sliderPos}%</span>
          </div>

          <div className="relative h-72 sm:h-96 w-full overflow-hidden rounded-lg select-none">
            {/* Background Image: Repaired */}
            <img
              src="/samples/benchmark_pairs/pothole_repaired.jpg"
              alt="Repaired asphalt surface"
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute top-3 right-3 px-2 py-1 rounded bg-black/60 text-white font-mono text-[11px] backdrop-blur-sm">
              Status: Repaired
            </div>

            {/* Foreground Image: Before (clipped by slider) */}
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ width: `${sliderPos}%` }}
            >
              <img
                src="/samples/benchmark_pairs/pothole_before.jpg"
                alt="Defect pothole on road"
                className="absolute inset-0 w-full h-full object-cover max-w-none"
                style={{ width: "100%", minWidth: "100%" }}
              />
              <div className="absolute top-3 left-3 px-2 py-1 rounded bg-rose-600/80 text-white font-mono text-[11px] backdrop-blur-sm">
                Status: Detected Defect
              </div>
            </div>

            {/* Divider Line */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-white shadow-lg cursor-ew-resize flex items-center justify-center"
              style={{ left: `calc(${sliderPos}% - 2px)` }}
            >
              <div className="w-6 h-6 rounded-full bg-white text-slate-700 shadow-md flex items-center justify-center text-[10px] font-bold">
                &#x2194;
              </div>
            </div>

            {/* Invisible Range Input for Scrubbing */}
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
              aria-label="Drag before and after comparison slider"
            />
          </div>

          <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
            <span>&larr; Drag slider left to reveal repaired pavement</span>
            <Link to="/scanner" className="text-primary-700 dark:text-primary-400 hover:underline font-medium">
              Test detection on live images in Scanner &rarr;
            </Link>
          </div>
        </div>
      </section>

      {/* 4. 3-Step "How It Works" */}
      <section className="space-y-8">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="font-heading font-bold text-2xl tracking-tight text-slate-900 dark:text-white">
            How It Works
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400">
            Three simple stages from field media capture to verified municipal repair.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {steps.map((s) => {
            const Icon = s.icon;
            return (
              <div
                key={s.step}
                className="card p-6 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 rounded-xl flex flex-col justify-between space-y-4 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-2xl font-bold text-slate-300 dark:text-slate-700">
                    {s.step}
                  </span>
                  <div className="p-2.5 rounded-lg bg-primary-50 dark:bg-primary-950/50 text-primary-700 dark:text-primary-400">
                    <Icon className="w-5 h-5" />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <h3 className="font-heading font-semibold text-base text-slate-900 dark:text-white">
                    {s.title}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    {s.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 5. Honest Capabilities & Research Limitations */}
      <section className="max-w-4xl mx-auto">
        <div className="card p-6 sm:p-8 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 rounded-xl shadow-sm space-y-6">
          <div>
            <h2 className="font-heading font-bold text-lg text-slate-900 dark:text-white">
              System Capabilities &amp; Known Limitations
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Transparent engineering evaluation for peer review and replication.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-semibold text-xs uppercase tracking-wider">
                <CheckCircle className="w-4 h-4" />
                <span>Implemented &amp; Verified</span>
              </div>
              <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2.5">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">•</span>
                  <span>97.46% defect recall across 1,728 multi-source held-out test images</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">•</span>
                  <span>0.00% video duplicate rate via spatial-temporal IoU tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">•</span>
                  <span>Wide format ingestion: EXIF rotation, alpha composite, 16-bit, WebP, AVIF</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">•</span>
                  <span>Work-order state machine with before/after physical repair comparison</span>
                </li>
              </ul>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-semibold text-xs uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4" />
                <span>Known Limitations</span>
              </div>
              <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2.5">
                <li className="flex items-start gap-2">
                  <span className="text-amber-600 dark:text-amber-400 font-bold">•</span>
                  <span>Stone mortar joints in sett/cobblestone roads cause false positives (asphalt F1 is 96-99%)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-amber-600 dark:text-amber-400 font-bold">•</span>
                  <span>Monocular camera input measures relative pixel area only (no calibrated depth/volume)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-amber-600 dark:text-amber-400 font-bold">•</span>
                  <span>Fine hairline crack recall is conservative to prevent false alarms on clean asphalt</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-amber-600 dark:text-amber-400 font-bold">•</span>
                  <span>Student research prototype only; not certified for life-safety critical road operations</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Footer Disclaimer Banner */}
      <div className="p-4 rounded-lg bg-slate-100 dark:bg-slate-900 text-center text-xs text-slate-500 space-y-1">
        <p className="font-semibold text-slate-700 dark:text-slate-300">
          Student research project. Not an official government system. Not safety-certified.
        </p>
        <p className="text-[11px] text-slate-400">
          Developed as a B.Tech capstone engineering project under the AGPL-3.0 open-source license.
        </p>
      </div>
    </div>
  );
};
