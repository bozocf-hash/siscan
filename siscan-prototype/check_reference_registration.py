from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
from tools.stage_db3k import TABLES, stage, digest
from tools.inspect_db3k_domains import inspect_domains
from tools.prepare_approval_packet import prepare_packet
from tools.register_source_references import register_references

scratch = Path(__file__).resolve().parent.parent / "tmp"
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source, review, evidence, packet_file, approval_file, target = [Path(folder)/name for name in ("source.db3", "review.sqlite3", "evidence.json", "packet.json", "approval.json", "siscan.sqlite3")]
    with closing(sqlite3.connect(source)) as db, db:
        for table in TABLES:
            db.execute(f'CREATE TABLE "{table}" (ID INTEGER PRIMARY KEY, Name TEXT)')
            db.execute(f'INSERT INTO "{table}" VALUES(1,?)', ("Sample",))
    stage(source, review, 1)
    evidence.write_text(json.dumps(inspect_domains(source, review)), encoding="utf-8")
    packet = prepare_packet(review, evidence)
    packet_file.write_text(json.dumps(packet), encoding="utf-8")
    approval = {"decision": "approved", "scope": "literal_source_identification_only", "batch_id": packet["batch_id"], "packet_sha256": digest(packet_file), "approved_by": "Responsável pelo projeto", "decision_record": "Decisão explícita de teste", "candidate_ids": [row["candidate_id"] for row in packet["candidates"]]}
    approval_file.write_text(json.dumps(approval), encoding="utf-8")
    hashes = digest(source), digest(review), digest(packet_file)
    assert register_references(packet_file, approval_file, target) == 4
    with closing(sqlite3.connect(target)) as db:
        ids = db.execute("SELECT reference_id FROM catalog_source_references ORDER BY reference_id").fetchall()
        assert len(ids) == 4
        assert db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='assets'").fetchone()[0] == 0
    assert register_references(packet_file, approval_file, target) == 0
    try:
        register_references(packet_file, approval_file, source)
    except ValueError:
        pass
    else:
        raise AssertionError("Original source accepted as write target")
    with closing(sqlite3.connect(target)) as db:
        assert ids == db.execute("SELECT reference_id FROM catalog_source_references ORDER BY reference_id").fetchall()
    approval["scope"] = "operational_attributes"
    approval_file.write_text(json.dumps(approval), encoding="utf-8")
    try:
        register_references(packet_file, approval_file, target)
    except ValueError:
        pass
    else:
        raise AssertionError("Broader approval accepted")
    approval["scope"] = "literal_source_identification_only"
    approval["packet_sha256"] = "wrong"
    approval_file.write_text(json.dumps(approval), encoding="utf-8")
    try:
        register_references(packet_file, approval_file, target)
    except ValueError:
        pass
    else:
        raise AssertionError("Mismatched approval accepted")
    assert hashes == (digest(source), digest(review), digest(packet_file))
    print("PASS: explicit scoped approval, stable reference IDs, idempotency, no asset creation and immutable inputs")
