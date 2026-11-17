import React from "react";
import { BookOpen, AlertTriangle, ShieldCheck } from "../components/Icons";

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-12 text-[var(--text-main)]">
      {/* Page Header */}
      <div className="space-y-3 pb-6 border-b border-[var(--border-rule)]">
        <p className="text-xs font-mono uppercase tracking-wider text-[var(--primary)] font-semibold">
          Methodology & System Architecture
        </p>
        <h1 className="font-serif font-bold text-3xl sm:text-4xl tracking-tight text-[var(--text-main)]">
          AI-Powered Road and Infrastructure Damage Detection and Severity Assessment
        </h1>
        <p className="text-sm sm:text-base text-[var(--text-muted)] leading-relaxed max-w-2xl">
          A computer-vision system for surveying road and civic infrastructure that detects damage such as
          potholes, cracks, and structural deterioration from images or video, and assigns a calibrated severity
          score to prioritise maintenance work.
        </p>
      </div>

      {/* Student Research Disclaimer (Rule H5) */}
      <div className="p-4 rounded border border-[var(--border-subtle)] bg-[var(--bg-surface-2)] flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs sm:text-sm text-[var(--text-muted)] space-y-1">
          <p className="font-semibold text-[var(--text-main)]">Student Research Project Disclaimer</p>
          <p>
            This software is an academic B.Tech capstone research project in computer vision and civil infrastructure
            surveying. It is <strong>not</strong> an official government system, not affiliated with any highway authority
            or municipal corporation, and <strong>not safety-certified</strong> for autonomous vehicular control or
            life-critical safety decisions.
          </p>
        </div>
      </div>

      {/* System Pipeline Architecture Diagram */}
      <section className="space-y-4">
        <h2 className="font-serif font-bold text-xl text-[var(--text-main)]">Detection & Severity Pipeline</h2>
        <p className="text-xs sm:text-sm text-[var(--text-muted)]">
          The processing pipeline executes through 5 sequential learned stages designed to eliminate off-road false alarms:
        </p>

        <div className="p-4 border border-[var(--border-rule)] bg-[var(--bg-surface)] rounded overflow-x-auto">
          <svg className="w-full min-w-[620px] h-32" viewBox="0 0 760 110" fill="none">
            {/* Stage 1 */}
            <rect x="10" y="20" width="130" height="70" rx="4" fill="var(--bg-surface-2)" stroke="var(--border-subtle)" strokeWidth="1.5" />
            <text x="75" y="45" fill="var(--text-main)" fontSize="12" fontWeight="600" textAnchor="middle" fontFamily="sans-serif">Stage A: Input Gate</text>
            <text x="75" y="65" fill="var(--text-muted)" fontSize="10" textAnchor="middle" fontFamily="monospace">Rejects Diagrams</text>

            {/* Arrow 1 */}
            <path d="M140 55 H165" stroke="var(--primary)" strokeWidth="2" markerEnd="url(#arrow)" />

            {/* Stage 2 */}
            <rect x="165" y="20" width="130" height="70" rx="4" fill="var(--bg-surface-2)" stroke="var(--border-subtle)" strokeWidth="1.5" />
            <text x="230" y="45" fill="var(--text-main)" fontSize="12" fontWeight="600" textAnchor="middle" fontFamily="sans-serif">Stage B: Road Mask</text>
            <text x="230" y="65" fill="var(--text-muted)" fontSize="10" textAnchor="middle" fontFamily="monospace">Drivable Area Prior</text>

            {/* Arrow 2 */}
            <path d="M295 55 H320" stroke="var(--primary)" strokeWidth="2" markerEnd="url(#arrow)" />

            {/* Stage 3 */}
            <rect x="320" y="20" width="130" height="70" rx="4" fill="var(--bg-surface-2)" stroke="var(--border-subtle)" strokeWidth="1.5" />
            <text x="385" y="45" fill="var(--text-main)" fontSize="12" fontWeight="600" textAnchor="middle" fontFamily="sans-serif">Stage C: Neural Detector</text>
            <text x="385" y="65" fill="var(--text-muted)" fontSize="10" textAnchor="middle" fontFamily="monospace">Potholes & Cracks</text>

            {/* Arrow 3 */}
            <path d="M450 55 H475" stroke="var(--primary)" strokeWidth="2" markerEnd="url(#arrow)" />

            {/* Stage 4 */}
            <rect x="475" y="20" width="130" height="70" rx="4" fill="var(--bg-surface-2)" stroke="var(--border-subtle)" strokeWidth="1.5" />
            <text x="540" y="45" fill="var(--text-main)" fontSize="12" fontWeight="600" textAnchor="middle" fontFamily="sans-serif">Stage D: Severity Score</text>
            <text x="540" y="65" fill="var(--text-muted)" fontSize="10" textAnchor="middle" fontFamily="monospace">0–100 Monotonic Model</text>

            {/* Arrow 4 */}
            <path d="M605 55 H630" stroke="var(--primary)" strokeWidth="2" markerEnd="url(#arrow)" />

            {/* Stage 5 */}
            <rect x="630" y="20" width="120" height="70" rx="4" fill="var(--bg-surface-2)" stroke="var(--primary)" strokeWidth="1.5" />
            <text x="690" y="45" fill="var(--primary)" fontSize="12" fontWeight="600" textAnchor="middle" fontFamily="sans-serif">Stage E: Priority</text>
            <text x="690" y="65" fill="var(--text-muted)" fontSize="10" textAnchor="middle" fontFamily="monospace">Severity × Exposure</text>

            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--primary)" />
              </marker>
            </defs>
          </svg>
        </div>
      </section>

      {/* Severity Formulation & Weights */}
      <section className="space-y-4">
        <h2 className="font-serif font-bold text-xl text-[var(--text-main)]">Severity Scoring Formulation</h2>
        <div className="text-xs sm:text-sm text-[var(--text-muted)] space-y-2 leading-relaxed">
          <p>
            Informed by common pavement condition evaluation practice (distress type × severity × extent), our scoring
            model computes a continuous 0–100 severity index:
          </p>
          <div className="p-3 bg-[var(--bg-surface-2)] rounded font-mono text-xs text-[var(--text-main)] border border-[var(--border-subtle)]">
            Severity = clamp(0, 100, BaseWeight × AreaMultiplier × PositionMultiplier + ClusterBonus + RiskFlags)
          </div>
          <ul className="list-disc pl-5 space-y-1 text-xs">
            <li><strong>Base Class Hazard:</strong> Potholes (48), Water-Filled Pothole (62), Alligator Cracks (40), Transverse (28), Longitudinal (22), Exposed Rebar (85), Spalling (58).</li>
            <li><strong>Position Multiplier:</strong> Wheel path (1.25x), Lane center (1.00x), Shoulder edge (0.85x).</li>
            <li><strong>Extents:</strong> Contiguous clusters add up to +20 points.</li>
          </ul>
        </div>
      </section>

      {/* Privacy & Ethical Considerations */}
      <section className="space-y-4">
        <h2 className="font-serif font-bold text-xl text-[var(--text-main)] flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-[var(--primary)]" />
          <span>Privacy & Data Protection (Section 10.6)</span>
        </h2>
        <p className="text-xs sm:text-sm text-[var(--text-muted)] leading-relaxed">
          Road and dashcam imagery inherently captures civilian faces and license plates. The system executes automated
          Gaussian redaction over detected human faces and vehicular registration markers before storage, strips EXIF and
          GPS coordinates unless explicitly opted in by the inspector, and supports complete data deletion.
        </p>
      </section>

      {/* Research Citations */}
      <section className="space-y-4 pt-4 border-t border-[var(--border-rule)]">
        <h2 className="font-serif font-bold text-xl text-[var(--text-main)] flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-[var(--primary)]" />
          <span>Verified Scientific Literature Citations</span>
        </h2>
        <div className="space-y-3 text-xs text-[var(--text-muted)]">
          <div className="p-3 rounded border border-[var(--border-subtle)] bg-[var(--bg-surface)]">
            <p className="font-semibold text-[var(--text-main)]">RDD2022 Multi-National Benchmark</p>
            <p className="italic">Arya et al., 2022. Crowdsensing-based Road Damage Detection: Challenge, Dataset, and Baseline. arXiv:2209.08538.</p>
          </div>
          <div className="p-3 rounded border border-[var(--border-subtle)] bg-[var(--bg-surface)]">
            <p className="font-semibold text-[var(--text-main)]">CODEBRIM Bridge Concrete Deterioration</p>
            <p className="italic">Mundt et al., 2019. Meta-learning for Concrete Defect Detection on Bridges. IEEE/CVF WACV 2019.</p>
          </div>
          <div className="p-3 rounded border border-[var(--border-subtle)] bg-[var(--bg-surface)]">
            <p className="font-semibold text-[var(--text-main)]">Weighted Boxes Fusion</p>
            <p className="italic">Romanenko et al., 2021. Weighted Boxes Fusion: ensembling methods for object detection. arXiv:1910.13302.</p>
          </div>
        </div>
      </section>

      {/* Academic AI Disclosure (Phase 13.5) */}
      <section className="p-4 rounded border border-[var(--border-subtle)] bg-[var(--bg-surface-2)] space-y-1.5 text-xs text-[var(--text-muted)]">
        <p className="font-semibold text-[var(--text-main)]">Academic Disclosure on AI-Assisted Development</p>
        <p>
          In accordance with institutional academic integrity guidelines, large language models (Claude, Gemini, Antigravity)
          were utilized as engineering aids for refactoring, test generation, and documentation drafting. All neural model
          architectures, training pipelines, evaluation datasets, and empirical numbers were independently authored,
          compiled, and verified from real experimental test sets.
        </p>
      </section>
    </div>
  );
};
