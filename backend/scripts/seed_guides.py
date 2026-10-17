"""Command-line entry point for Task41 guide data."""

import argparse

from app.db import SessionLocal
from scripts.seed_data.guide_seed_service import GuideSeedService


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Task41 guide data")
    parser.add_argument("--dataset", choices=("test", "demo"), required=True)
    parser.add_argument("--action", choices=("seed", "check", "restore"), required=True)
    args = parser.parse_args()

    with SessionLocal.begin() as session:
        service = GuideSeedService(session, args.dataset)
        if args.action == "seed":
            service.seed()
            counts = service.verify()
        elif args.action == "check":
            counts = service.verify()
        else:
            counts = service.restore()
    label = "removed" if args.action == "restore" else "verified"
    print(f"{args.dataset} {args.action} ({label}): {counts}")


if __name__ == "__main__":
    main()
