#!/usr/bin/env python3
"""Local-only didactic SISCAN prototype. Uses only Python's standard library."""

from __future__ import annotations

import hashlib
import hmac
import html
import json
import os
import secrets
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "siscan-demo.sqlite3"
REVIEW_DB_PATH = DATA_DIR / "db3k-review-01.sqlite3"
DOMAIN_REPORT_PATH = DATA_DIR / "db3k-domains-01.json"
HOST = "127.0.0.1"
PORT = int(os.environ.get("SISCAN_PORT", "8787"))
SESSION_SECONDS = 8 * 60 * 60
ITERATIONS = 310_000
COOKIE_NAME = "siscan_demo_session"
WARNING_NO_RATIONALE = (
    "Atenção: você optou por não apresentar uma justificativa para esta decisão. "
    "A ausência de justificativa será registrada no histórico do exercício e poderá "
    "ser considerada pelo instrutor ou avaliador durante a avaliação."
)

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('instructor','evaluator','student')),
  team TEXT CHECK(team IN ('AZUL','VERMELHO') OR team IS NULL),
  salt BLOB NOT NULL,
  password_hash BLOB NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS exercises (
  id INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  objective TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'open' CHECK(state IN ('open','closed')),
  max_attempts INTEGER CHECK(max_attempts IS NULL OR max_attempts > 0),
  due_at TEXT,
  scenario_version INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS scenario_versions (
  exercise_id INTEGER NOT NULL REFERENCES exercises(id),
  version INTEGER NOT NULL,
  title TEXT NOT NULL,
  objective TEXT NOT NULL,
  changed_by INTEGER REFERENCES users(id),
  change_note TEXT NOT NULL DEFAULT '',
  changed_at TEXT NOT NULL,
  PRIMARY KEY(exercise_id,version)
);
CREATE TABLE IF NOT EXISTS assets (
  id INTEGER PRIMARY KEY,
  exercise_id INTEGER NOT NULL REFERENCES exercises(id),
  team TEXT NOT NULL CHECK(team IN ('AZUL','VERMELHO')),
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  fiche TEXT NOT NULL,
  source_label TEXT NOT NULL DEFAULT 'Dado didático sintético',
  UNIQUE(exercise_id, team, code)
);
CREATE TABLE IF NOT EXISTS assignments (
  exercise_id INTEGER NOT NULL REFERENCES exercises(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  PRIMARY KEY(exercise_id,user_id)
);
CREATE TABLE IF NOT EXISTS submissions (
  id INTEGER PRIMARY KEY,
  exercise_id INTEGER NOT NULL REFERENCES exercises(id),
  student_id INTEGER NOT NULL REFERENCES users(id),
  revision INTEGER NOT NULL,
  document_type TEXT NOT NULL CHECK(document_type IN ('Exame da Situação','EPO')),
  group_name TEXT NOT NULL,
  asset_ids_json TEXT NOT NULL,
  rationale TEXT NOT NULL DEFAULT '',
  scenario_version INTEGER NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('draft','submitted','returned','validated','released')),
  reviewer_id INTEGER REFERENCES users(id),
  review_comment TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  submitted_at TEXT,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(exercise_id,student_id,revision)
);
CREATE TABLE IF NOT EXISTS asset_allocations (
  exercise_id INTEGER NOT NULL REFERENCES exercises(id),
  student_id INTEGER NOT NULL REFERENCES users(id),
  asset_id INTEGER NOT NULL REFERENCES assets(id),
  allocated_by INTEGER NOT NULL REFERENCES users(id),
  active INTEGER NOT NULL CHECK(active IN (0,1)),
  updated_at TEXT NOT NULL,
  PRIMARY KEY(exercise_id,student_id,asset_id)
);
CREATE TABLE IF NOT EXISTS party_allocations (
  exercise_id INTEGER NOT NULL REFERENCES exercises(id),
  team TEXT NOT NULL CHECK(team IN ('AZUL','VERMELHO')),
  asset_id INTEGER NOT NULL REFERENCES assets(id),
  allocated_by INTEGER NOT NULL REFERENCES users(id),
  active INTEGER NOT NULL CHECK(active IN (0,1)),
  updated_at TEXT NOT NULL,
  PRIMARY KEY(exercise_id,team,asset_id)
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY,
  exercise_id INTEGER REFERENCES exercises(id),
  actor_id INTEGER NOT NULL REFERENCES users(id),
  subject_user_id INTEGER REFERENCES users(id),
  submission_id INTEGER REFERENCES submissions(id),
  event_type TEXT NOT NULL,
  detail_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  csrf_token TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY,
  exercise_id INTEGER NOT NULL REFERENCES exercises(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  event_id INTEGER NOT NULL REFERENCES events(id),
  title TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  read_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_submissions_student ON submissions(student_id,exercise_id,revision);
CREATE INDEX IF NOT EXISTS idx_events_exercise ON events(exercise_id,created_at);
"""


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def password_record(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return salt, derived


def event(db: sqlite3.Connection, actor: int, event_type: str, *, exercise: int | None = None,
          subject: int | None = None, submission: int | None = None, detail: dict | None = None) -> None:
    cursor = db.execute(
        "INSERT INTO events(exercise_id,actor_id,subject_user_id,submission_id,event_type,detail_json) "
        "VALUES(?,?,?,?,?,?)",
        (exercise, actor, subject, submission, event_type, json.dumps(detail or {}, ensure_ascii=False)),
    )
    recipients = []
    title = None
    if event_type == "submission.submitted":
        recipients = [row[0] for row in db.execute(
            "SELECT u.id FROM users u JOIN assignments a ON a.user_id=u.id "
            "WHERE a.exercise_id=? AND u.active=1 AND u.role IN ('instructor','evaluator')", (exercise,))]
        title = "Novo documento submetido para avaliação"
    elif event_type in ("submission.returned", "submission.released") and subject:
        recipients = [subject]
        title = "Documento devolvido para revisão" if event_type == "submission.returned" else "Resultado liberado pelo instrutor"
    elif event_type == "assets.allocated" and subject:
        recipients = [subject]
        title = "Sua alocação de meios foi atualizada pelo instrutor"
    elif event_type == "assets.party_allocated":
        recipients = [row[0] for row in db.execute(
            "SELECT u.id FROM users u JOIN assignments a ON a.user_id=u.id WHERE a.exercise_id=? AND u.team=? AND u.role='student' AND u.active=1",
            (exercise, (detail or {}).get("team")))]
        title = "Os meios disponíveis para seu partido foram atualizados"
    if title:
        db.executemany("INSERT INTO notifications(exercise_id,user_id,event_id,title) VALUES(?,?,?,?)",
                       [(exercise, recipient, cursor.lastrowid, title) for recipient in recipients if recipient != actor])


def initialize() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with connect() as db:
        db.executescript(SCHEMA)
        existing_exercise = db.execute("SELECT * FROM exercises ORDER BY id LIMIT 1").fetchone()
        if existing_exercise:
            if not db.execute("SELECT 1 FROM scenario_versions WHERE exercise_id=? AND version=?",
                              (existing_exercise["id"], existing_exercise["scenario_version"])).fetchone():
                db.execute(
                    "INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(?,?,?,?,?)",
                    (existing_exercise["id"], existing_exercise["scenario_version"], existing_exercise["title"],
                     existing_exercise["objective"], existing_exercise["updated_at"]),
                )
            return

        passwords = {
            "instructor": os.environ.get("SISCAN_INSTRUCTOR_PASSWORD", ""),
            "evaluator": os.environ.get("SISCAN_EVALUATOR_PASSWORD", ""),
            "student": os.environ.get("SISCAN_STUDENT_PASSWORD", ""),
        }
        if any(len(value) < 12 for value in passwords.values()):
            raise RuntimeError("Configure senhas locais com pelo menos 12 caracteres nas variáveis SISCAN_*_PASSWORD.")

        users: list[tuple[str, str, str, str | None]] = [
            ("instrutor", "Instrutor demonstrativo", "instructor", None),
            ("avaliador", "Avaliador demonstrativo", "evaluator", None),
        ]
        users += [(f"azul-{i:02d}", f"Aluno Azul {i:02d}", "student", "AZUL") for i in range(1, 9)]
        users += [(f"vermelho-{i:02d}", f"Aluno Vermelho {i:02d}", "student", "VERMELHO") for i in range(1, 9)]
        for username, display_name, role, team in users:
            salt, digest = password_record(passwords[role])
            db.execute(
                "INSERT INTO users(username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,?)",
                (username, display_name, role, team, salt, digest),
            )

        db.execute(
            "INSERT INTO exercises(code,title,objective,max_attempts,due_at) VALUES(?,?,?,?,?)",
            ("SISCAN-DEMO-01", "Exercício demonstrativo", "Organizar um grupamento didático e registrar o raciocínio em um documento.", None, None),
        )
        exercise_id = int(db.execute("SELECT id FROM exercises WHERE code='SISCAN-DEMO-01'").fetchone()[0])
        seeded_exercise = db.execute("SELECT * FROM exercises WHERE id=?", (exercise_id,)).fetchone()
        db.execute(
            "INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(?,?,?,?,?)",
            (exercise_id, seeded_exercise["scenario_version"], seeded_exercise["title"],
             seeded_exercise["objective"], seeded_exercise["updated_at"]),
        )
        db.executemany(
            "INSERT INTO assignments(exercise_id,user_id) SELECT ?,id FROM users WHERE username=?",
            [(exercise_id, username) for username, *_ in users],
        )
        asset_rows = []
        for team in ("AZUL", "VERMELHO"):
            for i, category in enumerate(("Comando", "Observação", "Apoio", "Ligação"), 1):
                asset_rows.append((exercise_id, team, f"{team[:1]}-SYN-{i:02d}", f"Meio didático {i:02d}", category,
                                   f"Ficha técnica sintética. Categoria: {category}. Atributos operacionais não representados."))
        db.executemany(
            "INSERT INTO assets(exercise_id,team,code,name,category,fiche) VALUES(?,?,?,?,?,?)", asset_rows
        )


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def deadline_status(due_at, submitted_at=None, now=None):
    if not due_at:
        return "no_deadline"
    try:
        due = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
        if due.tzinfo is None:
            return "needs_timezone"
        if submitted_at:
            submitted = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
            if submitted.tzinfo is None:
                return "needs_timezone"
            return "submitted_late" if submitted > due else "submitted_on_time"
        return "overdue" if (now or datetime.now(timezone.utc)) > due else "within_deadline"
    except (ValueError, TypeError, AttributeError):
        return "needs_timezone"


class Handler(BaseHTTPRequestHandler):
    server_version = "SISCAN-Demo/0.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.log_date_time_string()} {self.address_string()} {fmt % args}")

    def send_json(self, status: int, body: dict, *, cookie: str | None = None) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 64_000:
                raise ValueError
            value = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(value, dict):
                raise ValueError
            return value
        except (ValueError, json.JSONDecodeError):
            raise ValueError("JSON inválido ou excede 64 KB")

    def current_user(self, db: sqlite3.Connection) -> tuple[sqlite3.Row, sqlite3.Row] | None:
        raw_cookie = self.headers.get("Cookie", "")
        token = next((part.strip().split("=", 1)[1] for part in raw_cookie.split(";")
                      if part.strip().startswith(COOKIE_NAME + "=")), None)
        if not token:
            return None
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        row = db.execute(
            "SELECT s.*,u.username,u.display_name,u.role,u.team,u.id AS uid,u.active "
            "FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?",
            (token_hash, int(time.time())),
        ).fetchone()
        if not row or not row["active"]:
            return None
        return row, row

    def require_user(self, db: sqlite3.Connection) -> tuple[sqlite3.Row, sqlite3.Row] | None:
        result = self.current_user(db)
        if result is None:
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "Autenticação necessária."})
        return result

    def check_csrf(self, session: sqlite3.Row) -> bool:
        token = self.headers.get("X-CSRF-Token", "")
        return bool(token) and hmac.compare_digest(token, session["csrf_token"])

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            data = (STATIC / "index.html").read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)
            return
        if path in ("/app.js", "/report.js", "/styles.css", "/fluxograma.jpg"):
            target = STATIC / path.rsplit("/", 1)[1]
            data = target.read_bytes()
            content_type = ("text/javascript; charset=utf-8" if path.endswith(".js") else
                            "text/css; charset=utf-8" if path.endswith(".css") else "image/jpeg")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)
            return

        with connect() as db:
            if path == "/api/catalog-candidates":
                current = self.require_user(db)
                if current:
                    self.candidate_catalog(db, current[1])
                return
            if path.startswith("/report/"):
                current = self.require_user(db)
                if not current:
                    return
                self.report(db, current[1], path.rsplit("/", 1)[-1])
                return
            if path == "/api/me":
                current = self.current_user(db)
                if not current:
                    self.send_json(HTTPStatus.OK, {"user": None})
                else:
                    session, user = current
                    self.send_json(HTTPStatus.OK, {"user": self.user_json(user), "csrf": session["csrf_token"]})
                return
            if path == "/api/dashboard":
                current = self.require_user(db)
                if not current:
                    return
                session, user = current
                self.send_json(HTTPStatus.OK, self.dashboard(db, user, session["csrf_token"]))
                return
        self.send_json(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        origin = self.headers.get("Origin")
        host = self.headers.get("Host", "")
        if origin and origin != f"http://{host}":
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Origem da solicitação inválida."})
            return
        try:
            payload = self.read_json()
        except ValueError as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        with connect() as db:
            if path == "/api/login":
                self.login(db, payload)
                return
            current = self.require_user(db)
            if not current:
                return
            session, user = current
            if not self.check_csrf(session):
                self.send_json(HTTPStatus.FORBIDDEN, {"error": "Token de segurança inválido. Atualize a página."})
                return
            if path == "/api/logout":
                db.execute("DELETE FROM sessions WHERE token_hash=?", (session["token_hash"],))
                self.send_json(HTTPStatus.OK, {"ok": True}, cookie=f"{COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0")
            elif path == "/api/submission":
                self.save_submission(db, user, payload)
            elif path == "/api/review":
                self.review(db, user, payload)
            elif path == "/api/release":
                self.release(db, user, payload)
            elif path == "/api/exercise-config":
                self.configure_exercise(db, user, payload)
            elif path == "/api/scenario":
                self.update_scenario(db, user, payload)
            elif path == "/api/notifications/read":
                self.read_notification(db, user, payload)
            elif path == "/api/allocations":
                self.allocate_assets(db, user, payload)
            else:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})

    @staticmethod
    def user_json(user: sqlite3.Row) -> dict:
        return {"id": user["uid"], "username": user["username"], "name": user["display_name"],
                "role": user["role"], "team": user["team"]}

    def login(self, db: sqlite3.Connection, payload: dict) -> None:
        username = str(payload.get("username", ""))[:80]
        password = str(payload.get("password", ""))[:500]
        user = db.execute("SELECT * FROM users WHERE username=? AND active=1", (username,)).fetchone()
        if not user:
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "Usuário ou senha inválidos."})
            return
        _, candidate = password_record(password, bytes(user["salt"]))
        if not hmac.compare_digest(candidate, bytes(user["password_hash"])):
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "Usuário ou senha inválidos."})
            return
        token = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(24)
        db.execute("INSERT INTO sessions(token_hash,user_id,csrf_token,expires_at) VALUES(?,?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(), user["id"], csrf, int(time.time()) + SESSION_SECONDS))
        self.send_json(HTTPStatus.OK, {"ok": True}, cookie=f"{COOKIE_NAME}={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_SECONDS}")

    def dashboard(self, db: sqlite3.Connection, user: sqlite3.Row, csrf: str) -> dict:
        exercise = db.execute("SELECT * FROM exercises ORDER BY id LIMIT 1").fetchone()
        base = {"user": self.user_json(user), "csrf": csrf,
                "exercise": dict(exercise) if exercise else None}
        base["notifications"] = [dict(row) for row in db.execute(
            "SELECT n.id,n.title,n.created_at,n.read_at FROM notifications n "
            "JOIN assignments a ON a.exercise_id=n.exercise_id AND a.user_id=n.user_id "
            "WHERE n.user_id=? ORDER BY n.id DESC LIMIT 100", (user["uid"],))]
        if not exercise:
            return base
        assigned = db.execute("SELECT 1 FROM assignments WHERE exercise_id=? AND user_id=?",
                              (exercise["id"], user["uid"])).fetchone()
        if not assigned:
            return {"user": self.user_json(user), "csrf": csrf, "exercise": None,
                    "error": "Este participante não está atribuído ao exercício."}
        if user["role"] == "student":
            if not assigned:
                base["error"] = "Este participante não está atribuído ao exercício."
                return base
            assets = db.execute("SELECT m.id,m.code,m.name,m.category,m.fiche,m.source_label FROM assets m "
                                "JOIN party_allocations a ON a.asset_id=m.id AND a.exercise_id=m.exercise_id AND a.team=m.team "
                                "WHERE m.exercise_id=? AND m.team=? AND a.active=1 ORDER BY m.id",
                                (exercise["id"], user["team"])).fetchall()
            base["historical_assets"] = [dict(row) for row in db.execute(
                "SELECT id,code,name FROM assets WHERE exercise_id=? AND team=? AND id IN "
                "(SELECT asset_id FROM party_allocations WHERE exercise_id=? AND team=?)",
                (exercise["id"], user["team"], exercise["id"], user["team"]))]
            submissions = db.execute("SELECT * FROM submissions WHERE exercise_id=? AND student_id=? ORDER BY revision DESC",
                                     (exercise["id"], user["uid"])).fetchall()
            base.update({"assets": [dict(row) for row in assets],
                         "submissions": [self.submission_json(row, include_private=False) for row in submissions]})
            base["deadline_status"] = deadline_status(exercise["due_at"], submissions[0]["submitted_at"] if submissions else None)
        elif user["role"] in ("instructor", "evaluator"):
            rows = db.execute(
                "SELECT s.*,u.username,u.display_name,u.team FROM submissions s JOIN users u ON u.id=s.student_id "
                "WHERE s.exercise_id=? ORDER BY s.created_at DESC,s.revision DESC", (exercise["id"],)
            ).fetchall()
            base["submissions"] = [self.submission_json(row, include_private=True) for row in rows]
            base["events"] = [dict(row) for row in db.execute(
                "SELECT e.event_type,e.detail_json,e.created_at,u.display_name FROM events e "
                "JOIN users u ON u.id=e.actor_id WHERE e.exercise_id=? ORDER BY e.id DESC LIMIT 50", (exercise["id"],)
            )]
            base["scenario_versions"] = [dict(row) for row in db.execute(
                "SELECT version,title,objective,change_note,changed_at,u.display_name AS changed_by "
                "FROM scenario_versions v LEFT JOIN users u ON u.id=v.changed_by "
                "WHERE exercise_id=? ORDER BY version DESC", (exercise["id"],)
            )]
            if user["role"] == "instructor":
                base["participants"] = [dict(row) for row in db.execute(
                    "SELECT u.id,u.display_name,u.team,s.status,s.revision,s.document_type,s.updated_at,s.submitted_at "
                    "FROM assignments a JOIN users u ON u.id=a.user_id "
                    "LEFT JOIN submissions s ON s.id=(SELECT id FROM submissions "
                    "WHERE exercise_id=a.exercise_id AND student_id=u.id ORDER BY revision DESC LIMIT 1) "
                    "WHERE a.exercise_id=? AND u.role='student' ORDER BY u.team,u.display_name",
                    (exercise["id"],))]
                for participant in base["participants"]:
                    participant["deadline_status"] = deadline_status(exercise["due_at"], participant["submitted_at"])
                    participant["allocated_asset_ids"] = [row[0] for row in db.execute(
                        "SELECT asset_id FROM party_allocations WHERE exercise_id=? AND team=? AND active=1 ORDER BY asset_id",
                        (exercise["id"], participant["team"]))]
                base["party_allocations"] = {team: [row[0] for row in db.execute(
                    "SELECT asset_id FROM party_allocations WHERE exercise_id=? AND team=? AND active=1 ORDER BY asset_id",
                    (exercise["id"], team))] for team in ("AZUL", "VERMELHO")}
                base["assets"] = [dict(row) for row in db.execute(
                    "SELECT id,code,name,category,team,fiche,source_label FROM assets WHERE exercise_id=? ORDER BY team,id",
                    (exercise["id"],))]
        return base

    @staticmethod
    def submission_json(row: sqlite3.Row, *, include_private: bool) -> dict:
        result = {key: row[key] for key in ("id", "revision", "document_type", "group_name", "rationale",
                                            "scenario_version", "status", "review_comment", "created_at",
                                            "submitted_at", "updated_at") if key in row.keys()}
        result["asset_ids"] = json.loads(row["asset_ids_json"])
        if not include_private and row["status"] not in ("returned", "released"):
            result["review_comment"] = ""
        if "display_name" in row.keys():
            result["student_name"] = row["display_name"]
            result["student_username"] = row["username"]
            result["team"] = row["team"]
        return result

    def save_submission(self, db: sqlite3.Connection, user: sqlite3.Row, payload: dict) -> None:
        if user["role"] != "student":
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Somente alunos podem editar documentos."})
            return
        exercise = db.execute("SELECT * FROM exercises ORDER BY id LIMIT 1").fetchone()
        if not exercise or exercise["state"] != "open" or not db.execute(
            "SELECT 1 FROM assignments WHERE exercise_id=? AND user_id=?", (exercise["id"], user["uid"])
        ).fetchone():
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Exercício fechado ou participante sem atribuição."})
            return
        document_type = payload.get("document_type")
        group_name = str(payload.get("group_name", "")).strip()[:100]
        rationale = str(payload.get("rationale", ""))[:12_000]
        asset_ids = payload.get("asset_ids", [])
        submit = bool(payload.get("submit"))
        if document_type not in ("Exame da Situação", "EPO") or not group_name:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Informe o tipo documental e o nome do grupamento."})
            return
        if not isinstance(asset_ids, list) or len(asset_ids) > 20 or any(not isinstance(x, int) for x in asset_ids):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Seleção de meios inválida."})
            return
        own_assets = {row[0] for row in db.execute(
            "SELECT m.id FROM assets m JOIN party_allocations a ON a.asset_id=m.id AND a.exercise_id=m.exercise_id AND a.team=m.team "
            "WHERE m.exercise_id=? AND m.team=? AND a.active=1",
            (exercise["id"], user["team"]))}
        if not set(asset_ids).issubset(own_assets):
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "A seleção inclui meios não alocados ao partido do aluno."})
            return

        previous = db.execute("SELECT * FROM submissions WHERE exercise_id=? AND student_id=? ORDER BY revision DESC LIMIT 1",
                              (exercise["id"], user["uid"])).fetchone()
        if previous and previous["status"] not in ("draft", "returned"):
            self.send_json(HTTPStatus.CONFLICT, {"error": "O documento foi submetido. Aguarde a devolução do avaliador para criar nova versão."})
            return
        if submit and not rationale.strip() and not payload.get("confirm_no_rationale"):
            self.send_json(HTTPStatus.CONFLICT, {"confirmation_required": True, "warning": WARNING_NO_RATIONALE})
            return
        submitted_count = db.execute("SELECT COUNT(*) FROM submissions WHERE exercise_id=? AND student_id=? AND submitted_at IS NOT NULL",
                                     (exercise["id"], user["uid"])).fetchone()[0]
        if submit and exercise["max_attempts"] is not None and submitted_count >= exercise["max_attempts"]:
            self.send_json(HTTPStatus.CONFLICT, {"error": "Limite de tentativas configurado para este exercício atingido."})
            return

        revision = int(previous["revision"] + 1) if previous and previous["status"] == "returned" else int(previous["revision"]) if previous else 1
        now = iso_now()
        status = "submitted" if submit else "draft"
        if previous and previous["status"] == "draft":
            submission_id = previous["id"]
            db.execute("UPDATE submissions SET document_type=?,group_name=?,asset_ids_json=?,rationale=?,status=?,submitted_at=?,updated_at=? WHERE id=?",
                       (document_type, group_name, json.dumps(asset_ids), rationale, status,
                        now if submit else None, now, submission_id))
        else:
            cur = db.execute(
                "INSERT INTO submissions(exercise_id,student_id,revision,document_type,group_name,asset_ids_json,rationale,scenario_version,status,submitted_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (exercise["id"], user["uid"], revision, document_type, group_name, json.dumps(asset_ids), rationale,
                 exercise["scenario_version"], status, now if submit else None, now),
            )
            submission_id = cur.lastrowid
        event(db, user["uid"], "submission.submitted" if submit else "submission.draft_saved",
              exercise=exercise["id"], subject=user["uid"], submission=submission_id,
              detail={"revision": revision, "document_type": document_type,
                      "rationale_present": bool(rationale.strip()), "no_rationale_confirmed": bool(submit and not rationale.strip())})
        self.send_json(HTTPStatus.OK, {"ok": True, "revision": revision, "status": status})

    def review(self, db: sqlite3.Connection, user: sqlite3.Row, payload: dict) -> None:
        if user["role"] not in ("evaluator", "instructor"):
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Somente avaliador ou instrutor pode revisar."})
            return
        try:
            submission_id = int(payload.get("submission_id"))
        except (TypeError, ValueError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Submissão inválida."})
            return
        status = payload.get("status")
        comment = str(payload.get("comment", "")).strip()[:8_000]
        if status not in ("returned", "validated"):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Decisão de revisão inválida."})
            return
        submission = db.execute("SELECT * FROM submissions WHERE id=?", (submission_id,)).fetchone()
        if submission and not db.execute("SELECT 1 FROM assignments WHERE exercise_id=? AND user_id=?", (submission["exercise_id"], user["uid"])).fetchone():
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Sem atribuição para revisar este exercício."})
            return
        allowed_statuses = ("submitted", "validated") if user["role"] == "instructor" else ("submitted",)
        if not submission or submission["status"] not in allowed_statuses:
            self.send_json(HTTPStatus.CONFLICT, {"error": "Somente documento submetido pode ser revisado."})
            return
        if submission["status"] == "validated" and status != "returned":
            self.send_json(HTTPStatus.CONFLICT, {"error": "Após validação, o instrutor pode devolver para revisão ou liberar o resultado."})
            return
        db.execute("UPDATE submissions SET status=?,reviewer_id=?,review_comment=?,updated_at=? WHERE id=?",
                   (status, user["uid"], comment, iso_now(), submission_id))
        event(db, user["uid"], "submission." + status, exercise=submission["exercise_id"],
              subject=submission["student_id"], submission=submission_id,
              detail={"comment_present": bool(comment), "comment": comment})
        self.send_json(HTTPStatus.OK, {"ok": True})

    def release(self, db: sqlite3.Connection, user: sqlite3.Row, payload: dict) -> None:
        if user["role"] != "instructor":
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Somente o instrutor libera resultados."})
            return
        try:
            submission_id = int(payload.get("submission_id"))
        except (TypeError, ValueError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Submissão inválida."})
            return
        submission = db.execute("SELECT * FROM submissions WHERE id=?", (submission_id,)).fetchone()
        if submission and not db.execute("SELECT 1 FROM assignments WHERE exercise_id=? AND user_id=?", (submission["exercise_id"], user["uid"])).fetchone():
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Sem atribuição para liberar este exercício."})
            return
        if not submission or submission["status"] != "validated":
            self.send_json(HTTPStatus.CONFLICT, {"error": "O instrutor libera após validação do avaliador."})
            return
        db.execute("UPDATE submissions SET status='released',updated_at=? WHERE id=?", (iso_now(), submission_id))
        event(db, user["uid"], "submission.released", exercise=submission["exercise_id"],
              subject=submission["student_id"], submission=submission_id)
        self.send_json(HTTPStatus.OK, {"ok": True})

    def report(self, db: sqlite3.Connection, user: sqlite3.Row, identifier: str) -> None:
        try:
            submission_id = int(identifier)
        except ValueError:
            self.send_json(404, {"error": "Relatório não encontrado."})
            return
        row = db.execute("SELECT s.*,u.display_name,u.team FROM submissions s JOIN users u ON u.id=s.student_id WHERE s.id=?", (submission_id,)).fetchone()
        if not row:
            self.send_json(404, {"error": "Relatório não encontrado."})
            return
        assigned = db.execute("SELECT 1 FROM assignments WHERE exercise_id=? AND user_id=?", (row["exercise_id"], user["uid"])).fetchone()
        allowed = assigned and (user["role"] in ("instructor", "evaluator") or (row["student_id"] == user["uid"] and row["status"] == "released"))
        if not allowed:
            self.send_json(403, {"error": "Relatório não autorizado ou ainda não liberado."})
            return
        scenario = db.execute("SELECT * FROM scenario_versions WHERE exercise_id=? AND version=?", (row["exercise_id"], row["scenario_version"])).fetchone()
        events = db.execute("SELECT e.*,u.display_name FROM events e JOIN users u ON u.id=e.actor_id WHERE submission_id=? ORDER BY e.id", (submission_id,)).fetchall()
        esc = lambda value: html.escape(str(value if value is not None else "—"))
        selected_ids = json.loads(row["asset_ids_json"])
        selected_assets = [dict(asset) for asset in db.execute("SELECT id,code,name,source_label FROM assets WHERE exercise_id=?", (row["exercise_id"],)) if asset["id"] in selected_ids]
        asset_description = "; ".join(f"{asset['code']} — {asset['name']} ({asset['source_label']})" for asset in selected_assets) or "Nenhum meio selecionado"
        sections = [("Participante", row["display_name"]), ("Equipe", row["team"]), ("Documento", row["document_type"]), ("Revisão", row["revision"]), ("Grupamento", row["group_name"]), ("Cenário", f"v{row['scenario_version']} — {scenario['title'] if scenario else 'registro indisponível'}"), ("Objetivo na versão usada", scenario["objective"] if scenario else "Registro indisponível"), ("Meios sintéticos selecionados", row["asset_ids_json"]), ("Justificativa", row["rationale"] or "Ausência de justificativa registrada"), ("Comentário de avaliação", row["review_comment"] or "Sem comentário"), ("Situação", row["status"]), ("Submetido em", row["submitted_at"])]
        sections = [(label, asset_description if label == "Meios sintéticos selecionados" else value) for label, value in sections]
        body = "".join(f"<dt>{esc(label)}</dt><dd>{esc(value)}</dd>" for label, value in sections)
        timeline_items = []
        event_labels = {"submission.draft_saved": "Rascunho salvo", "submission.submitted": "Documento submetido", "submission.returned": "Devolução para revisão", "submission.validated": "Documento validado", "submission.released": "Resultado liberado"}
        for item in events:
            detail = json.loads(item["detail_json"])
            comment = detail.get("comment", "")
            label = event_labels.get(item["event_type"], "Ação registrada")
            timeline_items.append(f"<li>{esc(item['created_at'])} · {esc(item['display_name'])} · {esc(label)}{(' · ' + esc(comment)) if comment else ''}</li>")
        timeline = "".join(timeline_items)
        page = f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Relatório SISCAN {submission_id}</title><link rel='stylesheet' href='/styles.css'><script src='/report.js' defer></script></head><body><main class='container card report'><div class='report-tools'><button class='btn' id='print-report' type='button'>Imprimir / salvar como PDF</button><p>Na janela de impressão, escolha salvar como PDF para obter uma cópia.</p></div><h1>Relatório individual SISCAN</h1><p>Registro demonstrativo {submission_id} · gerado {esc(iso_now())} · dados sintéticos</p><p>Horários com sufixo Z estão em UTC.</p><dl>{body}</dl><h2>Histórico desta revisão</h2><ol>{timeline}</ol><p class='report-note'>Cópia de consulta. A emissão de PDF com QR Code e validação de autenticidade ainda não está disponível.</p></main></body></html>".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(page)

    def candidate_catalog(self, db: sqlite3.Connection, user: sqlite3.Row) -> None:
        assigned = db.execute("SELECT 1 FROM assignments WHERE user_id=? AND exercise_id=(SELECT id FROM exercises ORDER BY id LIMIT 1)", (user["uid"],)).fetchone()
        if user["role"] != "instructor" or not assigned:
            self.send_json(403, {"error": "Consulta restrita ao instrutor atribuído ao exercício."})
            return
        if not REVIEW_DB_PATH.is_file():
            self.send_json(404, {"error": "Amostra DB3K para revisão ainda não preparada nesta instalação."})
            return
        try:
            with closing(sqlite3.connect(REVIEW_DB_PATH.resolve().as_uri() + "?mode=ro", uri=True)) as source:
                source.row_factory = sqlite3.Row
                source.execute("PRAGMA query_only=ON")
                provenance = source.execute("SELECT file_name,sha256,read_at FROM source LIMIT 1").fetchone()
                candidates = source.execute("SELECT candidate_id,source_table,external_id,source_name,raw_codes_json,review_status FROM candidates WHERE review_status='needs_review' ORDER BY source_table,external_id LIMIT 500").fetchall()
                total = source.execute("SELECT COUNT(*) FROM candidates WHERE review_status='needs_review'").fetchone()[0]
                if not provenance:
                    raise ValueError("Missing provenance")
                records = [dict(row) for row in candidates]
                evidence_status = "not_available"
                if DOMAIN_REPORT_PATH.is_file():
                    try:
                        evidence = json.loads(DOMAIN_REPORT_PATH.read_text(encoding="utf-8"))
                        if not isinstance(evidence, dict) or not isinstance(evidence.get("source"), dict) or not isinstance(evidence.get("candidates"), list):
                            raise ValueError("Invalid evidence structure")
                        with REVIEW_DB_PATH.open("rb") as stream:
                            review_hash = hashlib.file_digest(stream, "sha256").hexdigest()
                        if evidence.get("status") != "evidence_only_not_approved" or evidence["source"].get("sha256") != provenance["sha256"] or evidence.get("review_sha256") != review_hash:
                            evidence_status = "mismatch"
                        else:
                            by_id = {}
                            for item in evidence["candidates"]:
                                if not isinstance(item, dict) or not isinstance(item.get("candidate_id"), str) or not isinstance(item.get("domains"), dict):
                                    raise ValueError("Invalid candidate evidence")
                                for domain in item["domains"].values():
                                    if not isinstance(domain, dict) or any(domain.get(key) is not None and not isinstance(domain.get(key), str) for key in ("description", "enum_table", "status", "relation_status")):
                                        raise ValueError("Invalid domain evidence")
                                by_id[item["candidate_id"]] = item["domains"]
                            for record in records:
                                record["domain_evidence"] = by_id.get(record["candidate_id"], {})
                            evidence_status = "available"
                    except (OSError, ValueError, TypeError):
                        evidence_status = "invalid"
                self.send_json(200, {"source": dict(provenance), "candidates": records, "total": total, "limit": 500,
                                     "domain_evidence_status": evidence_status})
        except (sqlite3.Error, ValueError):
            self.send_json(503, {"error": "A amostra de revisão não está disponível em formato válido."})

    def allocate_assets(self, db: sqlite3.Connection, user: sqlite3.Row, payload: dict) -> None:
        if user["role"] != "instructor":
            self.send_json(403, {"error": "Somente o instrutor pode alocar meios."})
            return
        team = payload.get("team")
        ids = payload.get("asset_ids")
        if team not in ("AZUL", "VERMELHO") or not isinstance(ids, list) or len(ids) > 1000 or any(type(value) is not int for value in ids):
            self.send_json(400, {"error": "Partido ou seleção de meios inválidos."})
            return
        exercise = db.execute("SELECT * FROM exercises ORDER BY id LIMIT 1").fetchone()
        if not exercise or not db.execute("SELECT 1 FROM assignments WHERE exercise_id=? AND user_id=?", (exercise["id"], user["uid"])).fetchone():
            self.send_json(403, {"error": "Instrutor sem atribuição ao exercício."})
            return
        allowed = {row[0] for row in db.execute("SELECT id FROM assets WHERE exercise_id=? AND team=?", (exercise["id"], team))}
        selected = set(ids)
        if not selected.issubset(allowed):
            self.send_json(403, {"error": "Selecione somente meios do partido neste exercício."})
            return
        previous = {row[0] for row in db.execute("SELECT asset_id FROM party_allocations WHERE exercise_id=? AND team=? AND active=1", (exercise["id"], team))}
        if selected == previous:
            self.send_json(200, {"ok": True, "changed": False})
            return
        now = iso_now()
        db.execute("UPDATE party_allocations SET active=0,allocated_by=?,updated_at=? WHERE exercise_id=? AND team=? AND active=1", (user["uid"], now, exercise["id"], team))
        for asset_id in selected:
            db.execute("INSERT INTO party_allocations(exercise_id,team,asset_id,allocated_by,active,updated_at) VALUES(?,?,?,?,1,?) "
                       "ON CONFLICT(exercise_id,team,asset_id) DO UPDATE SET active=1,allocated_by=excluded.allocated_by,updated_at=excluded.updated_at",
                       (exercise["id"], team, asset_id, user["uid"], now))
        event(db, user["uid"], "assets.party_allocated", exercise=exercise["id"],
              detail={"team": team, "before": sorted(previous), "after": sorted(selected), "added": sorted(selected-previous), "removed": sorted(previous-selected)})
        self.send_json(200, {"ok": True, "changed": True})

    def read_notification(self, db: sqlite3.Connection, user: sqlite3.Row, payload: dict) -> None:
        identifier = payload.get("notification_id")
        if type(identifier) is not int:
            self.send_json(400, {"error": "Notificação inválida."})
            return
        notification = db.execute(
            "SELECT n.* FROM notifications n JOIN assignments a "
            "ON a.exercise_id=n.exercise_id AND a.user_id=n.user_id WHERE n.id=? AND n.user_id=?",
            (identifier, user["uid"])).fetchone()
        if not notification:
            self.send_json(404, {"error": "Notificação não encontrada."})
            return
        if not notification["read_at"]:
            now = iso_now()
            db.execute("UPDATE notifications SET read_at=? WHERE id=?", (now, identifier))
            event(db, user["uid"], "notification.read", exercise=notification["exercise_id"],
                  subject=user["uid"], detail={"notification_id": identifier, "read_at": now})
        self.send_json(200, {"ok": True})

    def configure_exercise(self, db: sqlite3.Connection, user: sqlite3.Row, payload: dict) -> None:
        if user["role"] != "instructor":
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Somente o instrutor configura o exercício."})
            return
        attempts = payload.get("max_attempts")
        due_at = payload.get("due_at") or None
        if attempts not in (None, ""):
            try:
                attempts = int(attempts)
                if not 1 <= attempts <= 100:
                    raise ValueError
            except (TypeError, ValueError):
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Tentativas devem ser número entre 1 e 100 ou sem limite."})
                return
        else:
            attempts = None
        if due_at and (not isinstance(due_at, str) or len(due_at) > 40):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Prazo inválido."})
            return
        if due_at and deadline_status(due_at) == "needs_timezone":
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "O prazo deve conter data, horário e fuso válidos."})
            return
        exercise = db.execute("SELECT * FROM exercises ORDER BY id LIMIT 1").fetchone()
        db.execute("UPDATE exercises SET max_attempts=?,due_at=?,updated_at=? WHERE id=?",
                   (attempts, due_at, iso_now(), exercise["id"]))
        event(db, user["uid"], "exercise.configuration_changed", exercise=exercise["id"],
              detail={"max_attempts": attempts, "due_at": due_at})
        self.send_json(HTTPStatus.OK, {"ok": True})

    def update_scenario(self, db: sqlite3.Connection, user: sqlite3.Row, payload: dict) -> None:
        if user["role"] != "instructor":
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Somente o instrutor pode alterar o cenário nesta demonstração."})
            return
        title = str(payload.get("title", "")).strip()[:160]
        objective = str(payload.get("objective", "")).strip()[:4000]
        note = str(payload.get("change_note", "")).strip()[:1000]
        if not title or not objective:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Título e objetivo do cenário são obrigatórios."})
            return
        if not payload.get("confirm_change"):
            self.send_json(HTTPStatus.CONFLICT, {
                "confirmation_required": True,
                "warning": "Você está alterando o cenário do jogo e isso pode ter impactos negativos durante a simulação."
            })
            return
        exercise = db.execute("SELECT * FROM exercises ORDER BY id LIMIT 1").fetchone()
        if not exercise:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Exercício não encontrado."})
            return
        if title == exercise["title"] and objective == exercise["objective"]:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Nenhuma alteração de cenário foi informada."})
            return
        previous_version = int(exercise["scenario_version"])
        new_version = previous_version + 1
        now = iso_now()
        db.execute(
            "INSERT OR IGNORE INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(?,?,?,?,?)",
            (exercise["id"], previous_version, exercise["title"], exercise["objective"], exercise["updated_at"]),
        )
        db.execute("UPDATE exercises SET title=?,objective=?,scenario_version=?,updated_at=? WHERE id=?",
                   (title, objective, new_version, now, exercise["id"]))
        db.execute(
            "INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_by,change_note,changed_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (exercise["id"], new_version, title, objective, user["uid"], note, now),
        )
        changed = {}
        if title != exercise["title"]:
            changed["title"] = {"from": exercise["title"], "to": title}
        if objective != exercise["objective"]:
            changed["objective"] = {"from": exercise["objective"], "to": objective}
        event(db, user["uid"], "scenario.changed", exercise=exercise["id"],
              detail={"from_version": previous_version, "to_version": new_version,
                      "changed": changed, "justification": note or None,
                      "during_exercise": exercise["state"] == "open"})
        self.send_json(HTTPStatus.OK, {"ok": True, "scenario_version": new_version})


def main() -> None:
    initialize()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Protótipo SISCAN em http://{HOST}:{PORT} (somente este computador)")
    print("Dados sintéticos locais. Ctrl+C encerra o servidor.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
