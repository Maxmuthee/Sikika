"""Alert registered citizens about a new project/bill in their sub-county.

Run:  python scripts/notify.py <project_id>
(Uses the SMS stub, which logs; wire Africa's Talking to send for real.)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.notify import notify_new_project

if __name__ == "__main__":
    pid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(json.dumps(notify_new_project(pid), indent=2))
