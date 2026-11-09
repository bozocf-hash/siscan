"""Register owner-approved literal references; never creates allocatable assets."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import uuid
from tools.stage_db3k import TABLES, digest

REFERENCE_SCHEMA = """
CREATE TABLE IF NOT EXISTS catalog_reference_approvals (
 approval_sha256 TEXT PRIMARY KEY, batch_id TEXT NOT NULL,
 approved_by TEXT NOT NULL, decision_record TEXT NOT NULL,
 manifest_json TEXT NOT NULL, recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS catalog_source_references (
 reference_id TEXT PRIMARY KEY, source_sha256 TEXT NOT NULL,
 source_file_name TEXT NOT NULL, source_table TEXT NOT NULL,
 external_id TEXT NOT NULL, source_name TEXT,
 approval_sha256 TEXT NOT NULL REFERENCES catalog_reference_approvals(approval_sha256),
 registered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(source_sha256,source_table,external_id)
);
"""


def register_references(packet_file, approval_file, target):
    packet_file, approval_file = Path(packet_file).resolve(strict=True), Path(approval_file).resolve(strict=True)
    target = Path(target).resolve()
    if target in (packet_file, approval_file):
        raise ValueError("O destino deve ser distinto dos documentos de entrada.")
    packet_hash, approval_hash = digest(packet_file), digest(approval_file)
    packet = json.loads(packet_file.read_text(encoding="utf-8"))
    approval = json.loads(approval_file.read_text(encoding="utf-8"))
    if approval.get("decision") != "approved" or approval.get("scope") != "literal_source_identification_only" or approval.get("packet_sha256") != packet_hash or approval.get("batch_id") != packet.get("batch_id"):
        raise ValueError("Aprovação ausente, divergente ou fora do escopo de identificação literal.")
    if not isinstance(approval.get("approved_by"), str) or not approval["approved_by"].strip() or not isinstance(approval.get("decision_record"), str) or not approval["decision_record"].strip():
        raise ValueError("A aprovação deve identificar responsável e registro da decisão.")
    if packet.get("scope") != "literal_source_identification_only" or packet.get("permits_allocation") is not False:
        raise ValueError("Proposta de escopo incompatível.")
    candidates = {row["candidate_id"]: row for row in packet["candidates"]}
    selected = approval.get("candidate_ids")
    if not isinstance(selected, list) or not selected or any(not isinstance(value, str) for value in selected) or len(set(selected)) != len(selected) or not set(selected).issubset(candidates):
        raise ValueError("Seleção aprovada inválida.")
    for identifier in selected:
        row = candidates[identifier]
        if row.get("proposed_entity_kind") != "source_reference" or row.get("source_table") not in TABLES:
            raise ValueError("Registro não corresponde a referência de fonte permitida.")
    if target.exists():
        with closing(sqlite3.connect(target.as_uri()+"?mode=ro", uri=True)) as check:
            tables = {row[0] for row in check.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if tables and not ({"users", "exercises"}.issubset(tables) or {"catalog_source_references", "catalog_reference_approvals"}.issubset(tables)):
                raise ValueError("Destino existente não é um banco SISCAN reconhecido; escrita recusada.")
    if packet_hash != digest(packet_file) or approval_hash != digest(approval_file):
        raise RuntimeError("Os documentos mudaram durante a leitura.")
    target.parent.mkdir(parents=True, exist_ok=True)
    inserted = 0
    with closing(sqlite3.connect(target)) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript(REFERENCE_SCHEMA)
        with db:
            db.execute("INSERT OR IGNORE INTO catalog_reference_approvals(approval_sha256,batch_id,approved_by,decision_record,manifest_json) VALUES(?,?,?,?,?)",
                       (approval_hash, packet["batch_id"], approval["approved_by"], approval["decision_record"], json.dumps(approval, ensure_ascii=False)))
            for identifier in selected:
                row = candidates[identifier]
                key = (packet["source"]["sha256"], row["source_table"], row["external_id"])
                existing = db.execute("SELECT source_name FROM catalog_source_references WHERE source_sha256=? AND source_table=? AND external_id=?", key).fetchone()
                if existing:
                    if existing[0] != row["source_name"]:
                        raise ValueError("Referência existente tem nome divergente; operação cancelada.")
                    continue
                db.execute("INSERT INTO catalog_source_references(reference_id,source_sha256,source_file_name,source_table,external_id,source_name,approval_sha256) VALUES(?,?,?,?,?,?,?)",
                           (str(uuid.uuid4()), key[0], packet["source"]["file_name"], key[1], key[2], row["source_name"], approval_hash))
                inserted += 1
    return inserted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Registra referências literais com decisão explícita do responsável; não cria meios alocáveis.")
    parser.add_argument("packet", type=Path)
    parser.add_argument("approval", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    print(f"Referências novas: {register_references(args.packet, args.approval, args.target)}")
