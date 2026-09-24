"""One-shot absolute deadline guard; never starts or resumes gameplay."""
import time
from datetime import datetime
from pathlib import Path
root=Path(__file__).resolve().parent
deadline=datetime.fromisoformat('2026-09-24T07:39:55-04:00').timestamp()
while time.time()<deadline:
 if (root/'stop').exists():raise SystemExit(0)
 time.sleep(min(5,deadline-time.time()))
(root/'stop').touch()
