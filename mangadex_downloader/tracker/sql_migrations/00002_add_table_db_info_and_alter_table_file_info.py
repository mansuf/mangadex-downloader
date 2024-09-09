import logging
import sqlite3
from .base import (
    SQLMigration,
)
from ...manga import Manga
from ... import __version__

log = logging.getLogger(__name__)


class Migration(SQLMigration):
    new_version = 1
    file = __file__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # I cannot read config values from class attributes
        # that would trigger recursive import error
        fmt = self.get_format()
        self.migrate_columns[f"file_info_{fmt}"] = ["volume"]
        self.migrate_values[f"file_info_{fmt}"] = ["volume", int]

        self.migrate_tables = ["db_info"]

    # Return:
    # {file_name: volume_manga}
    def _get_values_for_volume_column(self):
        from ...config import config

        # File info cursor
        fi_cursor = self.db.cursor()
        fi_cursor.execute(f"SELECT * FROM file_info_{self.get_format()}")

        values = {}
        for fi_data in fi_cursor.fetchall():
            manga_id = fi_data[1]
            fi_name = fi_data[0]
            manga = Manga(_id=manga_id)
            manga.fetch_chapters(lang=config.language, all_chapters=True)

            chapter_iterator = manga.chapters.iter()
            volumes = {}
            for chapter, images in chapter_iterator:
                try:
                    volumes[chapter.volume]
                except KeyError:
                    volumes[chapter.volume] = [(chapter, images)]
                else:
                    volumes[chapter.volume].append((chapter, images))

            for volume, chapters in volumes.items():

                ch_info_cursor = self.db.cursor()
                ch_info_cursor.execute(
                    f"SELECT id, fi_name FROM ch_info_{self.get_format()} WHERE fi_name = ?",
                    (fi_name,),
                )
                ch_info_data = ch_info_cursor.fetchall()
                chapter_ids = [i[0] for i in ch_info_data]

                if not ch_info_data:
                    continue

                # Get: file name
                ch_info_fi_name_ref = ch_info_data[0][1]

                if not any([i.id in chapter_ids for i, _ in chapters]):
                    continue

                values[ch_info_fi_name_ref] = volume
                ch_info_cursor.close()

        fi_cursor.close()
        return values

    def _update_volume_values(self, cursor, values):
        for filename, volume in values.items():
            cursor.execute(
                f"UPDATE file_info_{self.get_format()} SET volume = ? WHERE name = ?",
                (volume, filename),
            )
            self.db.commit()

    def _is_version_missing(self, cursor):
        # Ensure the db_version is exist in db_info table
        try:
            cursor.execute(
                "SELECT db_version FROM db_info WHERE app_name = 'mangadex-downloader'"
            )
        except sqlite3.OperationalError:
            # This only evaluated to boolean
            missing_version = True
        else:
            missing_version = False

        return missing_version

    def check_if_migrate_is_possible(self) -> bool:
        cursor = self.db.cursor()
        missing_tables = self.get_missing_tables()
        missing_columns = self.get_missing_columns()
        missing_version = self._is_version_missing(cursor)

        cursor.close()

        return any([missing_columns, missing_tables, missing_version])

    def migrate(self):
        cursor = self.db.cursor()
        missing_tables = self.get_missing_tables()
        missing_columns = self.get_missing_columns()
        missing_values = self.get_missing_values()
        missing_version = self._is_version_missing(cursor)
        volume_values = self._get_values_for_volume_column()

        # Migrate tables first
        if missing_tables:
            cursor.execute(
                'CREATE TABLE "db_info" ("app_name"	TEXT,"app_version" TEXT, "db_version" INTEGER);'
            )
            self.db.commit()

        if missing_version:
            cursor.execute(
                'INSERT INTO db_info ("app_name", "app_version", "db_version") VALUES (?,?,?)',
                ("mangadex-downloader", __version__, self.new_version),
            )
            self.db.commit()

        # Then migrate the columns
        if missing_columns:
            cursor.execute(
                f"ALTER TABLE file_info_{self.get_format()} ADD COLUMN volume INTEGER;"
            )
            self.db.commit()

            self._update_volume_values(cursor, volume_values)

        # Ensure that the values are not null
        for table, column_name, column_data_type in missing_values:
            cursor.execute(f"SELECT {column_name} FROM {table}")

            values = cursor.fetchall()
            # Verify it
            if any([not isinstance(i, column_data_type) for i in values]):
                self._update_volume_values(cursor, volume_values)

        if self.db.in_transaction:
            self.db.commit()

        cursor.close()
