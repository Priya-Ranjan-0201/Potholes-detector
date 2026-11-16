# ScamRoad Documentation Index

This directory contains engineering documentation, audit records, evaluation metrics, and provenance registers for ScamRoad.

---

## Core Reports & Registers

| Document | Description |
| :--- | :--- |
| [`FORENSICS.md`](FORENSICS.md) | Forensic diagnosis of failure cases on new photos and videos (Phase 1). |
| [`AI_EVALUATION.md`](AI_EVALUATION.md) | Reproducible held-out benchmark report (1,728 images, 20 videos) across classes and slices (Phase 3). |
| [`CLEANUP_LOG.md`](CLEANUP_LOG.md) | Audit trail of pruned legacy weights, unreferenced scripts, and storage optimization (Phase 6). |
| [`MODELS_AND_DATA.md`](MODELS_AND_DATA.md) | Provenance register, cryptographic SHA-256 hashes, training lineage, and licenses for all models and datasets. |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System architecture, component boundaries, and video tracking data flow. |
| [`DECISIONS.md`](DECISIONS.md) | Architectural and algorithmic decision log across project phases. |
| [`HUMAN_TODO.md`](HUMAN_TODO.md) | Queue of operational tasks requiring human intervention (deployment secrets, field drives). |
| [`LIMITATIONS.md`](LIMITATIONS.md) | Engineering limitations, error profiles, and environmental boundaries. |
| [`API.md`](API.md) | REST API endpoint documentation and schema definitions. |
| [`CHANGELOG.md`](CHANGELOG.md) | Release and milestone history. |

---

## Research Integrity Statement

ScamRoad is an open-source undergraduate capstone project. Every metric reported across documentation originates from reproducible test evaluation runs or database transactions. No synthetic or smoothed data is used in benchmarking or documentation.
