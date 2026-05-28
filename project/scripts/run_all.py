"""
Run the full analysis pipeline.

사용법:
    python scripts/run_all.py

또는 개별 단계만:
    python scripts/01_prepare_data.py
    python scripts/02_construct_fc.py
    python scripts/03_graph_metrics.py
    python scripts/04_glm_analyses.py
    python scripts/05_fdr_correction.py
    python scripts/06_mediation.py
    python scripts/07_make_figures.py
    
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
STEPS = [
    "01_prepare_data.py",
    "02_construct_fc.py",
    "03_graph_metrics.py",
    "04_glm_analyses.py",
    "05_fdr_correction.py",
    "06_mediation.py",
    "07_make_figures.py",
    
]


def main():
    for s in STEPS:
        path = SCRIPTS_DIR / s
        print(f"\n{'#' * 72}")
        print(f"# Running {s}")
        print(f"{'#' * 72}")
        result = subprocess.run([sys.executable, str(path)])
        if result.returncode != 0:
            print(f"\n[ERROR] {s} 실패 (exit code {result.returncode})")
            print(f"        이후 단계를 진행하려면 해당 단계의 입력 파일을 확인하세요.")
            return result.returncode
    print("\n=== 전체 pipeline 완료 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
