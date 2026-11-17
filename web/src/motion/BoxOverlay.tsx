import React from "react";

export interface BoundingBoxItem {
  id: string;
  label: string;
  confidence: number;
  box: [number, number, number, number]; // [x%, y%, w%, h%]
  polygon?: [number, number][]; // [[x%, y%], ...] non-intersecting contour
  severity?: string;
  score?: number;
}

interface BoxOverlayProps {
  detections: BoundingBoxItem[];
  activeId: string | null;
  onHover: (id: string | null) => void;
  onSelect: (id: string) => void;
  className?: string;
  colorScheme?: "emerald" | "severity";
  viewMode?: "boxes" | "masks" | "both";
}

/**
 * High-contrast dark bounding box overlay with non-overlapping label badges.
 */
export const BoxOverlay: React.FC<BoxOverlayProps> = ({
  detections,
  activeId,
  onHover,
  onSelect,
  className = "",
  viewMode = "boxes",
}) => {
  const sorted = [...detections].sort((a, b) => b.confidence - a.confidence);

  const getDefectName = (rawLabel: string) => {
    const upper = (rawLabel || "").toUpperCase();
    if (upper.includes("ALLIGATOR") || upper.includes("CROCODILE")) return "Alligator";
    if (upper.includes("LONGITUDINAL") || upper.includes("LONG")) return "Long. Crack";
    if (upper.includes("TRANSVERSE") || upper.includes("TRANS")) return "Trans. Crack";
    if (upper.includes("CRACK")) return "Crack";
    return "Pothole";
  };

  const getColor = (rawLabel: string) => {
    const upper = (rawLabel || "").toUpperCase();
    if (upper.includes("WATER")) return "#CC79A7"; // Water-filled pothole: Okabe-Ito reddish purple
    if (upper.includes("POTHOLE")) return "#D55E00"; // Pothole: Okabe-Ito vermilion
    if (upper.includes("CRACK")) return "#0072B2"; // Crack family: Okabe-Ito blue
    if (upper.includes("SPALLING")) return "#E69F00"; // Spalling: Okabe-Ito yellow-orange
    if (upper.includes("REBAR") || upper.includes("CORROSION")) return "#A6761D"; // Rebar / corrosion: dark amber
    if (upper.includes("EFFLORESCENCE")) return "#56B4E9"; // Efflorescence: sky blue
    return "#0072B2"; // Default
  };

  const labelHeight = 2.4;
  const placedLabels: { x: number; y: number; w: number; h: number }[] = [];

  const items = sorted.map((d, index) => {
    const [x, y, w, h] = d.box;
    const color = getColor(d.label);
    const shortName = getDefectName(d.label);
    const labelText = `${shortName} ${Math.round(d.confidence * 100)}%`;
    const labelWidth = Math.max(12.0, Math.min(24.0, labelText.length * 1.05 + 2.5));

    const candidates = [
      { x, y: y - labelHeight - 0.3 },
      { x: x + 0.3, y: y + 0.3 },
      { x, y: y + h + 0.3 },
      { x: Math.max(0.5, x + w - labelWidth), y: y - labelHeight - 0.3 },
      { x: Math.max(0.5, x + w - labelWidth - 0.3), y: y + 0.3 },
    ].map((c) => ({
      x: Math.max(0.4, Math.min(100 - labelWidth - 0.4, c.x)),
      y: Math.max(0.4, Math.min(100 - labelHeight - 0.4, c.y)),
    }));

    let bestPos: { x: number; y: number } | null = null;
    for (const cand of candidates) {
      const collides = placedLabels.some(
        (pl) =>
          !(
            cand.x + labelWidth <= pl.x ||
            cand.x >= pl.x + pl.w ||
            cand.y + labelHeight <= pl.y ||
            cand.y >= pl.y + pl.h
          )
      );
      if (!collides) {
        bestPos = cand;
        break;
      }
    }

    const isActive = activeId === d.id;
    const showLabel = isActive || (bestPos !== null && index < 15);
    const finalPos = bestPos ?? candidates[0];
    if (bestPos !== null) {
      placedLabels.push({ x: finalPos.x, y: finalPos.y, w: labelWidth, h: labelHeight });
    }

    return {
      d,
      x,
      y,
      w,
      h,
      labelX: finalPos.x,
      labelY: finalPos.y,
      labelWidth,
      labelText,
      showLabel,
      color,
    };
  });

  const ordered = [
    ...items.filter((i) => activeId !== i.d.id),
    ...items.filter((i) => activeId === i.d.id),
  ];

  return (
    <svg
      className={`absolute inset-0 w-full h-full pointer-events-none select-none ${className}`}
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      {ordered.map((item) => {
        const { d, x, y, w, h, labelX, labelY, labelWidth, labelText, showLabel, color } = item;
        const isActive = activeId === d.id;
        const isDimmed = activeId !== null && !isActive;

        return (
          <g
            key={d.id}
            className="pointer-events-auto cursor-pointer transition-opacity duration-150"
            style={{ opacity: isDimmed ? 0.65 : 1 }}
            onMouseEnter={() => onHover(d.id)}
            onMouseLeave={() => onHover(null)}
            onClick={() => onSelect(d.id)}
            role="button"
            tabIndex={0}
            aria-label={`${d.label} ${Math.round(d.confidence * 100)}%`}
          >
            {(viewMode === "masks" || viewMode === "both") &&
              d.polygon &&
              d.polygon.length >= 3 && (
                <>
                  <polygon
                    points={d.polygon.map(([px, py]) => `${px},${py}`).join(" ")}
                    fill="none"
                    stroke="#FFFFFF"
                    strokeWidth={isActive ? 1.6 : 1.2}
                    strokeLinejoin="round"
                    strokeOpacity={0.85}
                  />
                  <polygon
                    points={d.polygon.map(([px, py]) => `${px},${py}`).join(" ")}
                    fill={color}
                    fillOpacity={isActive ? 0.08 : 0.05}
                    stroke={color}
                    strokeWidth={isActive ? 1.1 : 0.8}
                    strokeLinejoin="round"
                  />
                </>
              )}

            {(viewMode === "boxes" || viewMode === "both" || !d.polygon || d.polygon.length < 3) && (
              <>
                {/* 3px High-contrast Halo Layer */}
                <rect
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  fill="none"
                  stroke="#FFFFFF"
                  strokeOpacity={0.9}
                  strokeWidth={isActive ? 1.7 : 1.3}
                  rx={0.35}
                />
                <rect
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  fill={color}
                  fillOpacity={isActive ? 0.08 : 0.04}
                  stroke={color}
                  strokeWidth={isActive ? 1.15 : 0.85}
                  rx={0.35}
                />
              </>
            )}

            {showLabel && (
              <g transform={`translate(${labelX}, ${labelY})`}>
                <rect
                  x={0}
                  y={0}
                  width={labelWidth}
                  height={labelHeight}
                  fill={color}
                  stroke="#000000"
                  strokeOpacity={0.55}
                  strokeWidth={0.22}
                  rx={0.35}
                />
                <text
                  x={0.75}
                  y={labelHeight * 0.72}
                  fill="#ffffff"
                  fontSize={1.45}
                  fontFamily="system-ui, -apple-system, sans-serif"
                  fontWeight="700"
                >
                  {labelText}
                </text>
              </g>
            )}
          </g>
        );
      })}
    </svg>
  );
};
