import subprocess
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "src/fetch_data.py",
    "src/fetch_hs_components.py",
    "src/build_dataset.py",
    "src/analyze_hs_components.py",
    "src/scenario_analysis.py",
    "src/supply_shock_simulation.py",
    "src/supplier_cost_model.py",
    "src/cluster_component_risk.py",
    "src/make_charts.py",
]

def run_script(script_path: str) -> None:
    print(f"\nRunning {script_path} ...")
    result = subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {script_path}")

def main() -> None:
    for script in SCRIPTS:
        run_script(script)
    print("\n Pipeline completed successfully.")

if __name__ == "__main__":
    main()