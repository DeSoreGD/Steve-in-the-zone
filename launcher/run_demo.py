"""Entry point inside the prepared demo's app directory."""
import sys
from pathlib import Path

base=(Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent).parent
sys.path.insert(0,str(base.parent/"python-deps"))
from demo_launcher import main

if __name__=="__main__":
    sys.argv=[sys.argv[0],"--config",str(base/"demo-launch.json"),*sys.argv[1:]]
    raise SystemExit(main())
