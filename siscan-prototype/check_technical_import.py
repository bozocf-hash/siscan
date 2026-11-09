from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
from tools.stage_db3k import TABLES, stage, digest
from tools.inspect_db3k_domains import inspect_domains
from tools.register_source_references import REFERENCE_SCHEMA
from tools.import_technical_values import import_technical_values

scratch = Path(__file__).resolve().parent.parent / 'tmp'
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source, review, evidence, target = [Path(folder)/n for n in
                                       ('source.db3', 'review.sqlite3', 'evidence.json', 'siscan.sqlite3')]
    with closing(sqlite3.connect(source)) as db, db:
        for table in TABLES:
            db.execute(f'CREATE TABLE {table}(ID INTEGER PRIMARY KEY, Name TEXT, Length REAL, Height REAL, MaxDepth INTEGER, Mass REAL)')
            db.execute(f'INSERT INTO {table} VALUES(1,?,NULL,0,-320,3.26)', ('Sample',))
    stage(source, review, 1)
    report = inspect_domains(source, review)
    evidence.write_text(json.dumps(report), encoding='utf-8')
    with closing(sqlite3.connect(target)) as db, db:
        db.executescript(REFERENCE_SCHEMA)
        db.execute("INSERT INTO catalog_reference_approvals VALUES('approval','batch','owner','decision','{}',CURRENT_TIMESTAMP)")
        for table in TABLES:
            db.execute('INSERT INTO catalog_source_references VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)',
                       (table, digest(source), source.name, table, '1', 'Sample', 'approval'))
        db.execute('CREATE TABLE assets(id INTEGER PRIMARY KEY)')
        db.execute('INSERT INTO assets VALUES(7)')
    hashes = digest(source), digest(review), digest(evidence)

    def rejected():
        try:
            import_technical_values(source, review, evidence, target, 'Decision from owner')
        except ValueError:
            return
        raise AssertionError('Invalid technical evidence accepted')

    for change in ('value', 'unit', 'validation_status'):
        bad = json.loads(json.dumps(report))
        bad['candidates'][0]['technical_fields']['Mass'][change] = {
            'value': 999, 'unit': 'kg', 'validation_status': 'approved'}[change]
        evidence.write_text(json.dumps(bad), encoding='utf-8')
        rejected()
    evidence.write_text(json.dumps(report), encoding='utf-8')
    with closing(sqlite3.connect(target)) as db, db:
        db.execute("DELETE FROM catalog_source_references WHERE reference_id='DataShip'")
    rejected()
    with closing(sqlite3.connect(target)) as db, db:
        assert db.execute("SELECT count(*) FROM sqlite_master WHERE name='catalog_technical_values'").fetchone()[0] == 0
        db.execute('INSERT INTO catalog_source_references VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)',
                   ('DataShip', digest(source), source.name, 'DataShip', '1', 'Sample', 'approval'))
    assert import_technical_values(source, review, evidence, target, 'Decision from owner') == 16
    assert import_technical_values(source, review, evidence, target, 'Decision from owner') == 0
    with closing(sqlite3.connect(target)) as db:
        rows = {r[0]: json.loads(r[1]) for r in db.execute("SELECT field_name,raw_value_json FROM catalog_technical_values WHERE reference_id='DataShip'")}
        assert rows == {'Length': None, 'Height': 0.0, 'MaxDepth': -320, 'Mass': 3.26}
        assert db.execute('SELECT count(*) FROM catalog_technical_values WHERE unit IS NOT NULL OR validation_status<>?', ('pending_unit_and_semantics',)).fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM catalog_technical_imports').fetchone()[0] == 1
        assert db.execute('SELECT * FROM assets').fetchall() == [(7,)]
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
        for sql in ("UPDATE catalog_technical_values SET unit='m'", "UPDATE catalog_technical_values SET validation_status='approved'"):
            try:
                db.execute(sql)
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError('Pending evidence can be promoted in place')
        db.rollback()
    with closing(sqlite3.connect(target)) as db, db:
        db.execute("DELETE FROM catalog_technical_values WHERE reference_id='DataAircraft' AND field_name='Length'")
        db.execute("UPDATE catalog_technical_values SET raw_value_json='999' WHERE reference_id='DataShip' AND field_name='Mass'")
    rejected()
    with closing(sqlite3.connect(target)) as db:
        assert db.execute('SELECT count(*) FROM catalog_technical_values').fetchone()[0] == 15
        assert db.execute("SELECT count(*) FROM catalog_technical_values WHERE reference_id='DataAircraft' AND field_name='Length'").fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM catalog_technical_imports').fetchone()[0] == 1
    try:
        import_technical_values(source, review, evidence, source, 'Decision from owner')
    except ValueError:
        pass
    else:
        raise AssertionError('Original source accepted as target')
    assert hashes == (digest(source), digest(review), digest(evidence))
    print('PASS: exact raw values, NULL/zero/sign, pending constraints, evidence checks, references, idempotency and preserved inputs/assets')
