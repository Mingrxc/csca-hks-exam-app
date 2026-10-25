"""Read/export private feedback on the server; mark status only when requested.

Run with the existing backend environment and server configuration. Access to
this script requires access to the server and its database credentials.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", choices=("unread", "read", "resolved"))
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=50, choices=range(1, 101), metavar="1..100")
    parser.add_argument("--output", type=Path, help="Optional JSON export path")
    parser.add_argument("--mark", type=int, metavar="ID", help="Explicitly update one feedback status")
    parser.add_argument("--to", choices=("unread", "read", "resolved"))
    args = parser.parse_args()
    if args.page < 1 or (args.mark is not None and args.mark < 1):
        parser.error("Page and feedback ID must be positive")
    if (args.mark is None) != (args.to is None):
        parser.error("Use --mark ID together with --to STATUS")
    output = args.output.resolve() if args.output else None
    sys.path.insert(0, str(PROJECT / "server"))
    os.chdir(PROJECT / "server")
    from src.config.database import SessionLocal
    from src.modules.feedback.service import list_feedback, update_feedback_status

    with SessionLocal() as db:
        if args.mark is not None:
            result = update_feedback_status(db, args.mark, args.to)
        else:
            result = list_feedback(db, status=args.status, page=args.page, page_size=args.page_size)
    encoded = json.dumps(result, ensure_ascii=False, indent=2, default=lambda value: value.isoformat()) + "\n"
    if output:
        output.write_text(encoded, encoding="utf-8")
        print("Feedback exported to the requested path.")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
