/* 
Use unsanitized input on SQL query is dangerous.
But here's the thing, python `sqlite3.Cursor.executescript`
doesn't support parameters, so we cannot add variables to the query. 
Also `sqlite3.Cursor.execute` and `sqlite3.Cursor.executemany` 
only support single-line query, so we have no choice to use
`str.format_map` and the only input to the SQL query 
is just file format name (raw, cbz, etc)
*/
CREATE TABLE IF NOT EXISTS "img_info_{format}" (
	"name"	TEXT NOT NULL,
	"hash"	TEXT NOT NULL,
	"chapter_id"	TEXT NOT NULL,
	"fi_name"	TEXT NOT NULL,
	FOREIGN KEY("fi_name") REFERENCES "file_info_{format}"("name") ON DELETE CASCADE
);