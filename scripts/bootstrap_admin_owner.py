"""Preview and explicitly bind the sole owner. --temporary preserves the test code."""
import argparse
import json
import os
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-code", required=True, help="Current public code of the verified owner")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--temporary", action="store_true", help="Test owner: keep the existing lw code and reserve lw000")
    parser.add_argument("--expected-user-id", type=int, help="Internal ID confirmed from the preview")
    args = parser.parse_args()
    if args.apply and not args.expected_user_id:
        parser.error("--apply requires --expected-user-id from the verified preview")
    sys.path.insert(0, str(PROJECT / "server"))
    os.chdir(PROJECT / "server")
    from src.config.database import SessionLocal
    from src.modules.admin.service import bootstrap_owner
    with SessionLocal() as db:
        try:
            result = bootstrap_owner(db, args.user_code, apply=args.apply, expected_user_id=args.expected_user_id,
                                     temporary=args.temporary)
        except ValueError as exc:
            parser.error(str(exc))
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
