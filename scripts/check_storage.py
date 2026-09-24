from pathlib import Path

MAX_BYTES = 10 * 1024**3
ROOT = Path(__file__).resolve().parents[1]

skip = {".git", ".venv"}
total = 0
for path in ROOT.rglob("*"):
    if any(part in skip for part in path.parts) or not path.is_file():
        continue
    total += path.stat().st_size
print(f"Repository/runtime footprint: {total / 1024**3:.3f} GiB")
if total > MAX_BYTES:
    raise SystemExit("Storage budget exceeded: >10 GiB")
