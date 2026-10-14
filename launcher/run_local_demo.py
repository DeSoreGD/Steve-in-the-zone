"""No-console entry point for the owner's prepared, playable local demo."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "runtime/python-deps"))
from demo_launcher import main

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--config", str(root / "runtime/local-demo/demo-launch.json")]
    raise SystemExit(main())
