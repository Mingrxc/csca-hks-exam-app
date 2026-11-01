"""Reserve lw000 for the operator's verified account; preview by default.

This changes a display number only. It grants no administrator privileges.
"""
import argparse
import os
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]


def assign_owner_code(db, user_id: int, *, apply: bool = False) -> dict:
    from src.modules.user.models import User

    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        raise ValueError("User does not exist")
    owner = db.query(User).filter(User.user_code == "lw000").first()
    if owner and owner.id != user.id:
        raise ValueError("lw000 already belongs to another account; no change made")
    result = {"id": user.id, "nickname": user.nickname, "previous_code": user.user_code,
              "new_code": "lw000", "applied": apply}
    if apply:
        user.user_code = "lw000"
        db.commit()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", type=int, required=True, help="Verified internal users.id")
    parser.add_argument("--apply", action="store_true", help="Write only after verifying this is the owner's account")
    args = parser.parse_args()
    if args.user_id <= 0:
        parser.error("User ID must be positive")
    sys.path.insert(0, str(PROJECT / "server"))
    os.chdir(PROJECT / "server")
    from src.config.database import SessionLocal
    import json
    with SessionLocal() as db:
        try:
            print(json.dumps(assign_owner_code(db, args.user_id, apply=args.apply), ensure_ascii=False))
        except ValueError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    main()
