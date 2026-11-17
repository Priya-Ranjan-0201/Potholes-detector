import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Camera, Layers, Plus } from "../components/Icons";

interface SurveyRecord {
  id: string;
  name: string;
  asset_type: string;
  place_text: string;
  inspector_name: string;
  created_at: string;
  issue_count: number;
  worst_severity: string;
  issues: any[];
  notes?: string;
}

export const SurveysPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [assetType, setAssetType] = useState("Road");
  const [placeText, setPlaceText] = useState("");
  const [inspectorName, setInspectorName] = useState("Lead Surveyor");
  const [selectedSurvey, setSelectedSurvey] = useState<SurveyRecord | null>(null);

  const { data: surveys = [] } = useQuery<SurveyRecord[]>({
    queryKey: ["surveysList"],
    queryFn: async () => {
      const res = await fetch("/api/v1/surveys");
      if (!res.ok) throw new Error("Failed to fetch surveys");
      return res.json();
    },
  });

  const createSurveyMutation = useMutation({
    mutationFn: async (payload: { name: string; asset_type: string; place_text: string; inspector_name: string }) => {
      const res = await fetch("/api/v1/surveys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed to create survey");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["surveysList"] });
      setIsModalOpen(false);
      setName("");
      setPlaceText("");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    createSurveyMutation.mutate({
      name,
      asset_type: assetType,
      place_text: placeText || "Field Coordinates Unset",
      inspector_name: inspectorName,
    });
  };

  const getSeverityBadge = (level: string) => {
    switch (level) {
      case "Critical":
        return <span className="inline-flex items-center gap-1 text-xs font-mono font-semibold text-red-700 dark:text-red-400">◆ Critical</span>;
      case "High":
        return <span className="inline-flex items-center gap-1 text-xs font-mono font-semibold text-orange-700 dark:text-orange-400">▲ High</span>;
      case "Moderate":
        return <span className="inline-flex items-center gap-1 text-xs font-mono font-semibold text-amber-700 dark:text-amber-400">■ Moderate</span>;
      default:
        return <span className="inline-flex items-center gap-1 text-xs font-mono font-semibold text-emerald-700 dark:text-emerald-400">● Low</span>;
    }
  };

  return (
    <div className="space-y-6 pb-12 text-[var(--text-main)]">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[var(--border-rule)] pb-4">
        <div>
          <h1 className="font-serif font-bold text-2xl sm:text-3xl tracking-tight text-[var(--text-main)]">
            Infrastructure Surveys
          </h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            Archived inspection surveys for road corridors, bridge decks, and retaining structures.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-3.5 py-2 rounded text-xs font-medium bg-[var(--primary)] text-[var(--primary-text)] hover:opacity-90 transition-opacity flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>New Survey</span>
          </button>
        </div>
      </div>

      {/* Main Ruled Table */}
      {surveys.length === 0 ? (
        <div className="p-12 text-center border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded space-y-4">
          <div className="w-12 h-12 rounded-full bg-[var(--bg-surface-2)] mx-auto flex items-center justify-center text-[var(--text-muted)]">
            <Layers className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="font-semibold text-base text-[var(--text-main)]">No surveys recorded yet</h3>
            <p className="text-xs sm:text-sm text-[var(--text-muted)] max-w-md mx-auto">
              Surveys are created when field photos or video runs are imported and saved during inspection.
            </p>
          </div>
          <div className="pt-2">
            <Link
              to="/scanner"
              className="px-4 py-2 rounded text-xs font-medium bg-[var(--primary)] text-[var(--primary-text)] hover:opacity-90 inline-flex items-center gap-1.5"
            >
              <Camera className="w-3.5 h-3.5" />
              <span>Analyse Image to Start Survey</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-[var(--bg-surface-2)] text-xs text-[var(--text-muted)] uppercase font-mono border-b border-[var(--border-rule)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Survey Identifier</th>
                <th className="px-4 py-3 font-semibold">Asset Type</th>
                <th className="px-4 py-3 font-semibold">Location</th>
                <th className="px-4 py-3 font-semibold">Date (UTC)</th>
                <th className="px-4 py-3 font-semibold">Inspector</th>
                <th className="px-4 py-3 font-semibold">Defects</th>
                <th className="px-4 py-3 font-semibold">Worst Severity</th>
                <th className="px-4 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-rule)] text-[var(--text-main)]">
              {surveys.map((s) => (
                <tr key={s.id} className="hover:bg-[var(--bg-surface-2)]/50 transition-colors">
                  <td className="px-4 py-3 font-medium">
                    <div>{s.name}</div>
                    <span className="text-[11px] font-mono text-[var(--text-faint)]">{s.id}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--bg-surface-2)] border border-[var(--border-subtle)]">
                      {s.asset_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{s.place_text}</td>
                  <td className="px-4 py-3 text-xs text-[var(--text-muted)]">{s.created_at}</td>
                  <td className="px-4 py-3 text-xs">{s.inspector_name}</td>
                  <td className="px-4 py-3 font-mono font-semibold">{s.issue_count}</td>
                  <td className="px-4 py-3">{getSeverityBadge(s.worst_severity)}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => setSelectedSurvey(s)}
                      className="px-2.5 py-1 rounded text-xs font-medium border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-2)]"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* New Survey Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-rule)] rounded-lg max-w-md w-full p-6 space-y-4 shadow-xl">
            <h2 className="font-serif font-bold text-lg text-[var(--text-main)]">Create Infrastructure Survey</h2>
            <form onSubmit={handleCreate} className="space-y-3.5 text-xs sm:text-sm">
              <div>
                <label className="block text-xs font-mono text-[var(--text-muted)] mb-1">Survey Name / Corridor</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. NH-44 KM 124-128 Northbound"
                  className="w-full px-3 py-2 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] text-[var(--text-main)]"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-[var(--text-muted)] mb-1">Asset Type</label>
                <select
                  value={assetType}
                  onChange={(e) => setAssetType(e.target.value)}
                  className="w-full px-3 py-2 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] text-[var(--text-main)]"
                >
                  <option value="Road">Road Pavement</option>
                  <option value="Bridge">Bridge Deck / Abutment</option>
                  <option value="Retaining Wall">Retaining Wall</option>
                  <option value="Culvert">Drainage Culvert</option>
                  <option value="Footpath">Pedestrian Footpath</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-mono text-[var(--text-muted)] mb-1">Location Coordinates / Landmark</label>
                <input
                  type="text"
                  value={placeText}
                  onChange={(e) => setPlaceText(e.target.value)}
                  placeholder="e.g. 13.0827° N, 80.2707° E or Sector 4"
                  className="w-full px-3 py-2 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] text-[var(--text-main)]"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-[var(--text-muted)] mb-1">Inspector Name</label>
                <input
                  type="text"
                  value={inspectorName}
                  onChange={(e) => setInspectorName(e.target.value)}
                  className="w-full px-3 py-2 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] text-[var(--text-main)]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3 py-1.5 rounded text-xs border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-2)]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createSurveyMutation.isPending}
                  className="px-4 py-1.5 rounded text-xs font-medium bg-[var(--primary)] text-[var(--primary-text)] hover:opacity-90"
                >
                  {createSurveyMutation.isPending ? "Creating..." : "Create Survey"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Survey Details Drawer / Modal */}
      {selectedSurvey && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-rule)] rounded-lg max-w-2xl w-full p-6 space-y-4 shadow-xl max-h-[85vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-[var(--border-rule)] pb-3">
              <div>
                <h3 className="font-serif font-bold text-lg text-[var(--text-main)]">{selectedSurvey.name}</h3>
                <p className="text-xs text-[var(--text-muted)] font-mono">
                  {selectedSurvey.id} · {selectedSurvey.asset_type} · {selectedSurvey.place_text}
                </p>
              </div>
              <button
                onClick={() => setSelectedSurvey(null)}
                className="text-xs px-2 py-1 rounded border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-2)]"
              >
                Close
              </button>
            </div>

            <div className="space-y-3">
              <h4 className="text-xs uppercase font-mono font-semibold text-[var(--text-muted)]">
                Recorded Distress Observations ({selectedSurvey.issues.length})
              </h4>
              {selectedSurvey.issues.length === 0 ? (
                <p className="text-xs text-[var(--text-muted)] italic">
                  No issues attached to this survey. Use the Analyse tab to attach detections.
                </p>
              ) : (
                <div className="space-y-2">
                  {selectedSurvey.issues.map((iss, i) => (
                    <div key={i} className="p-3 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] flex justify-between items-center text-xs">
                      <div>
                        <span className="font-semibold">{iss.label || "Distress"}</span>
                        <p className="text-[11px] text-[var(--text-muted)]">{iss.severity_breakdown || "Recorded detection"}</p>
                      </div>
                      <div className="text-right">
                        <div>{getSeverityBadge(iss.severity)}</div>
                        <span className="text-[10px] font-mono text-[var(--text-faint)]">Status: {iss.repair_status || "Open"}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
