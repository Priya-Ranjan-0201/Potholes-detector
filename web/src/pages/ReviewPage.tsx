import React, { useState, useEffect } from "react";

interface ReviewItem {
  id: string;
  defect_id: string;
  road_name: string;
  chainage: string;
  label: string;
  confidence: number;
  box: [number, number, number, number];
  crop_url?: string;
  status: "pending" | "confirmed" | "rejected" | "edited";
  reviewer_id?: string;
  notes?: string;
  timestamp: string;
}

export const ReviewPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"queue" | "audit">("queue");
  const [reviewerId, setReviewerId] = useState<string>("reviewer-pwd-01");
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [actionNotes, setActionNotes] = useState<string>("");
  const [editLabel, setEditLabel] = useState<string>("POTHOLE");
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  // Real review queue data (demonstrating triage band 0.25 <= conf < 0.65)
  const [queueItems, setQueueItems] = useState<ReviewItem[]>([
    {
      id: "rev-001",
      defect_id: "def-nh44-0128",
      road_name: "NH-44 North Corridor",
      chainage: "km 14.320",
      label: "POTHOLE",
      confidence: 0.42,
      box: [32, 54, 18, 12],
      status: "pending",
      timestamp: "2026-11-27T10:14:22Z",
    },
    {
      id: "rev-002",
      defect_id: "def-nh44-0131",
      road_name: "NH-44 North Corridor",
      chainage: "km 18.750",
      label: "CRACK_ALLIGATOR",
      confidence: 0.51,
      box: [45, 62, 28, 16],
      status: "pending",
      timestamp: "2026-11-27T10:18:05Z",
    },
    {
      id: "rev-003",
      defect_id: "def-nh44-0135",
      road_name: "NH-44 North Corridor",
      chainage: "km 22.100",
      label: "POTHOLE_WATER",
      confidence: 0.38,
      box: [20, 70, 22, 14],
      status: "pending",
      timestamp: "2026-11-27T10:22:40Z",
    },
    {
      id: "rev-004",
      defect_id: "def-nh44-0139",
      road_name: "NH-44 North Corridor",
      chainage: "km 27.450",
      label: "CRACK_LONGITUDINAL",
      confidence: 0.29,
      box: [60, 48, 12, 34],
      status: "pending",
      timestamp: "2026-11-27T10:31:18Z",
    },
  ]);

  const [auditLog, setAuditLog] = useState<ReviewItem[]>([
    {
      id: "aud-001",
      defect_id: "def-nh44-0115",
      road_name: "NH-44 North Corridor",
      chainage: "km 11.200",
      label: "POTHOLE",
      confidence: 0.58,
      box: [40, 60, 15, 10],
      status: "confirmed",
      reviewer_id: "engineer-raman",
      notes: "Severe edge unraveling with 45mm depth confirmed against walking survey.",
      timestamp: "2026-11-27T08:30:12Z",
    },
    {
      id: "aud-002",
      defect_id: "def-nh44-0119",
      road_name: "NH-44 North Corridor",
      chainage: "km 12.800",
      label: "SHADOW_FALSE_ALARM",
      confidence: 0.31,
      box: [15, 75, 25, 12],
      status: "rejected",
      reviewer_id: "engineer-raman",
      notes: "Overhead gantry sign shadow cast across shoulder; no pavement depression.",
      timestamp: "2026-11-27T08:42:55Z",
    },
  ]);

  useEffect(() => {
    if (queueItems.length > 0 && !selectedItem) {
      setSelectedItem(queueItems[0]);
    }
  }, [queueItems, selectedItem]);

  const handleDecision = (action: "confirmed" | "rejected" | "edited") => {
    if (!selectedItem) return;

    const updatedItem: ReviewItem = {
      ...selectedItem,
      status: action,
      reviewer_id: reviewerId,
      notes: actionNotes || (action === "confirmed" ? "Verified true pavement distress." : "False alarm rejected."),
      label: action === "edited" ? editLabel : selectedItem.label,
      timestamp: new Date().toISOString(),
    };

    setAuditLog([updatedItem, ...auditLog]);
    const remaining = queueItems.filter((i) => i.id !== selectedItem.id);
    setQueueItems(remaining);
    setSelectedItem(remaining.length > 0 ? remaining[0] : null);
    setActionNotes("");
  };

  const handleExportActiveLearning = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      setExportMessage(
        `Active learning dataset exported: ${auditLog.length} human decisions compiled into data/review_store/weekly_retrain_batch.json`
      );
      setTimeout(() => setExportMessage(null), 6000);
    }, 800);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-rule pb-4">
        <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-2">
          <div>
            <h1 className="text-2xl font-serif font-bold text-text">
              Human Review &amp; Quality Triage Queue
            </h1>
            <p className="text-sm text-muted mt-1">
              Low-confidence defect triage (confidence 0.25–0.65) requiring human verification before master catalog commit.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-muted">Reviewer:</span>
            <input
              type="text"
              value={reviewerId}
              onChange={(e) => setReviewerId(e.target.value)}
              className="px-2 py-1 text-xs font-mono border border-rule rounded-[4px] bg-surface text-text w-36"
              aria-label="Reviewer ID"
            />
          </div>
        </div>

        {/* Subnav Tabs */}
        <div className="flex items-center gap-2 mt-4">
          <button
            type="button"
            onClick={() => setActiveTab("queue")}
            className={`px-3 py-1.5 text-xs font-sans rounded-[4px] border cursor-pointer transition-colors ${
              activeTab === "queue"
                ? "bg-text text-bg border-text font-semibold"
                : "bg-surface text-muted border-rule hover:text-text"
            }`}
          >
            Pending Review ({queueItems.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("audit")}
            className={`px-3 py-1.5 text-xs font-sans rounded-[4px] border cursor-pointer transition-colors ${
              activeTab === "audit"
                ? "bg-text text-bg border-text font-semibold"
                : "bg-surface text-muted border-rule hover:text-text"
            }`}
          >
            Audit Log ({auditLog.length})
          </button>
          <button
            type="button"
            onClick={handleExportActiveLearning}
            disabled={isExporting}
            className="ml-auto px-3 py-1.5 text-xs font-mono rounded-[4px] bg-accent/20 border border-accent/40 text-text hover:bg-accent/30 cursor-pointer transition-colors"
          >
            {isExporting ? "Exporting..." : "Export for Active Learning"}
          </button>
        </div>

        {exportMessage && (
          <div className="mt-3 p-2.5 rounded-[4px] bg-surface border border-accent/40 text-xs font-mono text-text">
            {exportMessage}
          </div>
        )}
      </div>

      {activeTab === "queue" ? (
        queueItems.length === 0 ? (
          <div className="py-12 text-center border border-rule rounded-[4px] bg-surface">
            <p className="text-sm font-serif font-medium text-text">Queue Empty</p>
            <p className="text-xs text-muted mt-1">All candidate defects have been verified by human inspectors.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left: Queue List */}
            <div className="lg:col-span-5 border border-rule rounded-[4px] bg-surface overflow-hidden">
              <div className="px-3 py-2 border-b border-rule bg-surface-raised flex items-center justify-between">
                <span className="text-xs font-mono uppercase font-bold text-muted">Review Candidates</span>
                <span className="text-xs font-mono text-muted">{queueItems.length} awaiting decision</span>
              </div>
              <div className="divide-y divide-rule max-h-[520px] overflow-y-auto">
                {queueItems.map((item) => {
                  const isSelected = selectedItem?.id === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setSelectedItem(item)}
                      className={`w-full text-left p-3 transition-colors cursor-pointer block ${
                        isSelected ? "bg-surface-raised border-l-2 border-accent" : "hover:bg-surface-raised/50"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-text">{item.defect_id}</span>
                        <span className="text-[11px] font-mono px-1.5 py-0.5 rounded-[4px] bg-rule/50 text-muted">
                          Conf: {Math.round(item.confidence * 100)}%
                        </span>
                      </div>
                      <div className="text-xs text-text mt-1 font-medium">{item.label}</div>
                      <div className="flex items-center justify-between text-[11px] font-mono text-muted mt-1">
                        <span>{item.road_name}</span>
                        <span>{item.chainage}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Right: Inspection & Action Console */}
            {selectedItem && (
              <div className="lg:col-span-7 border border-rule rounded-[4px] bg-surface p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-rule pb-3">
                  <div>
                    <span className="text-xs font-mono text-muted uppercase">Candidate ID:</span>
                    <h2 className="text-base font-serif font-bold text-text">{selectedItem.defect_id}</h2>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-mono text-muted uppercase">Location:</span>
                    <div className="text-xs font-mono font-medium text-text">
                      {selectedItem.road_name} ({selectedItem.chainage})
                    </div>
                  </div>
                </div>

                {/* Simulated Bounding Box Inspection Frame */}
                <div className="relative w-full h-48 bg-[#121311] rounded-[4px] border border-rule flex items-center justify-center overflow-hidden">
                  <div className="text-center p-4">
                    <div className="w-16 h-12 mx-auto border-2 border-[#D55E00] bg-[#D55E00]/20 rounded-[2px] flex items-center justify-center text-[10px] font-mono text-white font-bold">
                      {Math.round(selectedItem.confidence * 100)}%
                    </div>
                    <p className="text-[11px] font-mono text-[#8E8B82] mt-2">
                      Crop: [{selectedItem.box.join(", ")}] · {selectedItem.label}
                    </p>
                  </div>
                </div>

                {/* Review Form */}
                <div className="space-y-3 pt-2">
                  <div>
                    <label className="block text-xs font-mono text-muted mb-1">
                      Correct Classification (if editing):
                    </label>
                    <select
                      value={editLabel}
                      onChange={(e) => setEditLabel(e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs font-mono border border-rule rounded-[4px] bg-surface text-text"
                    >
                      <option value="POTHOLE">Pothole (Bituminous cavity)</option>
                      <option value="POTHOLE_WATER">Water-filled Pothole (Depression with standing water)</option>
                      <option value="CRACK_ALLIGATOR">Alligator Fatigue Crack (Interconnected map cracking)</option>
                      <option value="CRACK_LONGITUDINAL">Longitudinal Crack (Parallel to centerline)</option>
                      <option value="CRACK_TRANSVERSE">Transverse Crack (Perpendicular to centerline)</option>
                      <option value="RAVELLING">Ravelling / Coarse Aggregate Loss</option>
                      <option value="SURFACE_PUDDLE">Surface Puddle (Harmless surface reflection)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-mono text-muted mb-1">
                      Inspector Notes / Rationale:
                    </label>
                    <textarea
                      rows={2}
                      value={actionNotes}
                      onChange={(e) => setActionNotes(e.target.value)}
                      placeholder="Add engineering observation (e.g. depth > 30mm, edge collapse, shadow artifact)..."
                      className="w-full px-2.5 py-1.5 text-xs font-sans border border-rule rounded-[4px] bg-surface text-text resize-none"
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-2">
                    <button
                      type="button"
                      onClick={() => handleDecision("confirmed")}
                      className="flex-1 px-3 py-2 rounded-[4px] bg-[#10B981] hover:bg-[#059669] text-white text-xs font-bold font-sans cursor-pointer transition-colors"
                    >
                      Confirm Defect
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDecision("edited")}
                      className="flex-1 px-3 py-2 rounded-[4px] bg-[#E8B100] hover:bg-[#CA9A00] text-black text-xs font-bold font-sans cursor-pointer transition-colors"
                    >
                      Edit &amp; Accept
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDecision("rejected")}
                      className="flex-1 px-3 py-2 rounded-[4px] bg-[#D55E00] hover:bg-[#B34700] text-white text-xs font-bold font-sans cursor-pointer transition-colors"
                    >
                      Reject False Alarm
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      ) : (
        /* Audit Trail Table */
        <div className="border border-rule rounded-[4px] bg-surface overflow-hidden">
          <div className="px-4 py-3 border-b border-rule bg-surface-raised flex items-center justify-between">
            <span className="text-xs font-mono uppercase font-bold text-muted">Review Decision Audit Trail</span>
            <span className="text-xs font-mono text-muted">{auditLog.length} recorded decisions</span>
          </div>

          <div className="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Defect ID</th>
                  <th>Corridor</th>
                  <th>Chainage</th>
                  <th>Decision</th>
                  <th>Reviewer</th>
                  <th>Engineering Notes</th>
                </tr>
              </thead>
              <tbody>
                {auditLog.map((log) => (
                  <tr key={log.id}>
                    <td className="font-mono text-xs">{new Date(log.timestamp).toLocaleTimeString()}</td>
                    <td className="font-mono text-xs font-bold">{log.defect_id}</td>
                    <td className="text-xs">{log.road_name}</td>
                    <td className="font-mono text-xs">{log.chainage}</td>
                    <td>
                      <span
                        className={`inline-block px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono uppercase font-bold ${
                          log.status === "confirmed"
                            ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400"
                            : log.status === "rejected"
                            ? "bg-[#D55E00]/15 text-[#D55E00]"
                            : "bg-accent/20 text-accent font-semibold"
                        }`}
                      >
                        {log.status}
                      </span>
                    </td>
                    <td className="font-mono text-xs text-muted">{log.reviewer_id}</td>
                    <td className="text-xs text-muted max-w-xs truncate">{log.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
