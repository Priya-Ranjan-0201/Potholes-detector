"""ScamRoad AI Backend Server.

Runs FastAPI with CORS enabled on http://localhost:8000.
Serves real-time road defect detection (YOLO11n + YOLOv8n + COCO blocker)
and municipal maintenance / verification endpoints.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Threading optimizations for inference
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn


def main() -> None:
    port = int(os.environ.get("PORT", "8001"))
    host = os.environ.get("HOST", "127.0.0.1")

    print("=" * 60)
    print(f"  ScamRoad AI Backend Server starting on http://{host}:{port}")
    print(f"  Project Root: {PROJECT_ROOT}")
    print(f"  Docs:         http://localhost:{port}/api/v1/docs")
    print(f"  Health:       http://localhost:{port}/api/v1/health")
    print("=" * 60, flush=True)

    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
