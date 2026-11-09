"""Store source-verified raw evidence separately from usable platform attributes."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from tools.stage_db3k import digest
from tools.inspect_db3k_domains import inspect_domains

TECHNICAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS catalog_technical_imports (
 evidence_sha256 TEXT PRIMARY KEY,
 source_sha256 TEXT NOT NULL,
 review_sha256 TEXT NOT NULL,
 decision_record TEXT NOT NULL,
 value_count INTEGER NOT NULL CHECK(value_count > 0),
 imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS catalog_technical_values (
 reference_id TEXT NOT NULL REFERENCES catalog_source_references(reference_id),
 field_name TEXT NOT NULL,
 raw_value_json TEXT NOT NULL,
 sqlite_declared_type TEXT NOT NULL,
 unit TEXT CHECK(unit IS NULL),
 validation_status TEXT NOT NULL DEFAULT 'pending_unit_and_semantics'
   CHECK(validation_status='pending_unit_and_semantics'),
 evidence_sha256 TEXT NOT NULL REFERENCES catalog_technical_imports(evidence_sha256),
 PRIMARY KEY(reference_id,field_name)
);
"""


def import_technical_values(source, review, evidence, target, decision_record):
    source, review, evidence, target = [Path(p).resolve(strict=True) for p in
                                       (source, review, evidence, target)]
    if any(target.samefile(p) for p in (source, review, evidence)):
        raise ValueError('O destino deve ser distinto de todas as fontes.')
    if not isinstance(decision_record, str) or not decision_record.strip() or len(decision_record) > 4000:
        raise ValueError('Identifique a decisão de incorporar somente evidências pendentes.')
    hashes = digest(source), digest(review), digest(evidence)
    report = json.loads(evidence.read_text(encoding='utf-8'))
    verified = inspect_domains(source, review)
    for key in ('source', 'review_sha256', 'status', 'literal_records_verified', 'summary', 'candidates'):
        if report.get(key) != verified[key]:
            raise ValueError('As evidências divergem da conferência direta da fonte.')
    with closing(sqlite3.connect(review.as_uri()+'?mode=ro', uri=True)) as staged:
        names = {(t, str(i)): n for t, i, n in staged.execute(
            'SELECT source_table,external_id,source_name FROM candidates')}
    with closing(sqlite3.connect(target.as_uri()+'?mode=ro', uri=True)) as db:
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'catalog_source_references', 'catalog_reference_approvals'}.issubset(tables):
            raise ValueError('Destino não contém referências SISCAN cadastradas.')
        references = {(t, i): (rid, n) for rid, t, i, n in db.execute(
            'SELECT reference_id,source_table,external_id,source_name FROM catalog_source_references WHERE source_sha256=?',
            (hashes[0],))}
    rows = []
    for candidate in verified['candidates']:
        key = candidate['source_table'], candidate['external_id']
        reference = references.get(key)
        if reference is None or reference[1] != names[key]:
            raise ValueError('Candidato sem referência cadastrada correspondente.')
        for field, value in candidate['technical_fields'].items():
            if value['unit'] is not None or value['validation_status'] != 'pending_unit_and_semantics':
                raise ValueError('Somente valores sem unidade confirmada e pendentes são aceitos.')
            rows.append((reference[0], field,
                         json.dumps(value['value'], ensure_ascii=False, allow_nan=False, separators=(',', ':')),
                         value['sqlite_type'], None, 'pending_unit_and_semantics', hashes[2]))
    if not rows:
        raise ValueError('Nenhum valor técnico conferido para incorporar.')
    if hashes != (digest(source), digest(review), digest(evidence)):
        raise RuntimeError('Uma fonte mudou durante a preparação.')
    inserted = 0
    with closing(sqlite3.connect(target.as_uri()+'?mode=rw', uri=True)) as db:
        db.execute('PRAGMA foreign_keys=ON')
        with db:
            # DDL stays in the same transaction as the evidence import.
            db.execute('BEGIN IMMEDIATE')
            for statement in TECHNICAL_SCHEMA.split(';'):
                if statement.strip():
                    db.execute(statement)
            db.execute('INSERT OR IGNORE INTO catalog_technical_imports'
                       '(evidence_sha256,source_sha256,review_sha256,decision_record,value_count) VALUES(?,?,?,?,?)',
                       (hashes[2], hashes[0], hashes[1], decision_record.strip(), len(rows)))
            for row in rows:
                existing = db.execute('SELECT reference_id,field_name,raw_value_json,sqlite_declared_type,unit,validation_status,evidence_sha256 '
                                      'FROM catalog_technical_values WHERE reference_id=? AND field_name=?', row[:2]).fetchone()
                if existing:
                    if existing != row:
                        raise ValueError('Valor existente diverge; nenhuma substituição automática é permitida.')
                    continue
                db.execute('INSERT INTO catalog_technical_values VALUES(?,?,?,?,?,?,?)', row)
                inserted += 1
    return inserted


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Incorpora valores brutos pendentes; não promove atributos utilizáveis.')
    for name in ('source', 'review', 'evidence', 'target'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--decision-record', required=True)
    args = parser.parse_args()
    print(f'Valores técnicos novos: {import_technical_values(args.source, args.review, args.evidence, args.target, args.decision_record)}')
