import sqlite3
import logging
import glob
import re
from pathlib import Path

log = logging.getLogger(__name__)


def _get_migration_files():
    migration_files = {}
    files = glob.glob("*", root_dir=Path(__file__).parent.resolve())
    for file in files:
        result = re.match(r"(?P<migrate_id>[0-9]{1,}).{1,}\.py", file)
        if not result:
            continue

        migrate_id = int(result.group("migrate_id"))
        migration_files[migrate_id] = file

    return migration_files


# Format:
# {migrate_id: migration_file.py}
migration_files = _get_migration_files()


class SQLMigration:
    """Base class for SQL Migration"""

    # Base checking before migrations
    # subclasses must implement this
    migrate_tables = []
    new_version = None
    file = None

    # Format:
    # {table_name: [column_name1, column_name2, ...]}
    migrate_columns = {}

    # Format:
    # {table_name: [column_name, column_data_type]}
    # This to make sure that column value is not null
    migrate_values = {}

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def check_if_migrate_is_possible(self) -> bool:
        return True

    def migrate(self):
        """Subclasses must implement this"""
        raise NotImplementedError

    def get_format(self):
        from ...config import config

        return config.save_as.replace("-", "_")

    def get_current_version(self):
        cursor = self.db.cursor()

        try:
            cursor.execute(
                "SELECT version FROM db_info WHERE app_name = 'mangadex-downloader'"
            )
        except sqlite3.OperationalError:
            return 0

        version = cursor.fetchone()
        cursor.close()

        return version

    def get_missing_tables(self):
        missing_tables = []
        cursor = self.db.cursor()

        for table in self.migrate_tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
            except sqlite3.OperationalError:
                missing_tables.append(table)

        cursor.close()
        return missing_tables

    def get_missing_columns(self):
        missing_columns = []
        cursor = self.db.cursor()

        for table, columns in self.migrate_columns.items():
            cursor.execute(f"PRAGMA table_info('{table}')")

            column_names = [i[1] for i in cursor.fetchall()]

            for column in columns:
                if column not in column_names:
                    missing_columns.append(column)

        cursor.close()
        return missing_columns

    def get_missing_values(self):
        """Ensure that the values are not null

        Return: Tuple[str, str, Any]
        Note: data type "Any" depends on what "column_data_type" is
        """
        missing_values = []
        cursor = self.db.cursor()

        for table, (column_name, column_data_type) in self.migrate_values.items():
            try:
                cursor.execute(f"SELECT {column_name} FROM {table}")
            except sqlite3.OperationalError:
                # No such column
                missing_values.append((table, column_name, column_data_type))

            data = cursor.fetchall()
            for value in data:
                if not isinstance(value[0], column_data_type):
                    missing_values.append((table, column_name, column_data_type))

        cursor.close()
        return missing_values
