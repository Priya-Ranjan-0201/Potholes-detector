import React from "react";
import { Link } from "react-router-dom";
import { BookOpen, Database, Code, AlertTriangle, ArrowRight } from "../components/Icons";

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-10">
      {/* Page Header */}
      <div className="space-y-3 pb-6 border-b border-border">
        <p className="text-xs font-mono uppercase tracking-wider text-muted">
          About ScamRoad
        </p>
        <h1 className="font-heading font-bold text-3xl sm:text-4xl text-text tracking-tight">
          Road Defect Intelligence Platform
        </h1>
        <p className="text-sm sm:text-base text-muted leading-relaxed max-w-2xl">
          An open-source computer vision system for road surface distress detection, defect tracking, and maintenance workflow coordination.
        </p>
      </div>

      {/* Project Status Alert */}
      <div className="p-4 rounded-lg bg-subtle border border-border flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-status-warn shrink-0 mt-0.5" />
        <div className="text-xs sm:text-sm text-muted space-y-1">
          <p className="font-semibold text-text">Student Research Project</p>
          <p>
            ScamRoad is an academic B.Tech capstone research project in computer vision and municipal civil workflows.
            It is <strong>not</strong> an official government system, not affiliated with NHAI, MoRTH, or municipal corporations, and <strong>not safety-certified</strong> for autonomous driving or critical safety-of-life decisions.
          </p>
        </div>
      </div>

      {/* Problem & Motivation */}
      <section className="space-y-4">
        <h2 className="font-heading font-semibold text-xl text-text flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary" />
          <span>Problem Statement & Methodology</span>
        </h2>
        <div className="text-sm text-muted space-y-3 leading-relaxed">
          <p>
            Road surface degradation causes vehicular damage, traffic delays, and fatal accidents globally. Traditional municipal road inspections rely on manual periodic surveys or expensive sensor vans that cannot cover urban and rural corridors continuously.
          </p>
          <p>
            ScamRoad provides an edge-deployable, automated vision pipeline designed to ingest photos and dashcam streams from mobile phones and patrol vehicles:
          </p>
          <ul className="list-disc pl-5 space-y-1 text-xs sm:text-sm">
            <li><strong>Authentic Neural Detection:</strong> Fine-tuned YOLO11n for pothole detection paired with YOLOv8n for distress crack classification.</li>
            <li><strong>Spatial-Temporal Tracking:</strong> Continuous video frames are tracked via spatial IoU association to eliminate duplicate defect reports, condensing multiple frame detections of one physical hazard into a single maintenance event.</li>
            <li><strong>Calibrated Severity:</strong> Damage severity is calculated strictly using relative pixel area and localized cavity depression measurements—avoiding uncalibrated real-world metric claims without physical calibration targets.</li>
          </ul>
        </div>
      </section>

      {/* Datasets & Provenance */}
      <section className="space-y-4">
        <h2 className="font-heading font-semibold text-xl text-text flex items-center gap-2">
          <Database className="w-5 h-5 text-primary" />
          <span>Datasets & Provenance</span>
        </h2>
        <p className="text-sm text-muted">
          All models and benchmark evaluations are trained and tested on publicly licensed research datasets. No proprietary or scraped private data is used.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-surface border border-border space-y-2">
            <h3 className="font-semibold text-sm text-text">RDD2022 (Road Damage Dataset)</h3>
            <p className="text-xs text-muted">
              Global road damage imagery covering India, United States, Japan, and Egypt. Used for multi-condition asphalt pothole and crack evaluation.
            </p>
            <p className="text-[11px] font-mono text-muted">License: CC BY-SA 4.0</p>
          </div>

          <div className="p-4 rounded-lg bg-surface border border-border space-y-2">
            <h3 className="font-semibold text-sm text-text">Deep Pavements Dataset</h3>
            <p className="text-xs text-muted">
              Pavement surface patches covering asphalt, concrete, sett/cobblestone, and gravel. Used to evaluate negative retention and surface generalization.
            </p>
            <p className="text-[11px] font-mono text-muted">License: Open Research Dataset</p>
          </div>

          <div className="p-4 rounded-lg bg-surface border border-border space-y-2">
            <h3 className="font-semibold text-sm text-text">Taroii & Manot Benchmarks</h3>
            <p className="text-xs text-muted">
              Held-out road distress test images and clean pavement background images for out-of-domain cross-dataset validation.
            </p>
            <p className="text-[11px] font-mono text-muted">License: MIT / CC BY 4.0</p>
          </div>

          <div className="p-4 rounded-lg bg-surface border border-border space-y-2">
            <h3 className="font-semibold text-sm text-text">20 Real Dashcam Video Suite</h3>
            <p className="text-xs text-muted">
              Evaluation video clips capturing highway, urban, dusk, glare, and rain scenarios with verified temporal event ground truth.
            </p>
            <p className="text-[11px] font-mono text-muted">License: Open Dashcam Corpus</p>
          </div>
        </div>
      </section>

      {/* Technical Stack */}
      <section className="space-y-4">
        <h2 className="font-heading font-semibold text-xl text-text flex items-center gap-2">
          <Code className="w-5 h-5 text-primary" />
          <span>Architecture & Stack</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-subtle rounded border border-border">
            <p className="font-semibold text-text mb-1">Inference Engine</p>
            <p className="text-muted">ONNX Runtime CPU / INT8 Quantized / PyTorch Export</p>
          </div>
          <div className="p-3 bg-subtle rounded border border-border">
            <p className="font-semibold text-text mb-1">Backend API</p>
            <p className="text-muted">FastAPI, SQLAlchemy, PostgreSQL / PostGIS</p>
          </div>
          <div className="p-3 bg-subtle rounded border border-border">
            <p className="font-semibold text-text mb-1">Frontend Client</p>
            <p className="text-muted">React 18, Vite, TypeScript, Tailwind CSS ("Highway Green")</p>
          </div>
        </div>
      </section>

      {/* Research Credits & Open Source */}
      <section className="space-y-4 pt-4 border-t border-border">
        <h2 className="font-heading font-semibold text-xl text-text">Credits & License</h2>
        <div className="text-xs sm:text-sm text-muted space-y-2 leading-relaxed">
          <p>
            Developed as an undergraduate B.Tech capstone project. Designed with real-data fidelity, honest benchmark reporting, and zero fake or simulated metrics.
          </p>
          <p>
            Code is licensed under the <strong>GNU Affero General Public License v3.0 (AGPL-3.0)</strong>. Datasets and pretrained weights retain their respective open licenses (CC BY-SA 4.0 and MIT).
          </p>
        </div>

        <div className="flex flex-wrap gap-3 pt-2">
          <Link
            to="/benchmarks"
            className="px-4 py-2 bg-primary hover:bg-primary-hover text-primary-contrast rounded-md text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <span>View Verified Benchmarks</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
          <Link
            to="/scanner"
            className="px-4 py-2 bg-surface hover:bg-subtle text-text border border-border rounded-md text-xs font-semibold transition-colors"
          >
            <span>Try Road Scanner</span>
          </Link>
        </div>
      </section>
    </div>
  );
};
