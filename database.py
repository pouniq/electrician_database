import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "electrician.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS "customers" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"phone"	TEXT NOT NULL,
	"address"	TEXT NOT NULL,
	"notes"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "jobs" (
	"id"	INTEGER,
	"customer_id"	INTEGER NOT NULL,
	"job_title"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"status"	TEXT NOT NULL DEFAULT 'Quoted',
	"job_date"	TEXT NOT NULL,
	"address"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	"labor_pay"	INTEGER NOT NULL,
	FOREIGN KEY("customer_id") REFERENCES "customers"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "material_job" (
	"id"	INTEGER NOT NULL,
	"customer_id"	INTEGER NOT NULL,
	"materials_id"	INTEGER NOT NULL,
	"job_id"	INTEGER NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"price_at_time"	INTEGER NOT NULL,
	FOREIGN KEY("customer_id") REFERENCES "customers"("id"),
	FOREIGN KEY("materials_id") REFERENCES "materials"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "materials" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"quantity"	INTEGER NOT NULL DEFAULT 1,
	"unit_cost"	NUMERIC NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "payments" (
	"id"	INTEGER,
	"customer_id"	INTEGER NOT NULL,
	"job_id"	INTEGER NOT NULL,
	"amount"	REAL NOT NULL,
	"issue_date"	TEXT,
	"due_date"	TEXT,
	"paid"	INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY("customer_id") REFERENCES "customers"("id"),
	FOREIGN KEY("job_id") REFERENCES "jobs"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);


"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")
