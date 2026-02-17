import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Keep tests deterministic
os.environ.pop("SUPER_AGENT_MAX_STEPS", None)
os.environ.pop("SUPER_AGENT_MODE_DEFAULT", None)
