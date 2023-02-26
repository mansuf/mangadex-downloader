/* 
Use unsanitized input on SQL query is dangerous.
But here's the thing, python `sqlite3.Cursor.executescript`
doesn't support parameters, so we cannot add variables to the query. 
Also `sqlite3.Cursor.execute` and `sqlite3.Cursor.executemany` 
only support single-line query, so we have no choice to use
`str.format_map` and the only input to the SQL query 
is just file format name (raw, cbz, etc)
*/
CREATE TABLE IF NOT EXISTS "file_info_{format}" (
	"name"	TEXT NOT NULL,
	"manga_id" TEXT NOT NULL,
	"ch_id"	TEXT,
	"hash"	TEXT,
	"last_download_time" TEXT,
	"completed"	INTEGER NOT NULL,
	PRIMARY KEY("name")
);