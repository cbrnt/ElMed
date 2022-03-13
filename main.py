from loguru import logger
from lib.migration import StateFile
from lib.migration import build_migration
import argparse


def main():
    parser = argparse.ArgumentParser(description="Running migration process. Use --data parameter to point state file")
    parser.add_argument("--data", dest="path", required=False, help='point a JSON file with migration parameters')
    args = parser.parse_args()

    if args.path:
        state_file = StateFile(args.path)
        data = state_file.read()
        migration = build_migration(data)
        if migration.migration_state != 'running':
            migration.run()
        else:
            logger.warning("Migration is already in progress! Can't start another one")


if __name__ == '__main__':
    main()
