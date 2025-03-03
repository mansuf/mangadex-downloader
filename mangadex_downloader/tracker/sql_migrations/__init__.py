import importlib
import sqlite3
import logging
from .base import migration_files

log = logging.getLogger(__name__)


def _iter_migrate_cls(db: sqlite3.Connection):
    for _, file in sorted(migration_files.items()):

        migrate_lib = importlib.import_module(
            "." + file.replace(".py", ""), "mangadex_downloader.tracker.sql_migrations"
        )
        yield migrate_lib.Migration(db), file


def check_if_there_is_migrations(db):
    possible_migrations = []
    for migrate_cls, _ in _iter_migrate_cls(db):
        check = migrate_cls.check_if_migrate_is_possible()
        possible_migrations.append(check)

    return any(possible_migrations)


def migrate(db: sqlite3.Connection):
    for migrate_cls, file in _iter_migrate_cls(db):
        if not migrate_cls.check_if_migrate_is_possible():
            continue

        log.debug(f"Applying download tracker database migration {file}...")
        migrate_cls.migrate()
