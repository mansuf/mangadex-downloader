import sqlite3
import logging
import threading
from pathlib import Path
from typing import Union
from datetime import datetime

from .info_data.sqlite import FileInfo
from ..utils import delete_file
from ..config import config

log = logging.getLogger(__name__)

# Since download tracker is working on another thread (QueueWorker)
# We need to tell sqlite3 that we're working on serialized mode
# See https://docs.python.org/3/library/sqlite3.html#sqlite3.threadsafety
sqlite3.threadsafety = 3

sqlfiles_base_path = Path(__file__).parent.resolve()

sql_commands = {
    i: (sqlfiles_base_path / "sql_files" / f"{i}.sql").read_text()
    for i in 
    [
        "create_file_info",
        "create_ch_info",
        "create_img_info"
    ]
}

class DownloadTrackerSQLite:
    """An tracker for downloaded manga, data is written to SQLite format
    
    This will track downloaded volume and chapters from a manga. 
    The tracker will be put in downloaded manga directory, named `download.db`. 
    Inside the database contain these tables:

    - img_info_{format}
    - ch_info_{format}
    - file_info_{format}

    """

    def __init__(self, fmt, path):
        self.path = Path(path)
        self.format = fmt
        self.file = self.get_tracker_path(fmt, path)

        # Somehow i don't trust sqlite3 thread-safety
        # Sometimes it raised "sqlite3.OperationalError: cannot start a transaction within a transaction"
        # out of nowhere, and when i'm trying to run it again, it works without error.
        self._lock = threading.Lock()

        self.db = None

        self._kwargs_sqlite_con = {
            "database": self.file,
            "check_same_thread": False,
        }

        locked = self._check_db_locked()
        if locked:
            self._kwargs_sqlite_con["uri"] = True
            self._kwargs_sqlite_con["database"] = self.file.as_uri() + "?nolock=1"

        if not config.no_track:
            self.db = sqlite3.connect(**self._kwargs_sqlite_con)

        self._cache = {}
        self._load()

        # Table names for SQL query
        # Because sqlite3.Cursor.exceute() parameters doesn't support 
        # putting values into tables
        fmt_table = self.format.replace("-", "_")
        self._fi_name = f"file_info_{fmt_table}"
        self._img_name = f"img_info_{fmt_table}"
        self._ch_name = f"ch_info_{fmt_table}"

    def _check_db_locked(self):
        # https://github.com/mansuf/mangadex-downloader/issues/52
        db = sqlite3.connect(**self._kwargs_sqlite_con)
        with self._lock:
            try:
                db.execute("CREATE TABLE IF NOT EXISTS 'test' ('test' TEXT NOT NULL)")
                db.execute("INSERT INTO 'test' ('test') VALUES ('123')")
                db.commit()
                db.execute("DROP TABLE 'test'")
                db.commit()
                db.close()
            except sqlite3.OperationalError as e:
                msg = str(e)
                if "database is locked" in msg:
                    return True
            finally:
                db.close()
            
            return False

    def recreate(self):
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()

            cur.execute(f"DROP TABLE IF EXISTS '{self._fi_name}'")
            cur.execute(f"DROP TABLE IF EXISTS '{self._img_name}'")
            cur.execute(f"DROP TABLE IF EXISTS '{self._ch_name}'")

            self.db.commit()
            cur.close()

        self._load()

    @property
    def disabled(self):
        return config.no_track

    @classmethod
    def get_tracker_path(self, fmt, path) -> Path:
        return path / "download.db"

    @property
    def empty(self):
        with self._lock:
            cur = self.db.cursor()

            cur.execute(f"SELECT * FROM '{self._fi_name}'")
            empty = len(cur.fetchall()) == 0

            cur.close()

            return empty

    # I really want to rename this to `get_file_info`
    # but for compatibility reason, i won't
    def get(self, name) -> Union[FileInfo, None]:
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()
            cur.execute(f"SELECT * FROM '{self._fi_name}' WHERE name = ?", (name,))

            # Get file info data
            fi_data = cur.fetchone()

            if fi_data is None:
                return None

            # Get images info data
            im_data = []
            cur.execute(f"SELECT * FROM '{self._img_name}' WHERE fi_name = ?", (name,))
            for data in cur.fetchall():
                im_data.append(data)

            # Get chapters info data
            ch_data = []
            cur.execute(f"SELECT * FROM '{self._ch_name}' WHERE fi_name = ?", (name,))
            for data in cur.fetchall():
                ch_data.append(data)

            cur.close()

            fi_cls_args = list(fi_data)
            fi_cls_args.append(im_data)
            fi_cls_args.append(ch_data)

            return FileInfo(*fi_cls_args)

    def remove_file_info_from_name(self, name):
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()

            cur.execute(
                f"DELETE FROM '{self._fi_name}' WHERE name = ?", (name,)
            )

            self.db.commit()
            cur.close()

    def remove_duplicate_chapter_info(self, chapters):
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()

            cur.executemany(
                f"DELETE FROM '{self._ch_name}' WHERE fi_name = ? AND name = ?",
                [(i[2], i[0]) for i in chapters]
            )

            self.db.commit()
            cur.close()

    def remove_duplicate_image_info(self, images):
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()

            cur.executemany(
                f"DELETE FROM '{self._img_name}' WHERE fi_name = ? AND name = ?",
                [(im[3], im[0]) for im in images]
            )

            self.db.commit()
            cur.close()

    def add_file_info(
        self,
        name,
        manga_id=None,
        ch_id=None,
        hash=None,
    ):
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()

            query = f"INSERT INTO '{self._fi_name}' (" \
                    f"'name', " \
                    f"'manga_id', " \
                    f"'ch_id', " \
                    f"'hash', " \
                    f"'last_download_time', " \
                    f"'completed') VALUES (?,?,?,?,?,?)"
            
            cur.execute(query, (
                name,
                manga_id,
                ch_id,
                hash,
                None,
                0
            ))

            self.db.commit()
            cur.close()

    def add_images_info(self, images):
        if config.no_track:
            return

        # Remove duplicates
        self.remove_duplicate_image_info(images)

        with self._lock:
            cur = self.db.cursor()

            query = f"INSERT INTO '{self._img_name}' (" \
                    "'name', " \
                    "'hash', " \
                    "'chapter_id', " \
                    "'fi_name') VALUES (?,?,?,?) " \

            cur.executemany(query, images)

            self.db.commit()
        cur.close()

    def add_chapters_info(self, chapters):
        if config.no_track:
            return

        # Remove duplicates
        self.remove_duplicate_chapter_info(chapters)

        with self._lock:
            cur = self.db.cursor()

            query = f"INSERT INTO '{self._ch_name}' (" \
                    "'name', " \
                    "'id', " \
                    "'fi_name') VALUES (?,?,?) " \

            cur.executemany(query, chapters)

            self.db.commit()
            cur.close()

    def toggle_complete(self, fi_name, is_complete):
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()
            complete_val = 1 if is_complete else 0
            dt_finished = None

            if is_complete:
                dt_finished = datetime.now().isoformat()
            
            query = f"UPDATE '{self._fi_name}' SET " \
                    "completed = ?, " \
                    "last_download_time = ? " \
                    "WHERE name = ?"

            cur.execute(query, (complete_val, dt_finished, fi_name))

            self.db.commit()
            cur.close()

    def _load(self):
        if config.no_track:
            return

        with self._lock:
            cur = self.db.cursor()
            # Execute CREATE statements

            for cmd_name, cmd_script in sql_commands.items():
                log.debug(f"Executing SQL {cmd_name}")

                cmd_script = cmd_script.format_map(
                    {"format": self.format.replace("-", "_")}
                )

                cur.execute(cmd_script)

            if self.db.in_transaction:
                self.db.commit()