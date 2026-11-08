"""Checks the document workflow with an isolated, in-memory database."""
import io
import json
import sqlite3
import sys
from pathlib import Path

from app import Handler, SCHEMA, deadline_status
from datetime import datetime, timezone


def main():
    now = datetime(2026, 11, 8, 15, 0, tzinfo=timezone.utc)
    assert deadline_status(None, now=now) == "no_deadline"
    assert deadline_status("2026-11-08T12:00:00-03:00", now=now) == "within_deadline"
    assert deadline_status("2026-11-08T14:59:00Z", now=now) == "overdue"
    assert deadline_status("2026-11-08T15:00:00Z", "2026-11-08T15:00:01Z") == "submitted_late"
    assert deadline_status("2026-11-08T15:00:00Z", "2026-11-08T15:00:00Z") == "submitted_on_time"
    assert deadline_status("2026-11-08T15:00:00") == "needs_timezone"
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    for uid, role, team in [(1, "student", "AZUL"), (2, "student", "VERMELHO"), (3, "evaluator", None), (4, "instructor", None)]:
        db.execute("INSERT INTO users(id,username,display_name,role,team,salt,password_hash) VALUES(?,?,?,?,?,?,?)", (uid, str(uid), role, role, team, b"salt", b"hash"))
    db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'CHECK','Scenario','Objective')")
    db.execute("INSERT INTO scenario_versions(exercise_id,version,title,objective,changed_at) VALUES(1,1,'Scenario','Objective','2026-11-08')")
    for uid in range(1, 5):
        db.execute("INSERT INTO assignments VALUES(1,?)", (uid,))
    h = object.__new__(Handler)
    responses = []
    h.send_json = lambda status, body, **kw: responses.append((status, body))
    student = {"uid": 1, "role": "student", "team": "AZUL"}
    peer = {"uid": 2, "role": "student", "team": "VERMELHO"}
    evaluator = {"uid": 3, "role": "evaluator"}
    instructor = {"uid": 4, "role": "instructor"}
    payload = {"document_type": "EPO", "group_name": "Group", "asset_ids": [], "rationale": "Reason", "submit": True}
    if "--print-fixture" in sys.argv:
        payload["rationale"] = "\n\n".join(f"Parágrafo demonstrativo {i}: análise didática com acentuação, revisão humana e rastreabilidade. " * 3 for i in range(1, 31))
    h.save_submission(db, student, payload)
    assert responses[-1][0] == 200, responses[-1]
    sid = db.execute("SELECT id FROM submissions").fetchone()[0]
    db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(5,'unassigned','Unassigned','evaluator',?,?)", (b"salt", b"hash"))
    h.review(db, {"uid": 5, "role": "evaluator"}, {"submission_id": sid, "status": "validated"})
    assert responses[-1][0] == 403
    assert db.execute("SELECT status FROM submissions WHERE id=?", (sid,)).fetchone()[0] == "submitted"
    h.report(db, student, str(sid))
    assert responses[-1][0] == 403
    h.report(db, peer, str(sid))
    assert responses[-1][0] == 403
    h.review(db, evaluator, {"submission_id": sid, "status": "returned", "comment": "Revise"})
    assert responses[-1][0] == 200
    h.save_submission(db, student, payload)
    assert responses[-1][0] == 200
    rows = db.execute("SELECT id,status FROM submissions ORDER BY revision").fetchall()
    assert len(rows) == 2 and rows[0]["status"] == "returned"
    sid = rows[1]["id"]
    h.review(db, evaluator, {"submission_id": sid, "status": "validated", "comment": "Validated"})
    assert responses[-1][0] == 200
    validated = db.execute("SELECT * FROM submissions WHERE id=?", (sid,)).fetchone()
    assert Handler.submission_json(validated, include_private=False)["review_comment"] == ""
    assert Handler.submission_json(validated, include_private=True)["review_comment"] == "Validated"
    h.release(db, evaluator, {"submission_id": sid})
    assert responses[-1][0] == 403
    h.release(db, instructor, {"submission_id": sid})
    assert responses[-1][0] == 200
    h.send_response = lambda status: responses.append((status, {}))
    h.send_header = lambda *args: None
    h.end_headers = lambda: None
    h.wfile = io.BytesIO()
    h.report(db, student, str(sid))
    assert responses[-1][0] == 200
    content = h.wfile.getvalue().decode()
    assert "Scenario" in content and "Validated" in content and "Resultado liberado" in content
    assert "print-report" in content and "/report.js" in content
    if "--print-fixture" in sys.argv:
        target = Path(__file__).resolve().parent.parent / "tmp" / "print" / "report.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Print fixture: {target}")
    h.report(db, peer, str(sid))
    assert responses[-1][0] == 403
    print("PASS: submission, preserved revision, evaluator validation, instructor release, report access and peer denial")
    instructor.update(username="4", display_name="Instructor", team=None)
    panel = h.dashboard(db, instructor, "test-csrf")
    assert len(panel["participants"]) == 2
    statuses = {item["id"]: item["status"] for item in panel["participants"]}
    assert statuses[1] == "released" and statuses[2] is None
    print("PASS: participant overview includes latest revision and students who have not started")
    student_notices = db.execute("SELECT * FROM notifications WHERE user_id=1 ORDER BY id").fetchall()
    assert len(student_notices) == 2
    assert "revisão" in student_notices[0]["title"] and "liberado" in student_notices[1]["title"]
    identifier = student_notices[0]["id"]
    h.read_notification(db, peer, {"notification_id": identifier})
    assert responses[-1][0] == 404
    assert db.execute("SELECT read_at FROM notifications WHERE id=?", (identifier,)).fetchone()[0] is None
    h.read_notification(db, student, {"notification_id": identifier})
    assert responses[-1][0] == 200
    h.read_notification(db, student, {"notification_id": identifier})
    assert db.execute("SELECT COUNT(*) FROM events WHERE event_type='notification.read'").fetchone()[0] == 1
    assert db.execute("SELECT COUNT(*) FROM notifications WHERE user_id=5").fetchone()[0] == 0
    print("PASS: notification recipients, peer denial and idempotent read tracking")
    db.execute("INSERT INTO assets(id,exercise_id,team,code,name,category,fiche) VALUES(1,1,'AZUL','A1','Meio Azul','Didático','Sintético')")
    db.execute("INSERT INTO assets(id,exercise_id,team,code,name,category,fiche) VALUES(2,1,'VERMELHO','V1','Meio Vermelho','Didático','Sintético')")
    h.allocate_assets(db, student, {"student_id": 1, "asset_ids": [1]})
    assert responses[-1][0] == 403
    h.allocate_assets(db, instructor, {"student_id": 1, "asset_ids": [2]})
    assert responses[-1][0] == 403
    attempt = dict(payload, asset_ids=[1])
    h.save_submission(db, student, attempt)
    assert responses[-1][0] == 403
    h.allocate_assets(db, instructor, {"student_id": 1, "asset_ids": [1]})
    assert responses[-1][0] == 200
    student.update(username="1", display_name="Student")
    panel = h.dashboard(db, student, "test")
    assert [asset["id"] for asset in panel["assets"]] == [1]
    peer.update(username="2", display_name="Peer")
    assert h.dashboard(db, peer, "test")["assets"] == []
    h.allocate_assets(db, instructor, {"student_id": 1, "asset_ids": []})
    panel = h.dashboard(db, student, "test")
    assert panel["assets"] == [] and panel["historical_assets"][0]["id"] == 1
    assert db.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 2
    h.allocate_assets(db, instructor, {"student_id": 2, "asset_ids": [2]})
    h.save_submission(db, peer, dict(payload, asset_ids=[2]))
    assert responses[-1][0] == 200
    assert db.execute("SELECT asset_ids_json FROM submissions WHERE student_id=2").fetchone()[0] == "[2]"
    print("PASS: instructor allocation, team and student scope, revocation and preserved history")
    db.close()


if __name__ == "__main__":
    main()
