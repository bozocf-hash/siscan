"""Migração explícita/aditiva; nunca chamada pela inicialização do servidor."""
from datetime import datetime, timezone
import hashlib
import re
import sqlite3

STATEMENTS=(
'''CREATE TABLE operational_schema_migrations(
 version INTEGER PRIMARY KEY CHECK(version=1),schema_sha256 TEXT NOT NULL,created_at TEXT NOT NULL)''',
'''CREATE TABLE operational_proposals(
 proposal_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL REFERENCES exercises(id),
 source TEXT NOT NULL CHECK(source='didactic'),actor_id INTEGER NOT NULL REFERENCES users(id),
 created_at TEXT NOT NULL,correction_decision_id TEXT REFERENCES operational_decisions(decision_id),
 UNIQUE(proposal_id,exercise_id))''',
'''CREATE TABLE operational_proposal_revisions(
 proposal_id TEXT NOT NULL,exercise_id INTEGER NOT NULL,revision INTEGER NOT NULL CHECK(revision>0),
 scenario_version INTEGER NOT NULL,body_json TEXT NOT NULL,body_sha256 TEXT NOT NULL,
 actor_id INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL,
 PRIMARY KEY(proposal_id,revision),UNIQUE(proposal_id,revision,body_sha256),
 FOREIGN KEY(proposal_id,exercise_id) REFERENCES operational_proposals(proposal_id,exercise_id),
 FOREIGN KEY(exercise_id,scenario_version) REFERENCES scenario_versions(exercise_id,version))''',
'''CREATE TABLE operational_commands(
 command_id TEXT PRIMARY KEY,exercise_id INTEGER NOT NULL REFERENCES exercises(id),
 actor_id INTEGER NOT NULL REFERENCES users(id),operation TEXT NOT NULL,
 payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL,result_json TEXT NOT NULL,
 result_sha256 TEXT NOT NULL,created_at TEXT NOT NULL)''',
'''CREATE TABLE operational_decisions(
 decision_id TEXT PRIMARY KEY,proposal_id TEXT NOT NULL UNIQUE,
 revision INTEGER NOT NULL,body_sha256 TEXT NOT NULL,
 action TEXT NOT NULL CHECK(action IN ('confirm','reject')),reason TEXT NOT NULL CHECK(length(trim(reason))>0),
 actor_id INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL,
 command_id TEXT NOT NULL UNIQUE REFERENCES operational_commands(command_id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(proposal_id,revision,body_sha256) REFERENCES operational_proposal_revisions(proposal_id,revision,body_sha256))''',
'''CREATE TABLE operational_effects(
 decision_id TEXT NOT NULL REFERENCES operational_decisions(decision_id),unit_id TEXT NOT NULL,
 exercise_id INTEGER NOT NULL,team TEXT NOT NULL,revision INTEGER NOT NULL CHECK(revision>0),
 before_revision INTEGER NOT NULL CHECK(before_revision=revision-1),
 snapshot_id TEXT NOT NULL REFERENCES engine_unit_snapshots(snapshot_id),
 refs_json TEXT NOT NULL,refs_sha256 TEXT NOT NULL,before_json TEXT NOT NULL,before_sha256 TEXT NOT NULL,
 after_json TEXT NOT NULL,after_sha256 TEXT NOT NULL,
 PRIMARY KEY(decision_id,unit_id),UNIQUE(unit_id,revision),
 FOREIGN KEY(unit_id,exercise_id,team) REFERENCES engine_units(unit_id,exercise_id,team))''',
'''CREATE INDEX operational_effects_unit ON operational_effects(exercise_id,unit_id,revision)''',
)
for table in ('schema_migrations','proposals','proposal_revisions','commands','decisions','effects'):
    for action in ('UPDATE','DELETE'):
        STATEMENTS+=(f'''CREATE TRIGGER operational_{table}_no_{action.lower()} BEFORE {action} ON operational_{table}
 BEGIN SELECT RAISE(ABORT,'Operational history is immutable'); END''',)


def _normalized(sql):return ' '.join(sql.strip().rstrip(';').split())


def _objects():
    return {re.match(r'CREATE (?:TABLE|INDEX|TRIGGER) (\w+)',sql)[1]:_normalized(sql) for sql in STATEMENTS}


def _sha():return hashlib.sha256('\n'.join(STATEMENTS).encode('utf-8')).hexdigest()


def validate(db):
    if not db.execute('PRAGMA foreign_keys').fetchone()[0]:
        raise sqlite3.DatabaseError('Operational storage requires foreign keys.')
    actual={r[0]:_normalized(r[1]) for r in db.execute(
        "SELECT name,sql FROM sqlite_master WHERE name GLOB 'operational_*' AND sql IS NOT NULL")}
    if actual!=_objects():raise sqlite3.DatabaseError('Operational schema missing or incompatible.')
    rows=[tuple(r) for r in db.execute('SELECT version,schema_sha256 FROM operational_schema_migrations')]
    if rows!=[(1,_sha())] or db.execute('PRAGMA foreign_key_check').fetchone():
        raise sqlite3.DatabaseError('Operational migration/integrity mismatch.')


def migrate(db):
    """Commit próprio; requer conexão independente, nunca altera schema existente."""
    if db.in_transaction or not db.execute('PRAGMA foreign_keys').fetchone()[0]:
        raise sqlite3.DatabaseError('Migration requires independent connection with foreign keys.')
    db.execute('BEGIN IMMEDIATE')
    try:
        if db.execute("SELECT 1 FROM sqlite_master WHERE name GLOB 'operational_*'").fetchone():
            validate(db);db.commit();return False
        for table in ('exercises','users','engine_units','engine_unit_snapshots','scenario_versions'):
            if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():
                raise sqlite3.DatabaseError('Missing SISCAN prerequisite: '+table)
        for sql in STATEMENTS:db.execute(sql)
        db.execute('INSERT INTO operational_schema_migrations VALUES(1,?,?)',
                   (_sha(),datetime.now(timezone.utc).isoformat()))
        validate(db);db.commit();return True
    except Exception:
        db.rollback();raise
