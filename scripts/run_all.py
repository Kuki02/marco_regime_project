import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PARALLEL_SCRIPTS = [
    "scripts/fetch_yield_curve.py",
    "scripts/update_corporate_bonds.py",
    "scripts/fetch_fed_rates.py",
    "scripts/fetch_sp500.py",
]

SEQUENTIAL_SCRIPTS: list[str] = []


def run_script(path: str) -> tuple[str, int, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=env,
    )
    output = result.stdout + result.stderr
    return path, result.returncode, output


def main():
    print("=== Running parallel scripts ===")
    failed = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(run_script, s): s for s in PARALLEL_SCRIPTS}
        for future in as_completed(futures):
            path, code, output = future.result()
            name = Path(path).name
            status = "OK" if code == 0 else f"FAILED (exit {code})"
            print(f"\n[{name}] {status}")
            print(output.strip())
            if code != 0:
                failed.append(name)

    print("\n=== Running sequential scripts ===")
    for path in SEQUENTIAL_SCRIPTS:
        name = Path(path).name
        path_obj, code, output = run_script(path)
        status = "OK" if code == 0 else f"FAILED (exit {code})"
        print(f"\n[{name}] {status}")
        print(output.strip())
        if code != 0:
            failed.append(name)

    print("\n=== Done ===")
    if failed:
        print(f"Failed scripts: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All scripts completed successfully.")


if __name__ == "__main__":
    main()
