"""Paginated reference/evidence consultation, isolated from source files."""
from contextlib import closing
import sqlite3
import app

with closing(sqlite3.connect(':memory:')) as db:
    db.row_factory = sqlite3.Row
    db.executescript(app.SCHEMA)
    db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'teacher','Teacher','instructor',X'00',X'00')")
    db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
    db.execute('INSERT INTO assignments VALUES(1,1)')
    db.execute("INSERT INTO catalog_reference_approvals VALUES('approval','batch','owner','decision','{}',CURRENT_TIMESTAMP)")
    db.execute("INSERT INTO catalog_technical_imports VALUES('evidence','source','review','decision',101,CURRENT_TIMESTAMP)")
    for n in range(101):
        table = 'DataAircraft' if n < 100 else 'DataGroundUnit'
        name = 'Record <unsafe> unique' if n == 0 else f'Record {n}'
        db.execute('INSERT INTO catalog_source_references VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)',
                   (f'ref-{n}', 'source', 'fixture.db3', table, str(n), name, 'approval'))
        value = ('0', 'null', '-3.26')[n % 3]
        db.execute('INSERT INTO catalog_technical_values VALUES(?,?,?,?,?,?,?)',
                   (f'ref-{n}', 'Length', value, 'REAL', None, 'pending_unit_and_semantics', 'evidence'))
    db.execute("INSERT INTO catalog_review_notes(exercise_id,source_sha256,candidate_id,author_id,note) VALUES(1,'source','legacy-candidate',1,'Preserve this note')")
    handler = object.__new__(app.Handler)
    responses = []
    handler.send_json = lambda status, data: responses.append((status, data))
    teacher = {'uid': 1, 'role': 'instructor'}

    def get(query='', user=teacher):
        handler.reference_catalog(db, user, query)
        return responses[-1]

    before = db.total_changes
    for user in ({'uid': 1, 'role': 'student'}, {'uid': 1, 'role': 'evaluator'}, {'uid': 2, 'role': 'instructor'}):
        assert get(user=user)[0] == 403
    status, first = get()
    assert status == 200 and first['total'] == 101 and first['page'] == 1 and first['pages'] == 3
    assert len(first['references']) == first['page_size'] == 50
    assert first['references'][0]['reference_id'] == 'ref-0'
    fields = first['references'][0]['technical_fields']
    assert fields[0]['value'] == 0 and fields[0]['unit'] is None
    assert fields[0]['validation_status'] == 'pending_unit_and_semantics'
    assert fields[0]['evidence_sha256'] == 'evidence'
    second = get('page=2')[1]
    assert not {r['reference_id'] for r in first['references']} & {r['reference_id'] for r in second['references']}
    last = get('page=999')[1]
    assert last['page'] == 3 and len(last['references']) == 1
    assert get('table=DataGroundUnit')[1]['total'] == 1
    assert get('q=100')[1]['references'][0]['external_id'] == '100'
    assert get('q=1')[1]['total'] == 1
    assert get('q=%3Cunsafe%3E')[1]['references'][0]['source_name'] == 'Record <unsafe> unique'
    assert get('q=does-not-exist')[1]['references'] == []
    assert get('q=%25')[1]['total'] == 0  # Literal %, never a wildcard.
    for query in ('page=0', 'page=-1', 'page=nope', 'page=1&page=2', 'table=not-a-table', 'q='+('a'*121)):
        assert get(query)[0] == 400
    assert get('q=1')[1]['references'][0]['technical_fields'][0]['value'] is None
    assert get('q=2')[1]['references'][0]['technical_fields'][0]['value'] == -3.26
    assert db.total_changes == before
    assert db.execute('SELECT note FROM catalog_review_notes').fetchone()[0] == 'Preserve this note'
    assert db.execute('SELECT count(*) FROM assets').fetchone()[0] == 0
    db.execute("UPDATE catalog_technical_values SET raw_value_json='invalid' WHERE reference_id='ref-0'")
    assert get()[0] == 503
    print('PASS: authorization, stable pagination, filters, literal search, pending evidence, NULL/zero/sign, legacy notes and read-only access')
