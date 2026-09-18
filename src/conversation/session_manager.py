"""SQLite-backed Session Manager for conversational intelligence and profile memory."""

import sqlite3
import json
import uuid
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from src.input_layer.schemas import EnvironmentalState
from src.conversation.models import ConversationTurn, SessionProfile


class SessionManager:
    """Manages conversational session persistence, turn tracking, and non-destructive profile merging."""

    def __init__(self, db_path: Optional[Path] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.db_path = db_path or (base_dir / "data" / "sessions.db")
        if self.db_path != Path(":memory:"):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS turns (
                    turn_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    turn_index INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    role TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    extracted_state TEXT,
                    response TEXT NOT NULL,
                    clarification_required INTEGER NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    session_id TEXT PRIMARY KEY,
                    cumulative_state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

    def create_session(self, session_id: Optional[str] = None) -> SessionProfile:
        """Creates a new session record and initialized empty profile."""
        sid = session_id or str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
                (sid, now, now)
            )
            empty_state = EnvironmentalState()
            cursor.execute(
                "INSERT OR REPLACE INTO profiles (session_id, cumulative_state_json, updated_at) VALUES (?, ?, ?)",
                (sid, json.dumps(empty_state.model_dump()), now)
            )
            conn.commit()

        return SessionProfile(
            session_id=sid,
            created_at=now,
            updated_at=now,
            cumulative_state=empty_state,
            turn_count=0,
            history=[],
        )

    def get_session(self, session_id: str) -> Optional[SessionProfile]:
        """Loads an existing session with cumulative state and history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            s_row = cursor.fetchone()
            if not s_row:
                return None

            cursor.execute("SELECT * FROM profiles WHERE session_id = ?", (session_id,))
            p_row = cursor.fetchone()
            cum_state = EnvironmentalState()
            if p_row and p_row["cumulative_state_json"]:
                cum_state = EnvironmentalState(**json.loads(p_row["cumulative_state_json"]))

            cursor.execute(
                "SELECT * FROM turns WHERE session_id = ? ORDER BY turn_index ASC",
                (session_id,)
            )
            t_rows = cursor.fetchall()

            history = [
                ConversationTurn(
                    turn_id=t["turn_id"],
                    session_id=t["session_id"],
                    timestamp=t["timestamp"],
                    role=t["role"],
                    input_text=t["input_text"],
                    extracted_environmental_state=json.loads(t["extracted_state"]) if t["extracted_state"] else None,
                    response=json.loads(t["response"]),
                    clarification_required=bool(t["clarification_required"]),
                )
                for t in t_rows
            ]

            return SessionProfile(
                session_id=s_row["session_id"],
                created_at=s_row["created_at"],
                updated_at=s_row["updated_at"],
                cumulative_state=cum_state,
                turn_count=len(history),
                history=history,
            )

    def update_profile(self, session_id: str, new_extracted_state: EnvironmentalState) -> SessionProfile:
        """Loads session, merges newly extracted variables non-destructively, and persists to DB."""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)

        # Merge new state into cumulative profile
        merged_state = session.merge_state(new_extracted_state)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE profiles SET cumulative_state_json = ?, updated_at = ? WHERE session_id = ?",
                (json.dumps(merged_state.model_dump()), now, session_id)
            )
            cursor.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (now, session_id)
            )
            conn.commit()

        session.updated_at = now
        return session

    def store_turn(self, turn: ConversationTurn) -> None:
        """Persists an executed conversation turn."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM turns WHERE session_id = ?", (turn.session_id,))
            idx = cursor.fetchone()["count"]

            cursor.execute("""
                INSERT INTO turns (
                    turn_id, session_id, turn_index, timestamp, role,
                    input_text, extracted_state, response, clarification_required
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                turn.turn_id,
                turn.session_id,
                idx,
                turn.timestamp,
                turn.role,
                turn.input_text,
                json.dumps(turn.extracted_environmental_state) if turn.extracted_environmental_state else None,
                json.dumps(turn.response),
                1 if turn.clarification_required else 0,
            ))
            conn.commit()
