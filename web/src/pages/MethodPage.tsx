import React from "react";

export const MethodPage: React.FC = () => {

  const pipelineStages = [
    {
      num: "01",
      name: "Input Gate Classifier",
      model: "MobileNetV3-Small ONNX (BSD-3-Clause)",
      purpose: "Rejects non-road inputs before detection inference.",
      detail:
        "Trained on 935 real road images and 220 negative scenes (civil distress diagrams, whiteboard sketches, indoor furniture, pure sky). Calibrated at threshold 0.12 achieving 95.00% rejection on TEST-C while ensuring zero false rejections on valid Indian road photos.",
    },
    {
      num: "02",
      name: "Drivable Surface Segmentation Mask",
      model: "Road Surface Segmenter Prior",
      purpose: "Enforces road-only bounding box constraint.",
      detail:
        "Computes a drivable surface mask across the asphalt carriage. Bounding boxes with less than 35% bounding area on the road surface are automatically dropped, preventing false alarms on sidewalk benches, overhead gantry signboards, pedestrians, or horizon trees.",
    },
    {
      num: "03",
      name: "Regularized YOLO11 Detector",
      model: "YOLO11 Road Damage ONNX",
      purpose: "Multi-class distress bounding box localization.",
      detail:
        "Trained on multi-country road damage datasets with extensive background negatives (shadows, vehicles, road markings, manholes). Decodes normalized coordinates with letterbox parity between browser canvas and backend inference.",
    },
    {
      num: "04",
      name: "Weighted Boxes Fusion (WBF)",
      model: "Multi-Model / Multi-Scale Consensus",
      purpose: "Coordinate consensus and confidence reweighting.",
      detail:
        "Replaces arbitrary hand-set ensemble weights with formal Weighted Boxes Fusion. Clusters overlapping predictions across models and scales, computing weighted average box boundaries and fused confidence scores.",
    },
    {
      num: "05",
      name: "Puddle vs Pothole Classifier",
      model: "Dual-Feature Crop Classifier",
      purpose: "Prevents harmless rain puddles from triggering false alarms.",
      detail:
        "Analyzes two physical signatures: perimeter rim Sobel gradient (threshold 22.0) and interior cavity shadow absorption (threshold 0.35). Harmless surface water with smooth rims is filtered; dark deep cavities with broken aggregate edges are classified as water-filled potholes.",
    },
    {
      num: "06",
      name: "ByteTrack Video Temporal Tracking",
      model: "ByteTrack / BoT-SORT Tracker",
      purpose: "Single-event consolidation along survey video.",
      detail:
        "Associates defect bounding boxes across consecutive dashcam frames using Kalman filtering and Hungarian IoU bipartite matching. Emits exactly one consolidated distress event per physical defect, eliminating duplicate logging across frames.",
    },
    {
      num: "07",
      name: "Confidence Triage & Review Loop",
      model: "3-Tier Decision Engine",
      purpose: "Attains national-grade catalog integrity through human oversight.",
      detail:
        "Detections with confidence >= 0.65 are auto-accepted; detections between 0.25 and 0.65 are routed to the human reviewer queue; detections below 0.25 are dropped. Weekly active-learning exports retrain the base detector, activating only if frozen benchmark accuracy improves.",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-rule pb-4">
        <h1 className="text-2xl font-serif font-bold text-text">
          Methodology &amp; Pipeline Architecture
        </h1>
        <p className="text-sm text-muted mt-1">
          7-stage sequential triage pipeline designed for low-cost dashcam pavement condition assessment on Indian highways and urban corridors.
        </p>
      </div>

      {/* Ruled Pipeline Stages Table */}
      <div className="border border-rule rounded-[4px] bg-surface overflow-hidden">
        <div className="px-4 py-3 border-b border-rule bg-surface-raised flex items-center justify-between">
          <span className="text-xs font-mono uppercase font-bold text-muted">Sequential Pipeline Execution</span>
          <span className="text-xs font-mono text-muted">7 Validated Processing Stages</span>
        </div>

        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th className="w-16">Stage</th>
                <th className="w-48">Module Name</th>
                <th className="w-56">Engine / Artifact</th>
                <th>Engineering Function &amp; Evaluation Rule</th>
              </tr>
            </thead>
            <tbody>
              {pipelineStages.map((stage) => (
                <tr key={stage.num}>
                  <td className="font-mono text-xs font-bold text-muted">{stage.num}</td>
                  <td className="font-serif font-bold text-text text-sm">{stage.name}</td>
                  <td className="font-mono text-xs text-muted">{stage.model}</td>
                  <td className="text-xs text-muted leading-relaxed">
                    <p className="text-text font-medium">{stage.purpose}</p>
                    <p className="mt-1">{stage.detail}</p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Standards Mapping & Operational Boundaries */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border border-rule rounded-[4px] bg-surface p-5 space-y-3">
          <span className="text-xs font-mono uppercase font-bold text-muted">Distress Class Taxonomy</span>
          <h2 className="text-base font-serif font-bold text-text">Pavement Distress Definitions</h2>
          <div className="space-y-2 text-xs text-muted">
            <p>
              <strong className="text-text font-mono">POTHOLE:</strong> Bowl-shaped cavity in bituminous wearing course with minimum diameter &ge; 150mm and depth &ge; 25mm.
            </p>
            <p>
              <strong className="text-text font-mono">CRACK_ALLIGATOR:</strong> Series of interconnected fatigue cracks caused by cyclic traffic wheel load fatigue on asphalt layers.
            </p>
            <p>
              <strong className="text-text font-mono">CRACK_LONGITUDINAL:</strong> Linear fracture running predominantly parallel to highway center alignment or paving joint.
            </p>
            <p>
              <strong className="text-text font-mono">CRACK_TRANSVERSE:</strong> Linear fracture running predominantly perpendicular to highway alignment caused by thermal contraction.
            </p>
          </div>
        </div>

        <div className="border border-rule rounded-[4px] bg-surface p-5 space-y-3">
          <span className="text-xs font-mono uppercase font-bold text-muted">Operational Boundaries</span>
          <h2 className="text-base font-serif font-bold text-text">Pilot Boundaries &amp; Realistic Scope</h2>
          <div className="space-y-2 text-xs text-muted">
            <p>
              <strong className="text-text">Not a High-Speed Profilometer:</strong> Dashcam optical analytics do not measure millimeter-accurate International Roughness Index (IRI).
            </p>
            <p>
              <strong className="text-text">Human-in-the-Loop Requirement:</strong> Detections in the 0.25–0.65 band must be audited by certified highway engineers prior to issuance of contractor repair work orders.
            </p>
            <p>
              <strong className="text-text">Validation Corridor:</strong> Evaluated specifically on the 25.0 km pilot section of NH-44 North Corridor (Hebbal km 10 to Devanahalli km 35).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
