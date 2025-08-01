#!/usr/bin/env python3
"""
Migration management script for the FastAPI MVC application.
This script provides commands to manage database migrations using Alembic.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to make imports work
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

def get_alembic_config():
    """Return the Alembic configuration object."""
    alembic_config = Config(os.path.join(Path(__file__).parent.parent, "alembic.ini"))
    return alembic_config

def create_migration(message=None):
    """Create a new migration revision."""
    alembic_config = get_alembic_config()
    if message:
        command.revision(alembic_config, message=message, autogenerate=True)
    else:
        command.revision(alembic_config, autogenerate=True)
    logger.info("Migration revision created successfully.")

def upgrade_db(revision="head"):
    """Upgrade the database to the specified revision."""
    alembic_config = get_alembic_config()
    command.upgrade(alembic_config, revision)
    logger.info(f"Database upgraded to revision: {revision}")

def downgrade_db(revision="-1"):
    """Downgrade the database to the specified revision."""
    alembic_config = get_alembic_config()
    command.downgrade(alembic_config, revision)
    logger.info(f"Database downgraded to revision: {revision}")

def show_history():
    """Show the migration history."""
    alembic_config = get_alembic_config()
    command.history(alembic_config)

def show_current():
    """Show the current migration revision."""
    alembic_config = get_alembic_config()
    command.current(alembic_config)

def main():
    """Main function to parse command-line arguments and execute commands."""
    parser = argparse.ArgumentParser(description="Migration management for FastAPI MVC application")
    subparsers = parser.add_subparsers(dest="command", help="Migration command")

    # create command
    create_parser = subparsers.add_parser("create", help="Create a new migration revision")
    create_parser.add_argument("--message", "-m", help="Migration message")

    # upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade the database")
    upgrade_parser.add_argument("--revision", "-r", default="head", help="Target revision (default: head)")

    # downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade the database")
    downgrade_parser.add_argument("--revision", "-r", default="-1", help="Target revision (default: -1)")

    # history command
    subparsers.add_parser("history", help="Show migration history")

    # current command
    subparsers.add_parser("current", help="Show current migration version")

    args = parser.parse_args()

    if args.command == "create":
        create_migration(args.message)
    elif args.command == "upgrade":
        upgrade_db(args.revision)
    elif args.command == "downgrade":
        downgrade_db(args.revision)
    elif args.command == "history":
        show_history()
    elif args.command == "current":
        show_current()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
