import logging
import sqlite3
from pathlib import Path
from .base import SQLMigration

log = logging.getLogger(__name__)


class Migration(SQLMigration):
    file = __file__

    def check_if_migrate_is_possible(self) -> bool:
        cursor = self.db.cursor()
        fmt = self.get_format()

        missing_ch_info = False
        try:
            cursor.execute(f"SELECT * FROM ch_info_{fmt}")
        except sqlite3.OperationalError:
            missing_ch_info = True

        missing_file_info = False
        try:
            cursor.execute(f"SELECT * FROM file_info_{fmt}")
        except sqlite3.OperationalError:
            missing_file_info = True

        missing_img_info = False
        try:
            cursor.execute(f"SELECT * FROM img_info_{fmt}")
        except sqlite3.OperationalError:
            missing_img_info = True

        return any([missing_img_info, missing_ch_info, missing_file_info])

    def migrate(self):

        sqlfiles_base_path = Path(__file__).parent.parent.resolve()
        sql_commands = {
            i: (sqlfiles_base_path / "sql_files" / f"{i}.sql").read_text()
            for i in ["create_file_info", "create_ch_info", "create_img_info"]
        }
        cursor = self.db.cursor()

        for cmd_name, cmd_script in sql_commands.items():
            cmd_script = cmd_script.format_map({"format": self.get_format()})

            cursor.execute(cmd_script)

        if self.db.in_transaction:
            self.db.commit()

        cursor.close()
