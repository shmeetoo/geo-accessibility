from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def run_step(step_name, script_path):
    print(f"\n=== {step_name} ===")
    print(f"Running: {script_path}")

    result = subprocess.run(
        [sys.executable, "-m", script_path],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        print(f"\n❌ Step failed: {step_name}")
        sys.exit(result.returncode)

    print(f"✅ Completed: {step_name}")


def main():
    steps = [
        ("Run ingestion", "src.ingestion.run_ingestion"),
        ("Run proccessing", "src.processing.run_processing"),
        ("Load data to PostgreSQL", "src.db.run_load"),
        ("Create analytics table", "src.analytics.feature_engineering")
    ]

    for step_name, script_path in steps:
        run_step(step_name, script_path)

    print("\n🎉 Full pipeline completed successfully.")

if __name__ == "__main__":
    main()