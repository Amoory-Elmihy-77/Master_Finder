import json
import os
import sqlite3
from typing import List, Optional

from models.program import Program
from models.professor import Professor
from models.candidate import CandidateProfile


DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
)
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "masterfinder.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS favorite_programs (
            key TEXT PRIMARY KEY,
            data TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS favorite_professors (
            key TEXT PRIMARY KEY,
            data TEXT
        )
        """
    )

    conn.commit()
    conn.close()


# =====================================================
# Generic key/value state (candidate, programs,
# professors, chat messages)
# =====================================================

def _set_state(key: str, value) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO app_state (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, json.dumps(value)),
    )
    conn.commit()
    conn.close()


def _get_state(key: str):
    conn = get_connection()

    row = conn.execute(
        "SELECT value FROM app_state WHERE key = ?",
        (key,),
    ).fetchone()

    conn.close()

    if row is None:
        return None

    return json.loads(row[0])


def clear_all() -> None:
    conn = get_connection()
    conn.execute("DELETE FROM app_state")
    conn.execute("DELETE FROM favorite_programs")
    conn.execute("DELETE FROM favorite_professors")
    conn.commit()
    conn.close()


# ---------- candidate (from CV) ----------

def save_candidate(candidate: Optional[CandidateProfile]) -> None:
    _set_state(
        "candidate",
        candidate.model_dump() if candidate else None,
    )


def load_candidate() -> Optional[CandidateProfile]:
    data = _get_state("candidate")
    return CandidateProfile(**data) if data else None


# ---------- last program/professor search results ----------

def save_programs(programs: List[Program]) -> None:
    _set_state(
        "programs",
        [p.model_dump() for p in programs],
    )


def load_programs() -> List[Program]:
    data = _get_state("programs") or []
    return [Program(**p) for p in data]


def save_professors(professors: List[Professor]) -> None:
    _set_state(
        "professors",
        [p.model_dump() for p in professors],
    )


def load_professors() -> List[Professor]:
    data = _get_state("professors") or []
    return [Professor(**p) for p in data]


# ---------- chat history ----------

def save_messages(messages: List[dict]) -> None:
    _set_state("messages", messages)


def load_messages() -> List[dict]:
    return _get_state("messages") or []


# =====================================================
# Favorites (dedicated tables so add/remove is cheap)
# =====================================================

def add_favorite_program(key: str, program: Program) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO favorite_programs (key, data) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET data = excluded.data
        """,
        (key, program.model_dump_json()),
    )
    conn.commit()
    conn.close()


def remove_favorite_program(key: str) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM favorite_programs WHERE key = ?",
        (key,),
    )
    conn.commit()
    conn.close()


def load_favorite_programs() -> dict:
    conn = get_connection()

    rows = conn.execute(
        "SELECT key, data FROM favorite_programs"
    ).fetchall()

    conn.close()

    return {
        key: Program(**json.loads(data))
        for key, data in rows
    }


def add_favorite_professor(key: str, professor: Professor) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO favorite_professors (key, data) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET data = excluded.data
        """,
        (key, professor.model_dump_json()),
    )
    conn.commit()
    conn.close()


def remove_favorite_professor(key: str) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM favorite_professors WHERE key = ?",
        (key,),
    )
    conn.commit()
    conn.close()


def load_favorite_professors() -> dict:
    conn = get_connection()

    rows = conn.execute(
        "SELECT key, data FROM favorite_professors"
    ).fetchall()

    conn.close()

    return {
        key: Professor(**json.loads(data))
        for key, data in rows
    }
