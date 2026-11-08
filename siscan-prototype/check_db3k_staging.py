import sqlite3
import tempfile
from pathlib import Path
from contextlib import closing
from tools.stage_db3k import TABLES, digest, stage

scratch = Path(__file__).resolve().parent.parent / "tmp"
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source = Path(folder) / "source.db3"
    output = Path(folder) / "review.sqlite3"
    with closing(sqlite3.connect(source)) as db, db:
        for table in TABLES:
            db.execute(f'CREATE TABLE "{table}" (ID INTEGER PRIMARY KEY, Name TEXT, Category INTEGER)')
            db.execute(f'INSERT INTO "{table}" VALUES(1,?,1234)', ("Meio de teste",))
    before = digest(source)
    counts = stage(source, output, 1)
    assert sum(counts.values()) == 4 and digest(source) == before
    with closing(sqlite3.connect(output)) as db:
        assert db.execute("SELECT COUNT(*) FROM candidates WHERE review_status='needs_review'").fetchone()[0] == 4
        assert db.execute("SELECT sha256 FROM source").fetchone()[0] == before
    try:
        stage(source, output, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Existing output was not protected")
    try:
        stage(source, source, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Source was not protected")
    print("PASS: read-only source, provenance, review status and overwrite protection")
