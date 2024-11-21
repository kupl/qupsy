import argparse
from pathlib import Path

from qupsy.spec import parse_spec
from qupsy.utils import logger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dry-run", action="store_true", help="Dry run")
    parser.add_argument(
        "specification", type=Path, metavar="SPEC", help="Specification file"
    )

    args = parser.parse_args()

    logger.debug("Specification file: %s", args.specification)
    spec = parse_spec(args.specification)

    logger.info("Specification loaded: %s", args.specification)
    logger.debug("Specification:\n%s", spec)

    if args.dry_run:
        return

    print("Hello, qupsy!")
