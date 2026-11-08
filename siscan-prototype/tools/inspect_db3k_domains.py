"""Match literal enum descriptions for review; does not approve semantics."""
import argparse
from collections import Counter
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from tools.stage_db3k import TABLES, digest

DOMAINS = {
    "DataShip": {"Category": "EnumShipCategory", "Type": "EnumShipType"},
    "DataAircraft": {"Category": "EnumAircraftCategory", "Type": "EnumAircraftType"},
    "DataSubmarine": {"Category": "EnumSubmarineCategory", "Type": "EnumSubmarineType"},
    "DataGroundUnit": {"Category": "EnumGroundUnitCategory"},
}


def inspect_domains(source, review):
    source, review = Path(source).resolve(strict=True), Path(review).resolve(strict=True)
    before = digest(source), digest(review)
    with closing(sqlite3.connect(source.as_uri()+"?mode=ro", uri=True)) as db, closing(sqlite3.connect(review.as_uri()+"?mode=ro", uri=True)) as staged:
        db.row_factory = staged.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        staged.execute("PRAGMA query_only=ON")
        provenance = staged.execute("SELECT file_name,sha256,read_at FROM source").fetchone()
        if not provenance or provenance["sha256"] != before[0]:
            raise ValueError("A amostra e a fonte não correspondem ao mesmo hash DB3K.")
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        result = []
        counts = Counter()
        for candidate in staged.execute("SELECT candidate_id,source_table,external_id,raw_codes_json FROM candidates ORDER BY source_table,external_id"):
            table = candidate["source_table"]
            if table not in TABLES:
                raise ValueError("Tabela de origem não permitida.")
            mapping = {**DOMAINS[table], "OperatorCountry": "EnumOperatorCountry", "OperatorService": "EnumOperatorService"}
            domains = {}
            for field, code in json.loads(candidate["raw_codes_json"]).items():
                enum = mapping.get(field)
                record = {"raw_code": code, "enum_table": enum, "description": None,
                          "relation_status": "nominal_match_without_fk"}
                if not enum or enum not in tables:
                    record["status"] = "domain_missing"
                else:
                    columns = {row[1] for row in db.execute(f'PRAGMA table_info("{enum}")')}
                    if not {"ID", "Description"}.issubset(columns):
                        record["status"] = "domain_schema_unrecognized"
                    else:
                        matches = db.execute(f'SELECT Description FROM "{enum}" WHERE ID=?', (code,)).fetchall()
                        if len(matches) == 1:
                            record["description"] = matches[0][0]
                            record["status"] = "literal_code_match"
                        else:
                            record["status"] = "code_not_found" if not matches else "ambiguous_code"
                # A matching value alone is never treated as proof of a relationship.
                fks = db.execute(f'PRAGMA foreign_key_list("{table}")').fetchall()
                if enum and any(row[2] == enum and row[3] == field and row[4] == "ID" for row in fks):
                    record["relation_status"] = "declared_fk"
                counts[record["status"]] += 1
                domains[field] = record
            result.append({"candidate_id": candidate["candidate_id"], "source_table": table,
                           "external_id": candidate["external_id"], "domains": domains})
    if before != (digest(source), digest(review)):
        raise RuntimeError("Uma fonte mudou durante a inspeção; descarte o resultado.")
    return {"source": dict(provenance), "review_sha256": before[1],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "evidence_only_not_approved", "summary": dict(counts), "candidates": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspeciona domínios DB3K sem alterar ou aprovar candidatos.")
    parser.add_argument("source", type=Path)
    parser.add_argument("review", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = inspect_domains(args.source, args.review)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps(report["summary"], ensure_ascii=False))
