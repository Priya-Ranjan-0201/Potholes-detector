import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Camera, Download, AlertTriangle } from "../components/Icons";

interface PriorityItem {
  id: string;
  survey_id: string;
  survey_name: string;
  asset_type: string;
  place_text: string;
  label: string;
  severity_level: string;
  severity_score: number;
  exposure_factor: number;
  priority_score: number;
  reason: string;
  repair_status: string;
  created_at: string;
}

export const PriorityListPage: React.FC = () => {
  const [assetFilter, setAssetFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const { data: items = [] } = useQuery<PriorityItem[]>({
    queryKey: ["priorityList", assetFilter, severityFilter, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (assetFilter !== "all") params.append("asset_type", assetFilter);
      if (severityFilter !== "all") params.append("min_severity", severityFilter);
      if (statusFilter !== "all") params.append("status", statusFilter);

      const res = await fetch(`http://localhost:8000/api/v1/priority?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to load priority items");
      return res.json();
    },
  });

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

  const handleExportCsv = () => {
    window.open("http://localhost:8000/api/v1/priority/export/csv", "_blank");
  };

  return (
    <div className="space-y-6 pb-12 text-[var(--text-main)]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[var(--border-rule)] pb-4">
        <div>
          <h1 className="font-serif font-bold text-2xl sm:text-3xl tracking-tight text-[var(--text-main)]">
            Repair Priority Ranking
          </h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            Prioritised maintenance queue ranked by computed risk: Priority Score = Severity × Exposure.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportCsv}
            disabled={items.length === 0}
            className="px-3.5 py-2 rounded text-xs font-medium border border-[var(--border-subtle)] hover:bg-[var(--bg-surface-2)] transition-colors flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-rule)] text-xs">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[var(--text-muted)] uppercase text-[11px]">Asset:</span>
          <select
            value={assetFilter}
            onChange={(e) => setAssetFilter(e.target.value)}
            className="px-2 py-1 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] text-[var(--text-main)]"
          >
            <option value="all">All Asset Types</option>
            <option value="Road">Road Pavements</option>
            <option value="Bridge">Bridge Decks</option>
            <option value="Retaining Wall">Retaining Walls</option>
            <option value="Footpath">Footpaths</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[var(--text-muted)] uppercase text-[11px]">Severity:</span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-2 py-1 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] text-[var(--text-main)]"
          >
            <option value="all">All Severities</option>
            <option value="Critical">Critical Only</option>
            <option value="High">High & Above</option>
            <option value="Moderate">Moderate & Above</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[var(--text-muted)] uppercase text-[11px]">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2 py-1 rounded border border-[var(--border-subtle)] bg-[var(--bg-canvas)] text-[var(--text-main)]"
          >
            <option value="all">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Scheduled">Scheduled</option>
            <option value="Repaired">Repaired</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Main Ruled Table */}
      {items.length === 0 ? (
        <div className="p-12 text-center border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded space-y-4">
          <div className="w-12 h-12 rounded-full bg-[var(--bg-surface-2)] mx-auto flex items-center justify-center text-[var(--text-muted)]">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="font-semibold text-base text-[var(--text-main)]">No issues yet</h3>
            <p className="text-xs sm:text-sm text-[var(--text-muted)] max-w-md mx-auto">
              No defect records match the selected criteria. Analyse an image or video to start a survey.
            </p>
          </div>
          <div className="pt-2">
            <Link
              to="/scanner"
              className="px-4 py-2 rounded text-xs font-medium bg-[var(--primary)] text-[var(--primary-text)] hover:opacity-90 inline-flex items-center gap-1.5"
            >
              <Camera className="w-3.5 h-3.5" />
              <span>Analyse an Image</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-[var(--bg-surface-2)] text-xs text-[var(--text-muted)] uppercase font-mono border-b border-[var(--border-rule)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Priority Rank</th>
                <th className="px-4 py-3 font-semibold">Defect Type</th>
                <th className="px-4 py-3 font-semibold">Survey / Location</th>
                <th className="px-4 py-3 font-semibold">Severity</th>
                <th className="px-4 py-3 font-semibold">Exposure</th>
                <th className="px-4 py-3 font-semibold">Priority Score</th>
                <th className="px-4 py-3 font-semibold">Assessment Rationale</th>
                <th className="px-4 py-3 font-semibold">Repair Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-rule)] text-[var(--text-main)]">
              {items.map((it, idx) => (
                <tr key={it.id} className="hover:bg-[var(--bg-surface-2)]/50 transition-colors">
                  <td className="px-4 py-3 font-mono font-bold text-sm">#{idx + 1}</td>
                  <td className="px-4 py-3 font-medium">
                    <div>{it.label}</div>
                    <span className="text-[10px] font-mono text-[var(--text-faint)]">{it.id}</span>
                  </td>
                  <td className="px-4 py-3 text-xs">
                    <div className="font-medium">{it.survey_name}</div>
                    <span className="text-[11px] font-mono text-[var(--text-muted)]">{it.place_text}</span>
                  </td>
                  <td className="px-4 py-3">
                    {getSeverityBadge(it.severity_level)}
                    <div className="text-[10px] font-mono text-[var(--text-muted)]">Score: {it.severity_score}/100</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{it.exposure_factor.toFixed(1)}x ({it.asset_type})</td>
                  <td className="px-4 py-3 font-mono font-bold text-sm text-[var(--primary)]">{it.priority_score}</td>
                  <td className="px-4 py-3 text-xs text-[var(--text-muted)] max-w-xs">{it.reason}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--bg-surface-2)] border border-[var(--border-subtle)]">
                      {it.repair_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
