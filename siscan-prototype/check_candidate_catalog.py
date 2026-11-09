"""Read-only catalogue access checks with isolated fixtures."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import json
import app
from tools.stage_db3k import TABLES, stage, digest

scratch = Path(__file__).resolve().parent.parent / "tmp"
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source = Path(folder) / "source.db3"
    review = Path(folder) / "review.sqlite3"
    with closing(sqlite3.connect(source)) as db, db:
        for table in TABLES:
            db.execute(f'CREATE TABLE "{table}" (ID INTEGER PRIMARY KEY, Name TEXT)')
            db.execute(f'INSERT INTO "{table}" VALUES(1,?)', ("Nome <não executar>",))
    stage(source, review, 1)
    app.REVIEW_DB_PATH = review
    app.DOMAIN_REPORT_PATH = Path(folder) / "domains.json"
    before = digest(review)
    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        db.executescript(app.SCHEMA)
        db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'teacher','Teacher','instructor',X'00',X'00')")
        db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
        db.execute("INSERT INTO assignments VALUES(1,1)")
        h = object.__new__(app.Handler)
        responses = []
        h.send_json = lambda status, body: responses.append((status, body))
        h.candidate_catalog(db, {"uid": 2, "role": "student"})
        assert responses[-1][0] == 403
        h.candidate_catalog(db, {"uid": 2, "role": "instructor"})
        assert responses[-1][0] == 403
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        status, result = responses[-1]
        assert status == 200 and len(result["candidates"]) == 4
        assert result["domain_evidence_status"] == "not_available"
        candidate_id = result["candidates"][0]["candidate_id"]
        evidence = {"status": "evidence_only_not_approved", "source": {"sha256": digest(source)}, "review_sha256": digest(review),
                    "candidates": [{"candidate_id": candidate_id, "domains": {"Category": {"raw_code": 1, "description": "Descrição literal <teste>", "enum_table": "EnumAircraftCategory", "status": "literal_code_match", "relation_status": "nominal_match_without_fk"}}}]}
        app.DOMAIN_REPORT_PATH.write_text(json.dumps(evidence), encoding="utf-8")
        evidence["candidates"][0]["technical_fields"] = {"Length": {"value": 15.5, "sqlite_type": "REAL", "unit": None, "validation_status": "pending_unit_and_semantics"}, "MaxDepth": {"value": 0, "sqlite_type": "INTEGER", "unit": None, "validation_status": "pending_unit_and_semantics"}}
        app.DOMAIN_REPORT_PATH.write_text(json.dumps(evidence), encoding="utf-8")
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        status, enriched = responses[-1]
        assert status == 200 and enriched["domain_evidence_status"] == "available"
        assert enriched["candidates"][0]["domain_evidence"]["Category"]["description"] == "Descrição literal <teste>"
        assert enriched["candidates"][0]["technical_evidence"]["Length"]["value"] == 15.5
        assert enriched["candidates"][0]["technical_evidence"]["MaxDepth"]["value"] == 0
        evidence["candidates"][0]["technical_fields"]["Length"]["unit"] = "m"
        app.DOMAIN_REPORT_PATH.write_text(json.dumps(evidence), encoding="utf-8")
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][1]["domain_evidence_status"] == "invalid"
        assert not responses[-1][1]["candidates"][0].get("technical_evidence")
        evidence["candidates"][0]["technical_fields"]["Length"]["unit"] = None
        evidence["review_sha256"] = "mismatch"
        app.DOMAIN_REPORT_PATH.write_text(json.dumps(evidence), encoding="utf-8")
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][1]["domain_evidence_status"] == "mismatch"
        assert all(not row.get("domain_evidence") for row in responses[-1][1]["candidates"])
        app.DOMAIN_REPORT_PATH.write_text('{"invalid":', encoding="utf-8")
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][0] == 200 and responses[-1][1]["domain_evidence_status"] == "invalid"
        assert all(row["review_status"] == "needs_review" for row in result["candidates"])
        assert result["source"]["sha256"] == digest(source)
        assert digest(review) == before
        db.execute("INSERT INTO catalog_reference_approvals(approval_sha256,batch_id,approved_by,decision_record,manifest_json) VALUES('test-hash','test-batch','Responsável','Decisão de teste','{}')")
        first = result["candidates"][0]
        db.execute("INSERT INTO catalog_source_references(reference_id,source_sha256,source_file_name,source_table,external_id,source_name,approval_sha256) VALUES(?,?,?,?,?,?,'test-hash')",
                   ('internal-reference-test', digest(source), 'source.db3', first['source_table'], first['external_id'], first['source_name']))
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][1]["candidates"][0]["source_reference"]["reference_id"] == 'internal-reference-test'
        original_id = result["candidates"][0]["candidate_id"]
        note = {"candidate_id": original_id, "source_sha256": digest(source), "note": "Conferir categoria <referência>"}
        h.add_catalog_note(db, {"uid": 2, "role": "student"}, note)
        assert responses[-1][0] == 403
        h.add_catalog_note(db, {"uid": 2, "role": "instructor"}, note)
        assert responses[-1][0] == 403
        h.add_catalog_note(db, {"uid": 1, "role": "instructor"}, dict(note, note=" "))
        assert responses[-1][0] == 400
        h.add_catalog_note(db, {"uid": 1, "role": "instructor"}, dict(note, candidate_id="missing"))
        assert responses[-1][0] == 404
        h.add_catalog_note(db, {"uid": 1, "role": "instructor"}, dict(note, source_sha256="different"))
        assert responses[-1][0] == 409
        h.add_catalog_note(db, {"uid": 1, "role": "instructor"}, note)
        assert responses[-1][0] == 200
        h.add_catalog_note(db, {"uid": 1, "role": "instructor"}, dict(note, note="Segunda observação"))
        assert responses[-1][0] == 200
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        notes = responses[-1][1]["candidates"][0]["review_notes"]
        assert len(notes) == 2 and notes[0]["note"] == note["note"]
        assert notes[0]["author"] == "Teacher" and notes[0]["created_at"]
        assert digest(review) == before
        assert db.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 0
        app.REVIEW_DB_PATH = Path(folder) / "absent.sqlite3"
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][0] == 404 and not app.REVIEW_DB_PATH.exists()
        with closing(sqlite3.connect(app.REVIEW_DB_PATH)) as empty:
            empty.execute("CREATE TABLE unrelated(id INTEGER)")
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][0] == 503
    print("PASS: instructor scope, read-only provenance, evidence matching, invalid evidence fallback and no promotion")
