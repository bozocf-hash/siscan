"""Create a separate review catalogue; never imports into the exercise database."""
import argparse
import hashlib
import json
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

TABLES = ("DataShip", "DataAircraft", "DataSubmarine", "DataGroundUnit")
RAW_CODES = ("Category", "Type", "OperatorCountry", "OperatorService")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def stage(source, output, limit=20):
    source = Path(source).resolve(strict=True)
    output = Path(output).resolve()
    if source == output or output.exists():
        raise ValueError("O destino deve ser um arquivo novo, distinto da fonte.")
    if limit < 1:
        raise ValueError("O limite por tabela deve ser positivo.")
    source_hash = digest(source)
    rows = []
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        for table in TABLES:
            columns = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
            if not {"ID", "Name"}.issubset(columns):
                raise ValueError(f"Tabela {table} ausente ou sem ID/Name.")
            codes = [column for column in RAW_CODES if column in columns]
            selected = ",".join(f'"{column}"' for column in ["ID", "Name", *codes])
            for row in db.execute(f'SELECT {selected} FROM "{table}" ORDER BY "ID" LIMIT ?', (limit,)):
                rows.append((str(uuid.uuid4()), table, str(row[0]), row[1],
                             json.dumps(dict(zip(codes, row[2:])), ensure_ascii=False), "needs_review"))
    if digest(source) != source_hash:
        raise RuntimeError("A fonte mudou durante a leitura; nenhum catálogo foi criado.")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation avoids accidentally replacing an existing review or source.
    with output.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(output)) as target, target:
            target.executescript("""
                CREATE TABLE source (file_name TEXT NOT NULL, sha256 TEXT NOT NULL, read_at TEXT NOT NULL);
                CREATE TABLE candidates (
                    candidate_id TEXT PRIMARY KEY,
                    source_table TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    source_name TEXT,
                    raw_codes_json TEXT NOT NULL,
                    review_status TEXT NOT NULL CHECK(review_status='needs_review'),
                    UNIQUE(source_table,external_id)
                );
            """)
            target.execute("INSERT INTO source VALUES(?,?,?)", (source.name, source_hash, datetime.now(timezone.utc).isoformat()))
            target.executemany("INSERT INTO candidates VALUES(?,?,?,?,?,?)", rows)
    except Exception:
        output.unlink()
        raise
    return {table: sum(row[1] == table for row in rows) for table in TABLES}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepara candidatos DB3K para revisão, sem oficializar dados.")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit-per-table", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(stage(args.source, args.output, args.limit_per_table), ensure_ascii=False))
