"""Highway Stretch Chainage Reporting and Export Service (Gate E).

Implements Gate E requirements:
- Defect reports per highway stretch grouped by chainage (km).
- Defect density (defects per km) and severity distribution.
- Multi-format exports: CSV (RFC 4180), GeoJSON FeatureCollection, Structured PDF report.
- Mandatory Rule R3 disclaimers (No official government claims).
"""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime
from typing import Any, Dict, List


class ChainageReportingService:
    """Generates stretch reports grouped by chainage (km) and formatted exports."""

    def group_by_chainage(
        self,
        stretch_name: str,
        start_km: float,
        end_km: float,
        defects: List[Dict[str, Any]],
        bin_size_km: float = 0.5,
    ) -> Dict[str, Any]:
        """Aggregate defects along a highway stretch into chainage intervals."""
        num_bins = int(round((end_km - start_km) / bin_size_km))
        bins = []

        for i in range(num_bins):
            b_start = round(start_km + i * bin_size_km, 3)
            b_end = round(b_start + bin_size_km, 3)
            bins.append({
                "chainage_start_km": b_start,
                "chainage_end_km": b_end,
                "chainage_label": f"km {b_start:.3f} - km {b_end:.3f}",
                "defects": [],
                "pothole_count": 0,
                "crack_count": 0,
                "critical_count": 0,
            })

        for d in defects:
            # Assign chainage based on explicit km attribute or interpolated from start
            d_km = float(d.get("chainage_km", start_km + 0.1))
            assigned = False
            for b in bins:
                if b["chainage_start_km"] <= d_km < b["chainage_end_km"]:
                    b["defects"].append(d)
                    label = str(d.get("label", "POTHOLE")).upper()
                    if "POTHOLE" in label:
                        b["pothole_count"] += 1
                    else:
                        b["crack_count"] += 1
                    if d.get("severity") == "Critical" or d.get("score", 0) >= 70:
                        b["critical_count"] += 1
                    assigned = True
                    break
            if not assigned and bins:
                bins[-1]["defects"].append(d)

        total_defects = len(defects)
        stretch_length_km = max(0.1, end_km - start_km)
        density_per_km = round(total_defects / stretch_length_km, 2)

        return {
            "stretch_name": stretch_name,
            "start_km": start_km,
            "end_km": end_km,
            "total_length_km": round(stretch_length_km, 3),
            "total_defects": total_defects,
            "defect_density_per_km": density_per_km,
            "chainage_bins": bins,
            "generated_at": datetime.now(UTC).isoformat(),
            "disclaimer": "Student research project. Not an official government system. Not safety-certified.",
        }

    def export_csv(self, chainage_data: Dict[str, Any]) -> str:
        """Export chainage report as RFC 4180 CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["# ScamRoad Chainage Survey Report"])
        writer.writerow(["# Stretch", chainage_data.get("stretch_name", "")])
        writer.writerow(["# Total Length (km)", chainage_data.get("total_length_km", 0)])
        writer.writerow(["# Defect Density (per km)", chainage_data.get("defect_density_per_km", 0)])
        writer.writerow(["# Generated At", chainage_data.get("generated_at", "")])
        writer.writerow(["# Legal Disclaimer", chainage_data.get("disclaimer", "")])
        writer.writerow([])

        writer.writerow([
            "chainage_label",
            "chainage_start_km",
            "chainage_end_km",
            "total_defects",
            "pothole_count",
            "crack_count",
            "critical_count",
            "density_per_km",
        ])

        for b in chainage_data.get("chainage_bins", []):
            b_cnt = len(b["defects"])
            b_len = max(0.01, b["chainage_end_km"] - b["chainage_start_km"])
            writer.writerow([
                b["chainage_label"],
                b["chainage_start_km"],
                b["chainage_end_km"],
                b_cnt,
                b["pothole_count"],
                b["crack_count"],
                b["critical_count"],
                round(b_cnt / b_len, 2),
            ])

        return output.getvalue()

    def export_geojson(self, chainage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export chainage bins and defects as standard GeoJSON FeatureCollection."""
        features = []

        for b in chainage_data.get("chainage_bins", []):
            b_cnt = len(b["defects"])
            for d in b["defects"]:
                lat = float(d.get("latitude", 12.9716))
                lon = float(d.get("longitude", 77.5946))
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat],
                    },
                    "properties": {
                        "defect_id": str(d.get("defect_id", d.get("id", ""))),
                        "label": d.get("label", "POTHOLE"),
                        "severity": d.get("severity", "Moderate"),
                        "chainage_km": d.get("chainage_km", b["chainage_start_km"]),
                        "chainage_interval": b["chainage_label"],
                        "stretch_name": chainage_data.get("stretch_name", ""),
                    },
                })

        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "stretch_name": chainage_data.get("stretch_name", ""),
                "total_defects": chainage_data.get("total_defects", 0),
                "generated_at": chainage_data.get("generated_at", ""),
                "disclaimer": chainage_data.get("disclaimer", ""),
            },
        }

    def export_pdf_summary(self, chainage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured payload for PDF generation."""
        bins = chainage_data.get("chainage_bins", [])
        worst_bins = sorted(bins, key=lambda b: len(b["defects"]), reverse=True)[:3]

        return {
            "title": f"Highway Condition Survey Report: {chainage_data.get('stretch_name', '')}",
            "generated_at": chainage_data.get("generated_at", ""),
            "total_length_km": chainage_data.get("total_length_km", 0),
            "total_defects": chainage_data.get("total_defects", 0),
            "defect_density_per_km": chainage_data.get("defect_density_per_km", 0),
            "worst_distress_segments": [
                {
                    "interval": b["chainage_label"],
                    "defect_count": len(b["defects"]),
                    "critical_count": b["critical_count"],
                }
                for b in worst_bins
            ],
            "footer_disclaimer": "Student research project. Not an official government system. Not safety-certified.",
        }


chainage_reporting_service = ChainageReportingService()
