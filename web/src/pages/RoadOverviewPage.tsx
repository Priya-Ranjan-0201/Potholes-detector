import React from "react";
import { Link } from "react-router-dom";

export const RoadOverviewPage: React.FC = () => {

  const realCases = [
    {
      id: "nh44",
      title: "NH-44 North Corridor (Bengaluru)",
      location: "km 14.320, Lane 2 (Hebbal - Devanahalli)",
      src: "/samples/pothole_nh44.jpg",
      defect: "POTHOLE (88% confidence)",
      severity: "Critical",
      note: "Severe 45mm bowl depression on Bituminous Concrete wearing course.",
      box: { x: 74, y: 70, w: 22, h: 25 },
      color: "#D55E00",
    },
    {
      id: "crater",
      title: "State Highway 17 Pavement Crater",
      location: "km 88.200, Right Wheelpath",
      src: "/samples/asphalt_crater.jpg",
      defect: "POTHOLE (79% confidence)",
      severity: "Severe",
      note: "Coarse aggregate breakout with water absorption risk.",
      box: { x: 38, y: 22, w: 46, h: 68 },
      color: "#D55E00",
    },
    {
      id: "alligator",
      title: "MDR-04 Alligator Fatigue Pavement",
      location: "km 12.100, Lane Center",
      src: "/samples/alligator_cracks.jpg",
      defect: "CRACK_ALLIGATOR (80% confidence)",
      severity: "Moderate",
      note: "Interconnected fatigue micro-cracking across asphalt base layer.",
      box: { x: 24, y: 40, w: 54, h: 38 },
      color: "#0072B2",
    },
    {
      id: "diagram",
      title: "Civil Distress Diagram (Negative Control)",
      location: "eval_failures/case_02_teaching_diagram",
      src: "/samples/diagram_distress.png",
      defect: "REJECTED BY INPUT GATE",
      severity: "Non-Road",
      note: "MobileNetV3 classifier successfully rejects non-road diagram (P(road)=0.00).",
      box: null,
      color: "#5F5B50",
    },
  ];

  return (
    <div className="space-y-10 py-2">
      {/* 1. Hero / Reality Check */}
      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="px-2 py-0.5 rounded-[4px] text-[11px] font-mono font-medium bg-accent/20 border border-accent/40 text-text">
            Research Pilot
          </span>
          <span className="px-2 py-0.5 rounded-[4px] text-[11px] font-mono text-muted border border-rule">
            NH-44 Corridor km 10–35
          </span>
          <span className="px-2 py-0.5 rounded-[4px] text-[11px] font-mono text-muted border border-rule">
            Open Evaluation
          </span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-text tracking-tight max-w-3xl">
          Dashcam Road Defect Inspection for Indian Highways
        </h1>

        <p className="text-base text-muted max-w-3xl leading-relaxed">
          National and state highway authorities deploy dedicated laser profilometer Network Survey Vehicles (NSV) on tens of thousands of kilometers. ScamRoad does not replace those certified survey systems. Instead, it investigates a low-cost smartphone and dashcam triage pipeline with mandatory human engineering review for municipal roads, state PWDs, and rural PMGSY networks.
        </p>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Link
            to="/detect"
            className="px-4 py-2 rounded-[4px] bg-text text-bg text-xs font-sans font-semibold hover:opacity-90 transition-opacity"
          >
            Open Defect Detector
          </Link>
          <Link
            to="/review"
            className="px-4 py-2 rounded-[4px] border border-rule bg-surface text-text text-xs font-sans font-medium hover:bg-surface-raised transition-colors"
          >
            Review Queue (Triage)
          </Link>
          <Link
            to="/benchmarks"
            className="px-4 py-2 rounded-[4px] border border-rule bg-surface text-muted text-xs font-sans hover:text-text transition-colors"
          >
            View Scored Benchmarks
          </Link>
          <Link
            to="/method"
            className="px-4 py-2 rounded-[4px] border border-rule bg-surface text-muted text-xs font-sans hover:text-text transition-colors"
          >
            Architecture &amp; Methodology
          </Link>
        </div>
      </section>

      {/* 2. Measured Benchmark Scorecards (Real numbers only, R1 compliant) */}
      <section className="space-y-4">
        <div>
          <span className="text-xs font-mono uppercase font-bold text-muted">Empirical Performance</span>
          <h2 className="text-xl font-serif font-bold text-text">Measured Performance Across Gates</h2>
          <p className="text-xs text-muted mt-0.5">
            Evaluated on held-out test splits without synthetic data or test leakage.
          </p>
        </div>

        <div className="border border-rule rounded-[4px] bg-surface overflow-hidden">
          <div className="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Benchmark</th>
                  <th>Test Dataset Composition</th>
                  <th>Target Metric</th>
                  <th>Measured Result</th>
                  <th>95% Confidence Interval</th>
                  <th>Gate Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-mono text-xs font-bold text-text">TEST-A (Multi-Country)</td>
                  <td className="text-xs">1,508 multi-source images (750 damaged, 758 clean negatives)</td>
                  <td className="text-xs text-muted">Clean Negative Specificity</td>
                  <td className="font-mono text-xs font-bold text-text">98.81% (749/758 clean)</td>
                  <td className="font-mono text-xs text-muted">[97.77%, 99.42%]</td>
                  <td>
                    <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-bold">
                      PASS
                    </span>
                  </td>
                </tr>
                <tr>
                  <td className="font-mono text-xs font-bold text-text">TEST-B (Road Clutter)</td>
                  <td className="text-xs">300 clean road scenes with shadows, people, vehicles</td>
                  <td className="text-xs text-muted">False Alarm Images &le; 2.0%</td>
                  <td className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">1.33% (4/300 false alarms)</td>
                  <td className="font-mono text-xs text-muted">[0.52%, 3.38%]</td>
                  <td>
                    <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-bold">
                      PASS
                    </span>
                  </td>
                </tr>
                <tr>
                  <td className="font-mono text-xs font-bold text-text">TEST-C (Non-Road)</td>
                  <td className="text-xs">220 non-road scenes (diagrams, whiteboards, interiors)</td>
                  <td className="text-xs text-muted">Rejection Rate &ge; 95.0%</td>
                  <td className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">95.00% (209/220 rejected)</td>
                  <td className="font-mono text-xs text-muted">[91.27%, 97.19%]</td>
                  <td>
                    <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-bold">
                      PASS
                    </span>
                  </td>
                </tr>
                <tr>
                  <td className="font-mono text-xs font-bold text-text">Dashcam Video Tracker</td>
                  <td className="text-xs">20 continuous road survey video clips</td>
                  <td className="text-xs text-muted">False Alarms / min &amp; Event Dedup</td>
                  <td className="font-mono text-xs font-bold text-text">0.00 / min (13/13 matched)</td>
                  <td className="font-mono text-xs text-muted">0 duplicate events</td>
                  <td>
                    <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-bold">
                      PASS
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* 3. Real Credited Road Distress Samples */}
      <section className="space-y-4">
        <div>
          <span className="text-xs font-mono uppercase font-bold text-muted">Field Validation</span>
          <h2 className="text-xl font-serif font-bold text-text">Verified Evaluation Cases</h2>
          <p className="text-xs text-muted mt-0.5">
            Photographs evaluated under the multi-stage filter pipeline (2px outline, colour-blind safe overlays).
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {realCases.map((item) => (
            <div key={item.id} className="border border-rule rounded-[4px] bg-surface overflow-hidden flex flex-col">
              <div className="relative aspect-[16/10] bg-[#121311] overflow-hidden flex items-center justify-center">
                <img
                  src={item.src}
                  alt={item.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback visual if sample file path differs
                    (e.target as HTMLElement).style.display = "none";
                  }}
                />
                {item.box && (
                  <div
                    className="absolute border-2 pointer-events-none"
                    style={{
                      left: `${item.box.x}%`,
                      top: `${item.box.y}%`,
                      width: `${item.box.w}%`,
                      height: `${item.box.h}%`,
                      borderColor: item.color,
                      backgroundColor: `${item.color}15`,
                    }}
                  >
                    <span
                      className="absolute -top-6 left-0 px-1.5 py-0.5 text-[10px] font-mono text-white font-bold rounded-[2px]"
                      style={{ backgroundColor: item.color }}
                    >
                      {item.defect}
                    </span>
                  </div>
                )}
                {!item.box && (
                  <div className="absolute inset-0 bg-black/60 flex items-center justify-center p-4 text-center">
                    <span className="px-3 py-1.5 rounded-[4px] bg-surface text-text text-xs font-mono font-bold border border-rule">
                      {item.defect}
                    </span>
                  </div>
                )}
              </div>

              <div className="p-4 space-y-1.5 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="font-serif font-bold text-sm text-text">{item.title}</h3>
                    <span
                      className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-[3px] border"
                      style={{
                        borderColor: item.color,
                        color: item.color,
                        backgroundColor: `${item.color}10`,
                      }}
                    >
                      {item.severity}
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-muted">{item.location}</div>
                  <p className="text-xs text-muted mt-2 leading-relaxed">{item.note}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Comparison Ruled Table */}
      <section className="space-y-4">
        <div>
          <span className="text-xs font-mono uppercase font-bold text-muted">Method Comparison</span>
          <h2 className="text-xl font-serif font-bold text-text">Pavement Survey Methods in India</h2>
        </div>

        <div className="border border-rule rounded-[4px] bg-surface overflow-hidden">
          <div className="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Method</th>
                  <th>Capital Hardware Cost</th>
                  <th>Spatial Accuracy</th>
                  <th>Survey Cadence</th>
                  <th>Primary Use Case</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-bold text-text">Manual Engineer Walking Survey</td>
                  <td className="font-mono text-xs">Low (tape, depth gauge, GPS)</td>
                  <td className="text-xs">Sub-meter RTK (&le; 0.5m)</td>
                  <td className="text-xs text-muted">Monthly / Quarterly</td>
                  <td className="text-xs">Contractor dispute verification &amp; warranty sign-off</td>
                </tr>
                <tr>
                  <td className="font-bold text-text">Network Survey Vehicle (NSV / ROMDAS)</td>
                  <td className="font-mono text-xs">High (&gt; &#8377;1.5 Crore)</td>
                  <td className="text-xs">Millimeter laser profilometer</td>
                  <td className="text-xs text-muted">Semi-annual (NHAI mandate)</td>
                  <td className="text-xs">National highway concessionaire asset audit (IRI)</td>
                </tr>
                <tr className="bg-surface-raised/40">
                  <td className="font-bold text-text">ScamRoad Pilot (Dashcam + Triage)</td>
                  <td className="font-mono text-xs">Very Low (phone / dashcam)</td>
                  <td className="text-xs">5-meter along-track matching</td>
                  <td className="text-xs text-text font-medium">Daily / Weekly pass</td>
                  <td className="text-xs">Early distress warning &amp; human reviewer queue</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
};
