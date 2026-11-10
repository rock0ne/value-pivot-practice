"""Give an AI agent a database connection that can read and can't change anything (answer key).

SQLite asks an "authorizer" before every action a statement takes. This one allows
reading and nothing else, so the agent can investigate, and any change it wants
has to come back to a person as a proposal.

    python agent_guard.py ../../project/agent/proposed_tidy.sql

Other databases do the same job with a read-only role or user (for example GRANT SELECT only).
"""

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent.parent / "project" / "clinic.db"

ALLOWED = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}


def read_only_authorizer(action, arg1, arg2, db_name, trigger):
    return sqlite3.SQLITE_OK if action in ALLOWED else sqlite3.SQLITE_DENY


def connect_for_agent(path=DB):
    conn = sqlite3.connect(path)
    conn.set_authorizer(read_only_authorizer)
    return conn


def try_sql(sql_text, path=DB):
    conn = connect_for_agent(path)
    try:
        conn.executescript(sql_text)
        return "ran"
    except sqlite3.DatabaseError as exc:
        return f"refused: {exc}"
    finally:
        conn.close()


if __name__ == "__main__":
    print(try_sql(Path(sys.argv[1]).read_text(encoding="utf-8")))
