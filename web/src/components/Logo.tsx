import React from "react";

interface LogoProps {
  className?: string;
  showWordmark?: boolean;
  size?: "sm" | "md" | "lg" | "xl";
  alt?: string;
}

export const RoadGlyph: React.FC<{ sizeClass?: string; className?: string }> = ({
  sizeClass = "w-8 h-8",
  className = "",
}) => (
  <svg
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={`${sizeClass} shrink-0 ${className}`}
    aria-label="Road Glyph"
  >
    <rect width="32" height="32" rx="8" className="fill-primary-700 dark:fill-primary-600" />
    {/* Left lane border */}
    <path d="M10 26L13 6" stroke="white" strokeWidth="2" strokeLinecap="round" opacity="0.9" />
    {/* Right lane border */}
    <path d="M22 26L19 6" stroke="white" strokeWidth="2" strokeLinecap="round" opacity="0.9" />
    {/* Dashed centre line */}
    <path d="M16 25L16 20" stroke="white" strokeWidth="2" strokeLinecap="round" opacity="0.95" />
    <path d="M16 16L16 12" stroke="white" strokeWidth="1.75" strokeLinecap="round" opacity="0.8" />
    <path d="M16 9L16 7" stroke="white" strokeWidth="1.5" strokeLinecap="round" opacity="0.65" />
  </svg>
);

export const Logo: React.FC<LogoProps> = ({
  className = "",
  showWordmark = false,
  size = "md",
  alt = "ScamRoad",
}) => {
  const dim = {
    sm: "w-7 h-7",
    md: "w-8 h-8",
    lg: "w-10 h-10",
    xl: "w-12 h-12",
  }[size];

  if (showWordmark) {
    return (
      <div className={`flex items-center gap-2 select-none ${className}`}>
        <RoadGlyph sizeClass={dim} />
        <span className="font-heading font-bold text-base tracking-tight text-slate-900 dark:text-white">
          {alt}
        </span>
      </div>
    );
  }

  return <RoadGlyph sizeClass={dim} className={className} />;
};
