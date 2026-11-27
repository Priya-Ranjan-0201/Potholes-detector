# ScamRoad — Human Actions & Decision Queue

The development process tracks items in this file that strictly require human authorization or physical hardware access. All code, evaluation, and documentation proceed systematically.

---

| Item ID | Category | Description | Status | Added Date |
| :--- | :--- | :--- | :--- | :--- |
| `H-001` | Data / Labelling | Collect and label targeted local Indian road corridor test videos (e.g. Ludhiana / Punjab road sequences) for spatial deduplication ground truth. | PENDING | 2026-11-07 |
| `H-002` | Hardware | Run real physical on-device inference latency benchmarks on target devices (OPPO K13, Raspberry Pi 5, NVIDIA Jetson Orin) and provide raw `bench/*.json` outputs. | PENDING | 2026-11-07 |
| `H-003` | Secrets / Cloud | Provide cloud GPU production credentials or API tokens if cloud training outside Colab/Kaggle free tier is requested. | OPTIONAL | 2026-11-07 |
| `H-004` | Field Drive / IMU | Record smartphone accelerometer/gyroscope drive data over real potholes to empirically validate bump detection threshold (pipeline implemented in `edge/agent/sensor_fusion.py`). | PENDING | 2026-11-07 |
| `H-005` | Rater Study | Distribute `bench/rater_study_template.csv` to 3–5 classmates/engineers to rate defect severity and compute real inter-annotator Kappa agreement via `scripts/rater_study_kit.py`. | PENDING | 2026-11-07 |
| `H-006` | Gate F / Pilot | Coordinate corridor safety clearance and route mapping for 25.0 km pilot stretch on NH-44 (Hebbal km 10 to Devanahalli km 35). | PENDING | 2026-11-27 |
| `H-007` | Gate F / Hardware | Mount and lock dashcam/smartphone windshield rig at calibrated depression angle (15° downward pitch, 0° roll) in survey vehicle. | PENDING | 2026-11-27 |
| `H-008` | Gate F / Survey Run | Execute 2 consecutive survey drives (Pass A morning, Pass B afternoon, same calendar date) over the 25.0 km corridor at 45–65 km/h. | PENDING | 2026-11-27 |
| `H-009` | Gate F / Ground Truth | Accompany junior civil engineer walking survey team to log physical pothole dimensions, chainage, and RTK-GNSS coordinates into the validation template. | PENDING | 2026-11-27 |
| `H-010` | Gate F / Data Ingest | Upload raw survey video MP4s and synchronized GPS logs to `data/pilot_run_nh44/` for automated pipeline scoring and repeat-pass consistency audit. | PENDING | 2026-11-27 |
