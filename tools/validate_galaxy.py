"""Run the bundled Galaxy syntax parser with Node or VS Code's Node runtime."""

from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def javascript_runtime():
    environment = os.environ.copy()
    node = shutil.which("node")
    if node:
        return node, environment
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Microsoft VS Code/Code.exe",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Microsoft VS Code/Code.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            environment["ELECTRON_RUN_AS_NODE"] = "1"
            return str(candidate), environment
    raise RuntimeError("Galaxy syntax checking needs Node.js or an installed VS Code. The saved map can still be opened normally.")


def validate(*paths, self_test=False):
    runtime, environment = javascript_runtime()
    arguments = [runtime, str(ROOT / "tools/check_galaxy.cjs")]
    arguments += ["--self-test"] if self_test else [str(Path(p).resolve()) for p in paths]
    result = subprocess.run(arguments, env=environment, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or "Galaxy syntax check failed.")
    return result.stdout.strip()


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["--self-test"]:
            print(validate(self_test=True))
        else:
            paths = sys.argv[1:] or [ROOT / "src/Arena.galaxy", ROOT / "src/InstantArena_Basic.SC2Map/MapScript.galaxy"]
            print(validate(*paths))
    except (RuntimeError, ValueError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
