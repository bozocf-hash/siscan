"""Checks the document workflow with an isolated, in-memory database."""
import io
import json
import sqlite3

from app import Handler, SCHEMA


def main():
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
    h.save_submission(db, student, payload)
    assert responses[-1][0] == 200, responses[-1]
    sid = db.execute("SELECT id FROM submissions").fetchone()[0]
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
    assert "Scenario" in content and "Validated" in content and "submission.released" in content
    h.report(db, peer, str(sid))
    assert responses[-1][0] == 403
    print("PASS: submission, preserved revision, evaluator validation, instructor release, report access and peer denial")
    db.close()


if __name__ == "__main__":
    main()
