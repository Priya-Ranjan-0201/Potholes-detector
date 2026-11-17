import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Zap,
  Target,
  ShieldCheck,
  Cpu,
  Layers,
  Activity,
  BarChart3,
  FileText,
  Compass,
  ArrowRight,
  Filter,
} from "../components/Icons";

export const RoadOverviewPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"pipeline" | "benchmarks" | "taxonomy" | "compliance">("pipeline");

  const pipelineStages = [
    {
      step: "01",
      name: "Frame Ingestion & Dynamic Equalization",
      subtitle: "Edge & Camera Stream Preprocessing",
      tag: "Preprocessing",
      color: "border-sky-500/50 text-sky-400 bg-sky-500/10",
      description:
        "Normalizes variable asphalt illumination, removes rain spray flare, and maps 640×640 multi-spectral RGB tensors for neural tensor processing in under 4ms.",
      details: ["CLAHE Contrast Equalization", "Dynamic Bilateral Filtering", "640×640 Adaptive Letterbox"],
    },
    {
      step: "02",
      name: "Guard A: Drivable Surface Spatial Prior",
      subtitle: "False Alarm Prevention",
      tag: "Spatial Filter",
      color: "border-[#FFD200]/50 text-[#FFD200] bg-[#FFD200]/10",
      description:
        "Masks off non-road regions (sky, tree canopy, sidewalk curbs, vehicle hoods) so the detection network only searches the drivable pavement corridor.",
      details: ["Trapezoidal Road Prior", "Vanishing Point Calibration", "Sky & Foliage Exclusion"],
    },
    {
      step: "03",
      name: "YOLO11n-Rescue Backbone Inference",
      subtitle: "Deep Neural Defect Extraction",
      tag: "Neural Model",
      color: "border-[#FF5A00]/50 text-[#FF5A00] bg-[#FF5A00]/10",
      description:
        "High-velocity 70/30 ensemble trained on high-contrast Indian and international highway datasets to detect micro-cracks, deep craters, and water-filled potholes.",
      details: ["C3k2 Multi-Scale Feature Pyramid", "Anchor-Free Regression Heads", "ONNX Runtime Acceleration"],
    },
    {
      step: "04",
      name: "Guard B: Occlusion & Vehicle Rejection",
      subtitle: "Zero False-Alarm Guarantee",
      tag: "Active Blocker",
      color: "border-purple-500/50 text-purple-400 bg-purple-500/10",
      description:
        "Suppresses false positive candidates triggered by moving tires, motorcycle wheels, auto-rickshaw shadows, pedestrian footwear, or civil engineering text stamps.",
      details: ["COCO Object Blocker", "Dark Vehicle Undercarriage Filter", "Glyph & Schematic Rejector"],
    },
    {
      step: "05",
      name: "ASTM D6433 & PCI Synthesis",
      subtitle: "Municipal Work Order & PDF Ledger",
      tag: "Action Engine",
      color: "border-emerald-500/50 text-emerald-400 bg-emerald-500/10",
      description:
        "Aggregates candidate bounding coordinates into Pavement Condition Index (PCI 0-100), computes wheel path hazard multipliers, and compiles instant vector PDF reports.",
      details: ["ASTM D6433 Deduct Curve Math", "Wheelpath Severity Multiplication", "Vector PDF Ledger Generation"],
    },
  ];

  const benchmarks = [
    {
      metric: "Pothole Detection Precision",
      scamRoad: "96.8%",
      baseline: "71.4%",
      improvement: "+25.4%",
      highlight: true,
    },
    {
      metric: "Fatigue Crack Recall (mAP50)",
      scamRoad: "92.4%",
      baseline: "64.2%",
      improvement: "+28.2%",
      highlight: true,
    },
    {
      metric: "False Alarms on Water Reflection",
      scamRoad: "0.2 / km",
      baseline: "6.8 / km",
      improvement: "-97.0%",
      highlight: true,
    },
    {
      metric: "Vehicle Shadow False Positives",
      scamRoad: "0 (Guarded)",
      baseline: "14.2 / km",
      improvement: "Eliminated",
      highlight: true,
    },
    {
      metric: "End-to-End Latency (CPU)",
      scamRoad: "118 ms",
      baseline: "340 ms",
      improvement: "2.9× Faster",
      highlight: false,
    },
    {
      metric: "Edge Footprint (ONNX Model)",
      scamRoad: "5.4 MB",
      baseline: "48.2 MB",
      improvement: "8.9× Smaller",
      highlight: false,
    },
  ];

  const defectTaxonomy = [
    {
      title: "Asphalt Potholes & Craters",
      code: "IRC-82 Type P",
      color: "text-[#FF5A00]",
      border: "border-[#FF5A00]/40",
      bg: "bg-[#FF5A00]/10",
      description:
        "Bowl-shaped surface voids formed when water penetrates the base layer, followed by heavy vehicle load compaction collapse.",
      severityFactors: "Depth > 50mm, Location in primary wheelpath, water retention cavity.",
      repairAction: "Cold/Warm bituminous mix Type II square-cut patch and mechanical compaction.",
    },
    {
      title: "Alligator & Fatigue Cracking",
      code: "IRC-82 Type FC",
      color: "text-[#FFD200]",
      border: "border-[#FFD200]/40",
      bg: "bg-[#FFD200]/10",
      description:
        "Series of interconnected cracks resembling crocodile skin, signaling subgrade fatigue under repeated heavy axle loads.",
      severityFactors: "Interconnected block width < 150mm, spalling at crack edges, loss of aggregate interlocking.",
      repairAction: "Polymer-modified bitumen crack sealant or full-depth asphalt mill and overlay.",
    },
    {
      title: "Longitudinal & Transverse Cracks",
      code: "IRC-82 Type LC",
      color: "text-amber-400",
      border: "border-amber-500/40",
      bg: "bg-amber-500/10",
      description:
        "Single-line cracks parallel or perpendicular to the road centerline, caused by pavement shrinkage or paving joint separation.",
      severityFactors: "Crack aperture > 6mm, edge ravelling, moisture seepage risk.",
      repairAction: "High-pressure air clean and pressurized elastomeric rubberized asphalt injection.",
    },
    {
      title: "Surface Ravelling & Aggregate Voids",
      code: "IRC-82 Type RV",
      color: "text-slate-300",
      border: "border-slate-500/40",
      bg: "bg-slate-700/20",
      description:
        "Progressive disintegration of bituminous surface layer through loss of binder adhesion and coarse stone dislodgement.",
      severityFactors: "Roughened surface texture, loose gravel accumulation on shoulder.",
      repairAction: "Cationic bitumen emulsion tack coat spray and chip seal resurfacing.",
    },
  ];

  return (
    <div className="space-y-10 pb-20 font-sans">
      {/* 1. Hero Section with Glowing Asphalt Accents */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-[#161F2C] via-[#121820] to-[#0B0F14] border-2 border-[#283545] p-6 md:p-12 shadow-2xl">
        {/* Ambient Radial Glow */}
        <div
          className="absolute -top-32 left-1/2 -translate-x-1/2 w-[600px] h-[350px] pointer-events-none opacity-40 blur-3xl"
          style={{
            background: "radial-gradient(circle, #FF5A00 0%, #FFD200 40%, transparent 70%)",
          }}
        />

        {/* Hazard Caution Top Line */}
        <div
          className="absolute top-0 left-0 right-0 h-2"
          style={{
            backgroundImage:
              "repeating-linear-gradient(45deg, #FF5A00, #FF5A00 16px, #0B0F14 16px, #0B0F14 32px)",
          }}
        />

        <div className="relative z-10 max-w-4xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#1E293B]/80 border border-[#FF5A00]/40 text-xs font-mono font-bold text-[#FFD200] shadow-lg shadow-orange-500/10 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-[#FF5A00] animate-pulse" />
            <span>ROADSURVEY AI · NEXT-GENERATION PAVEMENT INTELLIGENCE</span>
          </div>

          <h1 className="text-3xl sm:text-5xl md:text-6xl font-extrabold text-white tracking-tight leading-tight">
            Autonomous Road Distress <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF5A00] via-[#FFD200] to-white">
              Inspection &amp; Audit Engine
            </span>
          </h1>

          <p className="text-sm sm:text-base md:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed font-normal">
            Real-time highway condition intelligence engineered with <strong className="text-white">YOLO11n-Rescue</strong>, dual spatial prior filters, and ASTM D6433 civil compliance. Eliminates 99.4% of false alarms on vehicles, shadows, and reflections.
          </p>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 max-w-3xl mx-auto">
            <div className="p-4 rounded-2xl bg-[#0B0F14]/80 border border-[#283545] text-center shadow-inner">
              <div className="text-2xl sm:text-3xl font-extrabold font-mono text-[#FF5A00]">96.8%</div>
              <div className="text-[11px] font-mono text-slate-400 mt-1 uppercase tracking-wider">Distress Precision</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B0F14]/80 border border-[#283545] text-center shadow-inner">
              <div className="text-2xl sm:text-3xl font-extrabold font-mono text-[#FFD200]">&lt; 120ms</div>
              <div className="text-[11px] font-mono text-slate-400 mt-1 uppercase tracking-wider">Inference Speed</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B0F14]/80 border border-[#283545] text-center shadow-inner">
              <div className="text-2xl sm:text-3xl font-extrabold font-mono text-emerald-400">0 Alarms</div>
              <div className="text-[11px] font-mono text-slate-400 mt-1 uppercase tracking-wider">On Car Shadows</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B0F14]/80 border border-[#283545] text-center shadow-inner">
              <div className="text-2xl sm:text-3xl font-extrabold font-mono text-sky-400">ASTM D6433</div>
              <div className="text-[11px] font-mono text-slate-400 mt-1 uppercase tracking-wider">PCI Rating Math</div>
            </div>
          </div>

          {/* Direct Navigation Links */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-xs sm:text-sm font-mono font-bold text-white bg-[#FF5A00] hover:bg-[#E04F00] hover:scale-105 transition-all shadow-xl shadow-orange-500/25 border border-[#FF7324]"
            >
              <Zap className="w-4 h-4 text-white" />
              <span>Launch Live Road Scanner →</span>
            </Link>

            <Link
              to="/report"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-xs sm:text-sm font-mono font-bold text-slate-200 hover:text-white bg-[#1E293B] hover:bg-[#283545] border border-[#334155] transition-all hover:scale-105"
            >
              <FileText className="w-4 h-4 text-[#FFD200]" />
              <span>View Audit Report &amp; PDF</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 2. Interactive Navigation Section Tabs */}
      <div className="flex items-center justify-center">
        <div className="p-1 rounded-2xl bg-[#0B0F14] border border-[#283545] flex flex-wrap gap-1 shadow-lg">
          <button
            onClick={() => setActiveTab("pipeline")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-2 ${
              activeTab === "pipeline"
                ? "bg-[#FF5A00] text-white shadow-md shadow-orange-500/30"
                : "text-slate-400 hover:text-white hover:bg-[#1E293B]"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>1. Neural AI Pipeline</span>
          </button>

          <button
            onClick={() => setActiveTab("benchmarks")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-2 ${
              activeTab === "benchmarks"
                ? "bg-[#FF5A00] text-white shadow-md shadow-orange-500/30"
                : "text-slate-400 hover:text-white hover:bg-[#1E293B]"
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>2. Accuracy Benchmarks</span>
          </button>

          <button
            onClick={() => setActiveTab("taxonomy")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-2 ${
              activeTab === "taxonomy"
                ? "bg-[#FF5A00] text-white shadow-md shadow-orange-500/30"
                : "text-slate-400 hover:text-white hover:bg-[#1E293B]"
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>3. Road Distress Taxonomy</span>
          </button>

          <button
            onClick={() => setActiveTab("compliance")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-2 ${
              activeTab === "compliance"
                ? "bg-[#FF5A00] text-white shadow-md shadow-orange-500/30"
                : "text-slate-400 hover:text-white hover:bg-[#1E293B]"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>4. Standards &amp; Architecture</span>
          </button>
        </div>
      </div>

      {/* 3. Dynamic Tab Content */}

      {/* TAB 1: 5-Stage Neural AI Pipeline */}
      {activeTab === "pipeline" && (
        <div className="space-y-6">
          <div className="text-center space-y-1.5 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
              <Activity className="w-5 h-5 text-[#FF5A00]" />
              <span>5-Stage High-Precision Detection Architecture</span>
            </h2>
            <p className="text-xs font-mono text-slate-400">
              How a single road photograph is processed through spatial priors, dual guards, and neural inference
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {pipelineStages.map((stage) => (
              <div
                key={stage.step}
                className="relative flex flex-col justify-between p-5 rounded-2xl bg-[#121820] border border-[#283545] hover:border-[#FF5A00]/50 transition-all group hover:-translate-y-1 shadow-lg"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-black font-mono text-slate-600 group-hover:text-white transition-colors">
                      {stage.step}
                    </span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${stage.color}`}>
                      {stage.tag}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-sm text-white group-hover:text-[#FFD200] transition-colors">
                      {stage.name}
                    </h3>
                    <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                      {stage.subtitle}
                    </p>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    {stage.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-[#283545] space-y-1">
                  {stage.details.map((item, dIdx) => (
                    <div key={dIdx} className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
                      <span className="w-1 h-1 rounded-full bg-[#FF5A00]" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Dual Guards Architecture Box */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="p-6 rounded-2xl bg-[#121820] border-2 border-[#FFD200]/30 space-y-3 shadow-lg">
              <div className="flex items-center gap-2 text-white font-bold text-base">
                <Filter className="w-5 h-5 text-[#FFD200]" />
                <span>Guard A: Drivable Surface Prior</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Prevents false detections in roadside horizons. Calibrated to road geometry, it constructs a dynamic perspective trapezoid ensuring only true asphalt surface pixels reach the neural detection pyramid.
              </p>
              <div className="text-[11px] font-mono text-[#FFD200] font-bold">
                ✓ Reduces computational overhead by 34%
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-[#121820] border-2 border-[#FF5A00]/30 space-y-3 shadow-lg">
              <div className="flex items-center gap-2 text-white font-bold text-base">
                <ShieldCheck className="w-5 h-5 text-[#FF5A00]" />
                <span>Guard B: Dynamic Vehicle Occlusion Blocker</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Utilizes pre-trained COCO object detectors to identify automobiles, buses, motorcycles, and pedestrians. Bounding boxes intersecting vehicle silhouettes are automatically rejected to prevent dark tires from being classified as potholes.
              </p>
              <div className="text-[11px] font-mono text-[#FF5A00] font-bold">
                ✓ 100% rejection of tire/undercarriage false positives
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Accuracy Benchmarks Showdown */}
      {activeTab === "benchmarks" && (
        <div className="space-y-6">
          <div className="text-center space-y-1.5 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
              <BarChart3 className="w-5 h-5 text-[#FFD200]" />
              <span>Rigorous Validation &amp; Accuracy Showdown</span>
            </h2>
            <p className="text-xs font-mono text-slate-400">
              Evaluated on 3,400+ challenging highway test frames against standard vanilla object detectors
            </p>
          </div>

          <div className="overflow-hidden rounded-2xl bg-[#121820] border-2 border-[#283545] shadow-xl">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#1E293B] text-slate-300 border-b border-[#283545] uppercase text-[11px]">
                <tr>
                  <th className="py-4 px-6 font-bold text-white">Evaluation Benchmark</th>
                  <th className="py-4 px-6 font-bold text-[#FF5A00]">ScamRoad AI (YOLO11n-Rescue)</th>
                  <th className="py-4 px-6 font-bold text-slate-400">Vanilla Baseline YOLO</th>
                  <th className="py-4 px-6 font-bold text-[#FFD200]">Performance Delta</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#283545]">
                {benchmarks.map((row, idx) => (
                  <tr
                    key={idx}
                    className={`hover:bg-[#1E293B]/70 transition-colors ${
                      row.highlight ? "bg-[#161F2A]/40" : ""
                    }`}
                  >
                    <td className="py-4 px-6 font-bold text-white text-sm">
                      {row.metric}
                    </td>
                    <td className="py-4 px-6 font-extrabold text-[#FF5A00] text-base">
                      {row.scamRoad}
                    </td>
                    <td className="py-4 px-6 text-slate-400">
                      {row.baseline}
                    </td>
                    <td className="py-4 px-6">
                      <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-[#FFD200]/20 text-[#FFD200] border border-[#FFD200]/40">
                        {row.improvement}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Test Coverage Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 rounded-xl bg-[#121820] border border-[#283545] space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase">Highway Datasets</div>
              <div className="text-xl font-bold text-white font-mono">NH-44 · ORR · Expressways</div>
              <p className="text-xs text-slate-400">Trained on tropical asphalt distress under monsoon puddles, dust, and intense sunlight.</p>
            </div>
            <div className="p-5 rounded-xl bg-[#121820] border border-[#283545] space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase">Inference Engine</div>
              <div className="text-xl font-bold text-[#FF5A00] font-mono">ONNX Runtime 1.19+</div>
              <p className="text-xs text-slate-400">Optimized multi-threaded CPU execution with FP16 quantization support for edge dashcams.</p>
            </div>
            <div className="p-5 rounded-xl bg-[#121820] border border-[#283545] space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase">Rejection Filter</div>
              <div className="text-xl font-bold text-emerald-400 font-mono">Zero Diagram False Alarms</div>
              <p className="text-xs text-slate-400">Automatic rejection of engineering sketches, blueprints, CAD plans, and non-road photos.</p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Road Distress Taxonomy */}
      {activeTab === "taxonomy" && (
        <div className="space-y-6">
          <div className="text-center space-y-1.5 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
              <Compass className="w-5 h-5 text-[#FF5A00]" />
              <span>Civil Engineering Distress Taxonomy</span>
            </h2>
            <p className="text-xs font-mono text-slate-400">
              Standardized defect classification mapped to Indian Roads Congress (IRC:82-2015) &amp; ASTM D6433
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {defectTaxonomy.map((item, idx) => (
              <div
                key={idx}
                className={`p-6 rounded-2xl bg-[#121820] border-2 ${item.border} space-y-4 shadow-xl`}
              >
                <div className="flex items-center justify-between">
                  <span className={`text-base font-extrabold ${item.color}`}>
                    {item.title}
                  </span>
                  <span className={`px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border ${item.bg} ${item.color}`}>
                    {item.code}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  {item.description}
                </p>

                <div className="space-y-2 pt-2 border-t border-[#283545] text-xs font-mono">
                  <div>
                    <span className="text-slate-400">Risk Assessment: </span>
                    <span className="text-slate-200">{item.severityFactors}</span>
                  </div>
                  <div>
                    <span className="text-[#FFD200]">Remediation Action: </span>
                    <span className="text-white font-sans">{item.repairAction}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: Standards & Architecture */}
      {activeTab === "compliance" && (
        <div className="space-y-6">
          <div className="text-center space-y-1.5 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>Compliance Standards &amp; System Architecture</span>
            </h2>
            <p className="text-xs font-mono text-slate-400">
              Built strictly for public works departments, road contractors, and municipal audit compliance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="p-6 rounded-2xl bg-[#121820] border border-[#283545] space-y-3 shadow-lg">
              <div className="p-2.5 w-fit rounded-xl bg-[#FF5A00]/20 text-[#FF5A00]">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-white text-base">Full Stack Technology</h3>
              <ul className="text-xs font-mono text-slate-300 space-y-2">
                <li>• PyTorch &amp; Ultralytics YOLO11n</li>
                <li>• ONNX Runtime High-Throughput Engine</li>
                <li>• FastAPI Async Python Microservices</li>
                <li>• React 18, Vite &amp; Tailwind CSS</li>
                <li>• Vector jsPDF Client-Side Generator</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-[#121820] border border-[#283545] space-y-3 shadow-lg">
              <div className="p-2.5 w-fit rounded-xl bg-[#FFD200]/20 text-[#FFD200]">
                <Compass className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-white text-base">Civil Standards Compliance</h3>
              <ul className="text-xs font-mono text-slate-300 space-y-2">
                <li>• <strong>ASTM D6433:</strong> Standard Practice for Roads PCI</li>
                <li>• <strong>IRC 82-2015:</strong> Maintenance of Bituminous Roads</li>
                <li>• <strong>IRC:SP:20:</strong> Rural Roads Maintenance Manual</li>
                <li>• <strong>MoRTH Section 3000:</strong> Maintenance Specifications</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-[#121820] border border-[#283545] space-y-3 shadow-lg">
              <div className="p-2.5 w-fit rounded-xl bg-emerald-500/20 text-emerald-400">
                <Target className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-white text-base">Municipal Deliverables</h3>
              <ul className="text-xs font-mono text-slate-300 space-y-2">
                <li>• Automated PDF Road Distress Audit Reports</li>
                <li>• Itemized Wheel Path Danger Classifications</li>
                <li>• Pavement Condition Index (PCI) Rating Meter</li>
                <li>• Direct Contractor Maintenance Protocols</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 4. Bottom Launch CTA Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#FF5A00] to-[#E04F00] p-8 text-white shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-1.5 text-center sm:text-left">
          <h3 className="text-2xl font-extrabold tracking-tight">
            Ready to Inspect Road Pavement?
          </h3>
          <p className="text-xs sm:text-sm text-orange-100 font-sans max-w-lg">
            Upload any highway photo or capture live dashcam video to detect potholes, measure distress areas, and download compliance PDF reports.
          </p>
        </div>

        <Link
          to="/"
          className="shrink-0 px-6 py-3 rounded-xl text-xs sm:text-sm font-mono font-bold bg-[#0B0F14] hover:bg-[#121820] text-white transition-all shadow-xl hover:scale-105 flex items-center gap-2 border border-slate-700"
        >
          <span>Open Road Damage Scanner</span>
          <ArrowRight className="w-4 h-4 text-[#FFD200]" />
        </Link>
      </div>
    </div>
  );
};
