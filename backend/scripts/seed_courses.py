"""Command-line entry point for Task26 course seed data."""

import argparse

from app.db import SessionLocal, engine
from app.models.course_seed_ownership import CourseSeedOwnership
from scripts.seed_data.course_seed_service import CourseSeedService


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Task26 course seed data")
    parser.add_argument("--dataset", choices=("test", "demo"), required=True)
    parser.add_argument("--action", choices=("seed", "check", "restore"), required=True)
    args = parser.parse_args()
    if args.action == "seed":
        with engine.begin() as connection:
            CourseSeedOwnership.__table__.create(connection, checkfirst=True)
    with SessionLocal() as session, session.begin():
        service = CourseSeedService(session, args.dataset)
        report = service.seed() if args.action == "seed" else (
            service.verify() if args.action == "check" else service.restore()
        )
    print(f"{args.dataset} {args.action}: {report}")


if __name__ == "__main__":
    main()
