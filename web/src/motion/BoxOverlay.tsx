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
  viewMode?: "boxes" | "masks" | "both";
}

/**
 * BoxOverlay with colour-blind safe palette (Wong 2011):
 * - Pothole: #D55E00
 * - Crack: #0072B2
 * - Water-filled: #CC79A7
 * 2px outline, labels placed outside bounding box with collision avoidance.
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
    if (upper.includes("WATER")) return "Water-filled Pothole";
    if (upper.includes("ALLIGATOR") || upper.includes("CROCODILE")) return "Alligator Crack";
    if (upper.includes("LONGITUDINAL") || upper.includes("LONG")) return "Longitudinal Crack";
    if (upper.includes("TRANSVERSE") || upper.includes("TRANS")) return "Transverse Crack";
    if (upper.includes("CRACK")) return "Crack";
    return "Pothole";
  };

  const getColor = (rawLabel: string) => {
    const upper = (rawLabel || "").toUpperCase();
    if (upper.includes("WATER")) {
      return "#CC79A7"; // Colour-blind safe reddish purple
    }
    if (upper.includes("CRACK") || upper.includes("ALLIGATOR") || upper.includes("LONGITUDINAL") || upper.includes("TRANSVERSE")) {
      return "#0072B2"; // Colour-blind safe blue
    }
    return "#D55E00"; // Colour-blind safe vermillion orange
  };

  const labelHeight = 2.6;
  const placedLabels: { x: number; y: number; w: number; h: number }[] = [];

  const items = sorted.map((d, index) => {
    const [x, y, w, h] = d.box;
    const color = getColor(d.label);
    const shortName = getDefectName(d.label);
    const labelText = `${shortName} ${Math.round(d.confidence * 100)}%`;
    const labelWidth = Math.max(14.0, Math.min(28.0, labelText.length * 1.1 + 3.0));

    // Prefer outside above; fallback to outside below if too close to frame top
    const candidates = [
      { x, y: y - labelHeight - 0.5 }, // Above top edge
      { x, y: y + h + 0.5 },           // Below bottom edge
      { x: Math.max(0.5, x + w - labelWidth), y: y - labelHeight - 0.5 }, // Above right-aligned
      { x: Math.max(0.5, x + w - labelWidth), y: y + h + 0.5 },           // Below right-aligned
    ].map((c) => ({
      x: Math.max(0.5, Math.min(100 - labelWidth - 0.5, c.x)),
      y: Math.max(0.5, Math.min(100 - labelHeight - 0.5, c.y)),
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
    const showLabel = isActive || (bestPos !== null && index < 20);
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
            style={{ opacity: isDimmed ? 0.5 : 1 }}
            onMouseEnter={() => onHover(d.id)}
            onMouseLeave={() => onHover(null)}
            onClick={() => onSelect(d.id)}
            role="button"
            tabIndex={0}
            aria-label={`${d.label} ${Math.round(d.confidence * 100)}%`}
          >
            {/* Segmentation Polygon if available */}
            {(viewMode === "masks" || viewMode === "both") &&
              d.polygon &&
              d.polygon.length >= 3 && (
                <polygon
                  points={d.polygon.map(([px, py]) => `${px},${py}`).join(" ")}
                  fill={color}
                  fillOpacity={isActive ? 0.25 : 0.15}
                  stroke={color}
                  strokeWidth="2"
                  vectorEffect="non-scaling-stroke"
                />
              )}

            {/* Bounding Box: 2px outline */}
            {(viewMode === "boxes" || viewMode === "both" || !d.polygon || d.polygon.length < 3) && (
              <rect
                x={x}
                y={y}
                width={w}
                height={h}
                fill={color}
                fillOpacity={isActive ? 0.18 : 0.08}
                stroke={color}
                strokeWidth="2"
                vectorEffect="non-scaling-stroke"
                rx={0.5}
              />
            )}

            {/* Outside Label with collision avoidance */}
            {showLabel && (
              <g transform={`translate(${labelX}, ${labelY})`}>
                <rect
                  x={0}
                  y={0}
                  width={labelWidth}
                  height={labelHeight}
                  fill={color}
                  stroke="#1B1A17"
                  strokeWidth="0.5"
                  vectorEffect="non-scaling-stroke"
                  rx={0.3}
                />
                <text
                  x={0.8}
                  y={labelHeight * 0.72}
                  fill="#FFFFFF"
                  fontSize={1.5}
                  fontFamily="'IBM Plex Mono', monospace"
                  fontWeight="600"
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
