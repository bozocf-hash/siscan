"""Compare every source value with its compiled record; export schema and coverage."""
import argparse
from contextlib import closing
from itertools import zip_longest
import json
from pathlib import Path
import sqlite3
from tools.compile_db3k import quoted, encoded, compact
from tools.stage_db3k import digest


def audit_source(source, compiled, output):
    source,compiled=Path(source).resolve(strict=True),Path(compiled).resolve(strict=True)
    output=Path(output).resolve()
    if output.exists() or output in (source,compiled):
        raise ValueError('O relatório deve ser um novo arquivo distinto das fontes.')
    before=digest(source),digest(compiled)
    inventory=[]
    with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as original, closing(sqlite3.connect(compiled.as_uri()+'?mode=ro',uri=True)) as db:
        original.execute('PRAGMA query_only=ON');db.execute('PRAGMA query_only=ON')
        if db.execute('SELECT sha256 FROM source').fetchone()[0]!=before[0]:
            raise ValueError('A compilação pertence a outra fonte.')
        tables=[r[0] for r in original.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        if set(tables)!={r[0] for r in db.execute('SELECT name FROM tables')}:
            raise ValueError('Inventário de tabelas divergente.')
        for table in tables:
            schema=original.execute('PRAGMA table_info('+quoted(table)+')').fetchall()
            columns=[r[1] for r in schema]
            stored_columns=json.loads(db.execute('SELECT columns_json FROM tables WHERE name=?',(table,)).fetchone()[0])
            if columns!=stored_columns:
                raise ValueError('Colunas divergentes: '+table)
            actual=original.execute('SELECT rowid,* FROM '+quoted(table)+' ORDER BY rowid')
            stored=db.execute('SELECT source_rowid,source_id_json,payload_json FROM records WHERE table_name=? ORDER BY source_rowid',(table,))
            count=0
            for source_row,compiled_row in zip_longest(actual,stored):
                if source_row is None or compiled_row is None:
                    raise ValueError('Quantidade de registros divergente: '+table)
                payload=dict(zip(columns,map(encoded,source_row[1:])))
                if (source_row[0],compact(payload.get('ID')),compact(payload))!=compiled_row:
                    raise ValueError(f'Registro divergente: {table}/{source_row[0]}')
                count+=1
            inventory.append({'table':table,'records':count,'values':count*len(columns),
                              'columns':[dict(zip(('position','name','declared_type','not_null','default','primary_key_position'),r)) for r in schema]})
        statuses=dict(db.execute('SELECT status,count(*) FROM links GROUP BY status'))
        critical={t:db.execute('SELECT row_count FROM tables WHERE name=?',(t,)).fetchone()[0] for t in
                  ('DataSensor','DataFuel','DataPropulsion','DataPropulsionPerformance') if t in tables}
    if before!=(digest(source),digest(compiled)):
        raise RuntimeError('Uma fonte mudou durante a auditoria.')
    report={'source_sha256':before[0],'compiled_sha256':before[1],'status':'all_source_values_matched',
            'tables':len(inventory),'records':sum(t['records'] for t in inventory),
            'values':sum(t['values'] for t in inventory),'critical_tables':critical,
            'link_status_counts':statuses,'inventory':inventory}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','compiled','output'):parser.add_argument(name,type=Path)
    args=parser.parse_args()
    report=audit_source(args.source,args.compiled,args.output)
    print(json.dumps({k:v for k,v in report.items() if k!='inventory'},ensure_ascii=False))
