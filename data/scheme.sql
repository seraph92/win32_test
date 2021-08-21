CREATE TABLE "inout_history" (
	"dtm"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	"temper"	TEXT,
	"dtm2"	TEXT,
	"reg_dtm"	TEXT NOT NULL,
	"send_dtm"	TEXT,
	"del_yn"	TEXT DEFAULT 'N',
	PRIMARY KEY("dtm")
);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE "user" (
	"no"	INTEGER NOT NULL,
	"user_name"	TEXT UNIQUE,
	"chat_room"	TEXT,
	"reg_dtm"	TEXT,
	PRIMARY KEY("no" AUTOINCREMENT)
);
