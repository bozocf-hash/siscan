from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
from tools.stage_db3k import TABLES, stage
from tools.inspect_db3k_domains import inspect_domains
from tools.prepare_approval_packet import prepare_packet, as_markdown

scratch = Path(__file__).resolve().parent.parent / "tmp"
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source, review, evidence = [Path(folder)/name for name in ("source.db3", "review.sqlite3", "evidence.json")]
    with closing(sqlite3.connect(source)) as db, db:
        for table in TABLES:
            db.execute(f'CREATE TABLE "{table}" (ID INTEGER PRIMARY KEY, Name TEXT)')
            db.execute(f'INSERT INTO "{table}" VALUES(1,?)', ("Reference | Test",))
    stage(source, review, 1)
    evidence.write_text(json.dumps(inspect_domains(source, review)), encoding="utf-8")
    packet = prepare_packet(review, evidence)
    assert len(packet["candidates"]) == 4 and packet["status"] == "awaiting_project_owner_review"
    assert all(row["decision"] == "pending" and row["approved_fields"] == [] for row in packet["candidates"])
    assert all(row["proposed_entity_kind"] == "source_reference" for row in packet["candidates"])
    assert packet["permits_allocation"] is False
    assert "Reference \\| Test" in as_markdown(packet)
    assert as_markdown(packet).count("| Pendente |") == 4
    changed = json.loads(evidence.read_text())
    changed["review_sha256"] = "wrong"
    evidence.write_text(json.dumps(changed), encoding="utf-8")
    try:
        prepare_packet(review, evidence)
    except ValueError:
        pass
    else:
        raise AssertionError("Unrelated evidence accepted")
    print("PASS: pending-only decisions, reference-only scope, no allocation and mismatched evidence rejection")
