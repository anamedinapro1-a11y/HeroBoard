# main.py
# FastAPI backend for Student Focus App
# Features:
# - Register user (no password) -> user_id
# - Admin code verification to edit schedule
# - CRUD-lite schedule (replace all blocks)
# - Time-aware current block (/today)
# - Drops: star/planet/comet on completion
# - SQLite storage, CORS enabled

import os
import json
import random
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Literal

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

# -------------------------
# Config & setup
# -------------------------
DB_PATH = os.environ.get("DATABASE_PATH", "data.db")
ADMIN_CODE = os.environ.get("ADMIN_CODE", "change-me")
ALLOWED = os.environ.get("ALLOWED_ORIGINS", "*")

app = FastAPI(title="Student Focus App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOWED == "*" else [o.strip() for o in ALLOWED.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL DEFAULT 'Default',
        timezone TEXT DEFAULT 'America/Guatemala'
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL, -- 0=Mon ... 6=Sun
        start_min INTEGER NOT NULL,   -- minutes from 00:00 local
        end_min INTEGER NOT NULL,
        title TEXT NOT NULL,
        color TEXT DEFAULT NULL,
        difficulty TEXT DEFAULT 'medium',
        FOREIGN KEY(schedule_id) REFERENCES schedules(id) ON DELETE CASCADE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS drops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,           -- YYYY-MM-DD
        type TEXT NOT NULL,           -- star | planet | comet
        label TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    # Ensure one default schedule exists
    cur.execute("SELECT id FROM schedules LIMIT 1")
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO schedules (title) VALUES ('Default')")
        schedule_id = cur.lastrowid
        # Seed a tiny example (Mon only)
        seed = [
            (schedule_id, 0, 16*60, 16*60+45, "Math Homework", None, "medium"),
            (schedule_id, 0, 16*60+45, 17*60, "Break", None, "easy"),
            (schedule_id, 0, 17*60, 17*60+40, "Science Reading", None, "hard"),
            (schedule_id, 0, 18*60, 19*60, "Dance Practice", None, "hard"),
        ]
        cur.executemany(
            "INSERT INTO blocks (schedule_id, day_of_week, start_min, end_min, title, color, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?)",
            seed
        )
    conn.commit()
    conn.close()


init_db()

# -------------------------
# Models
# -------------------------
Difficulty = Literal["easy", "medium", "hard"]

class RegisterReq(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class RegisterRes(BaseModel):
    user_id: int
    name: str

class AdminVerifyReq(BaseModel):
    admin_code: str

class OkRes(BaseModel):
    ok: bool

class Block(BaseModel):
    # minutes from 00:00 local (e.g., 8:30 => 510)
    day_of_week: int = Field(ge=0, le=6)
    start_min: int = Field(ge=0, le=24*60-1)
    end_min: int = Field(ge=1, le=24*60)
    title: str
    color: Optional[str] = None
    difficulty: Difficulty = "medium"

    @validator("end_min")
    def end_after_start(cls, v, values):
        if "start_min" in values and v <= values["start_min"]:
            raise ValueError("end_min must be greater than start_min")
        return v

class ScheduleRes(BaseModel):
    schedule_id: int
    title: str
    blocks: List[Block]

class ReplaceScheduleReq(BaseModel):
    title: Optional[str] = None
    admin_code: str
    blocks: List[Block]

class TodayQuery(BaseModel):
    tz_offset_minutes: Optional[int] = None  # client offset from UTC (e.g., -360 for GMT-6)
    now_iso: Optional[str] = None            # for testing (ISO string)

class CurrentBlockRes(BaseModel):
    current: Optional[Block]
    minutes_left: Optional[int]
    next_block_starts_in: Optional[int]

class CompleteReq(BaseModel):
    user_id: int
    block_title: str
    difficulty: Difficulty

class DropRes(BaseModel):
    type: Literal["star", "planet", "comet"]
    label: str

# -------------------------
# Helpers
# -------------------------
def is_admin(code: str) -> bool:
    # Simple compare (for school project). For production, hash + constant-time compare.
    return code == ADMIN_CODE

def get_default_schedule_id(conn: sqlite3.Connection) -> int:
    r = conn.execute("SELECT id FROM schedules ORDER BY id LIMIT 1").fetchone()
    return int(r["id"])

def row_to_block(row: sqlite3.Row) -> Block:
    return Block(
        day_of_week=row["day_of_week"],
        start_min=row["start_min"],
        end_min=row["end_min"],
        title=row["title"],
        color=row["color"],
        difficulty=row["difficulty"] or "medium"
    )

def parse_local_now(tz_offset_minutes: Optional[int], now_iso: Optional[str]) -> datetime:
    if now_iso:
        try:
            dt = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid now_iso: {e}")
    else:
        dt = datetime.now(timezone.utc)
    if tz_offset_minutes is None:
        # Default Guatemala time (UTC-6) if not provided
        offset = -6 * 60
    else:
        offset = tz_offset_minutes
    return dt.astimezone(timezone(timedelta(minutes=offset)))

# -------------------------
# Routes
# -------------------------
@app.post("/auth/register", response_model=RegisterRes)
def register(req: RegisterReq):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name) VALUES (?)", (req.name,))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return RegisterRes(user_id=user_id, name=req.name)

@app.post("/auth/admin/verify", response_model=OkRes)
def admin_verify(req: AdminVerifyReq):
    return OkRes(ok=is_admin(req.admin_code))

@app.get("/schedule", response_model=ScheduleRes)
def get_schedule():
    conn = get_db()
    sid = get_default_schedule_id(conn)
    cur = conn.cursor()
    row_sched = cur.execute("SELECT id, title FROM schedules WHERE id=?", (sid,)).fetchone()
    rows = cur.execute(
        "SELECT day_of_week, start_min, end_min, title, color, difficulty FROM blocks WHERE schedule_id=? ORDER BY day_of_week, start_min",
        (sid,)
    ).fetchall()
    conn.close()
    return ScheduleRes(
        schedule_id=sid,
        title=row_sched["title"],
        blocks=[row_to_block(r) for r in rows]
    )

@app.put("/schedule", response_model=OkRes)
def replace_schedule(req: ReplaceScheduleReq):
    if not is_admin(req.admin_code):
        raise HTTPException(status_code=403, detail="Invalid admin code")
    conn = get_db()
    cur = conn.cursor()
    sid = get_default_schedule_id(conn)
    if req.title:
        cur.execute("UPDATE schedules SET title=? WHERE id=?", (req.title, sid))
    # Replace all blocks
    cur.execute("DELETE FROM blocks WHERE schedule_id=?", (sid,))
    cur.executemany(
        "INSERT INTO blocks (schedule_id, day_of_week, start_min, end_min, title, color, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(sid, b.day_of_week, b.start_min, b.end_min, b.title, b.color, b.difficulty) for b in req.blocks]
    )
    conn.commit()
    conn.close()
    return OkRes(ok=True)

@app.post("/today", response_model=CurrentBlockRes)
def today(q: TodayQuery):
    conn = get_db()
    sid = get_default_schedule_id(conn)
    local_now = parse_local_now(q.tz_offset_minutes, q.now_iso)
    dow = (local_now.weekday())  # Mon=0
    minutes_now = local_now.hour * 60 + local_now.minute
    rows = conn.execute(
        "SELECT day_of_week, start_min, end_min, title, color, difficulty FROM blocks WHERE schedule_id=? AND day_of_week=? ORDER BY start_min",
        (sid, dow)
    ).fetchall()
    conn.close()

    current_row = None
    next_row = None
    for r in rows:
        if r["start_min"] <= minutes_now < r["end_min"]:
            current_row = r
            break
        if r["start_min"] > minutes_now and next_row is None:
            next_row = r

    if current_row:
        minutes_left = current_row["end_min"] - minutes_now
        return CurrentBlockRes(
            current=row_to_block(current_row),
            minutes_left=minutes_left,
            next_block_starts_in=None
        )
    else:
        if next_row:
            return CurrentBlockRes(
                current=None,
                minutes_left=None,
                next_block_starts_in=next_row["start_min"] - minutes_now
            )
        return CurrentBlockRes(current=None, minutes_left=None, next_block_starts_in=None)

@app.post("/complete", response_model=DropRes)
def complete(req: CompleteReq):
    # Decide drop type
    rare = random.random() < 0.05
    if rare:
        drop_type = "comet"
    else:
        drop_type = "planet" if req.difficulty == "hard" else "star"

    # Label
    if drop_type == "planet":
        # Planet A, B, C ...
        label = f"Planet {chr(65 + random.randint(0, 25))}"
    elif drop_type == "comet":
        label = "Comet ✨"
    else:
        label = "Star ⭐"

    # Save
    conn = get_db()
    today_str = datetime.now(timezone.utc).date().isoformat()
    conn.execute(
        "INSERT INTO drops (user_id, date, type, label, created_at) VALUES (?, ?, ?, ?, ?)",
        (req.user_id, today_str, drop_type, label, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    return DropRes(type=drop_type, label=label)

@app.get("/drops/today")
def drops_today(user_id: int):
    today_str = datetime.now(timezone.utc).date().isoformat()
    conn = get_db()
    rows = conn.execute(
        "SELECT id, type, label, created_at FROM drops WHERE user_id=? AND date=? ORDER BY created_at DESC",
        (user_id, today_str)
    ).fetchall()
    conn.close()
    return [{"id": r["id"], "type": r["type"], "label": r["label"], "created_at": r["created_at"]} for r in rows]

# Health check for Railway
@app.get("/health")
def health():
    return {"ok": True}
