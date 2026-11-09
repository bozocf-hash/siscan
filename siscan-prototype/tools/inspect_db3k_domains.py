"""Match literal enum descriptions for review; does not approve semantics."""
import argparse
from collections import Counter
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from tools.stage_db3k import TABLES, RAW_CODES, digest

DOMAINS = {
    "DataShip": {"Category": "EnumShipCategory", "Type": "EnumShipType"},
    "DataAircraft": {"Category": "EnumAircraftCategory", "Type": "EnumAircraftType"},
    "DataSubmarine": {"Category": "EnumSubmarineCategory", "Type": "EnumSubmarineType"},
    "DataGroundUnit": {"Category": "EnumGroundUnitCategory"},
}
TECHNICAL_FIELDS = ("Length", "Beam", "Draft", "Height", "Span", "WeightEmpty", "WeightMax",
                    "DisplacementEmpty", "DisplacementStandard", "DisplacementFull", "MaxDepth",
                    "Area", "Width", "MastHeight", "Mass", "Crew")


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
        for candidate in staged.execute("SELECT candidate_id,source_table,external_id,source_name,raw_codes_json FROM candidates ORDER BY source_table,external_id"):
            table = candidate["source_table"]
            if table not in TABLES:
                raise ValueError("Tabela de origem não permitida.")
            source_columns = {row[1]: row[2] for row in db.execute(f'PRAGMA table_info("{table}")')}
            code_fields = [field for field in RAW_CODES if field in source_columns]
            technical_names = [field for field in TECHNICAL_FIELDS if field in source_columns]
            fields = ",".join(f'"{field}"' for field in ["ID", "Name", *code_fields, *technical_names])
            original = db.execute(f'SELECT {fields} FROM "{table}" WHERE ID=?', (candidate["external_id"],)).fetchone()
            raw_codes = json.loads(candidate["raw_codes_json"])
            if not original or str(original["ID"]) != candidate["external_id"] or original["Name"] != candidate["source_name"]:
                raise ValueError(f"Identificação do candidato diverge da fonte: {table}/{candidate['external_id']}")
            expected_codes = {field: original[field] for field in code_fields}
            if not isinstance(raw_codes, dict) or json.dumps(raw_codes, sort_keys=True) != json.dumps(expected_codes, sort_keys=True):
                raise ValueError(f"Códigos do candidato divergem da fonte: {table}/{candidate['external_id']}")
            mapping = {**DOMAINS[table], "OperatorCountry": "EnumOperatorCountry", "OperatorService": "EnumOperatorService"}
            domains = {}
            for field, code in raw_codes.items():
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
                           "external_id": candidate["external_id"], "literal_source_check": "matched", "domains": domains,
                           "technical_fields": {field: {"value": original[field], "sqlite_type": source_columns[field], "unit": None,
                                                        "validation_status": "pending_unit_and_semantics"} for field in technical_names}})
    if before != (digest(source), digest(review)):
        raise RuntimeError("Uma fonte mudou durante a inspeção; descarte o resultado.")
    return {"source": dict(provenance), "review_sha256": before[1],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "evidence_only_not_approved", "literal_records_verified": len(result), "summary": dict(counts), "candidates": result}


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
