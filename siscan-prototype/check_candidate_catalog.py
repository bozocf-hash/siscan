"""Read-only catalogue access checks with isolated fixtures."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import app
from tools.stage_db3k import TABLES, stage, digest

scratch = Path(__file__).resolve().parent.parent / "tmp"
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source = Path(folder) / "source.db3"
    review = Path(folder) / "review.sqlite3"
    with closing(sqlite3.connect(source)) as db, db:
        for table in TABLES:
            db.execute(f'CREATE TABLE "{table}" (ID INTEGER PRIMARY KEY, Name TEXT)')
            db.execute(f'INSERT INTO "{table}" VALUES(1,?)', ("Nome <não executar>",))
    stage(source, review, 1)
    app.REVIEW_DB_PATH = review
    before = digest(review)
    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        db.executescript(app.SCHEMA)
        db.execute("INSERT INTO users(id,username,display_name,role,salt,password_hash) VALUES(1,'teacher','Teacher','instructor',X'00',X'00')")
        db.execute("INSERT INTO exercises(id,code,title,objective) VALUES(1,'X','X','X')")
        db.execute("INSERT INTO assignments VALUES(1,1)")
        h = object.__new__(app.Handler)
        responses = []
        h.send_json = lambda status, body: responses.append((status, body))
        h.candidate_catalog(db, {"uid": 2, "role": "student"})
        assert responses[-1][0] == 403
        h.candidate_catalog(db, {"uid": 2, "role": "instructor"})
        assert responses[-1][0] == 403
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        status, result = responses[-1]
        assert status == 200 and len(result["candidates"]) == 4
        assert all(row["review_status"] == "needs_review" for row in result["candidates"])
        assert result["source"]["sha256"] == digest(source)
        assert digest(review) == before
        assert db.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 0
        app.REVIEW_DB_PATH = Path(folder) / "absent.sqlite3"
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][0] == 404 and not app.REVIEW_DB_PATH.exists()
        with closing(sqlite3.connect(app.REVIEW_DB_PATH)) as empty:
            empty.execute("CREATE TABLE unrelated(id INTEGER)")
        h.candidate_catalog(db, {"uid": 1, "role": "instructor"})
        assert responses[-1][0] == 503
    print("PASS: instructor scope, read-only provenance, pending records, no promotion and missing file")
