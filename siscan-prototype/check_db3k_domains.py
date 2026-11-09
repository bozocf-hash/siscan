from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
from tools.stage_db3k import TABLES, stage, digest
from tools.inspect_db3k_domains import inspect_domains

scratch = Path(__file__).resolve().parent.parent / "tmp"
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as folder:
    source, review = Path(folder)/"source.db3", Path(folder)/"review.sqlite3"
    with closing(sqlite3.connect(source)) as db, db:
        for table in TABLES:
            db.execute(f'CREATE TABLE "{table}" (ID INTEGER PRIMARY KEY, Name TEXT, Category INTEGER, OperatorCountry INTEGER, Length REAL, MaxDepth INTEGER)')
            db.execute(f'INSERT INTO "{table}" VALUES(1,?,2001,9999,15.5,0)', ("Sample",))
        db.execute("CREATE TABLE EnumShipCategory(ID INTEGER PRIMARY KEY, Description TEXT)")
        db.execute("INSERT INTO EnumShipCategory VALUES(2001,'Literal category')")
        db.execute("CREATE TABLE EnumOperatorCountry(ID INTEGER PRIMARY KEY, Description TEXT)")
    stage(source, review, 1)
    hashes = digest(source), digest(review)
    report = inspect_domains(source, review)
    assert report["literal_records_verified"] == 4
    assert all(row["literal_source_check"] == "matched" for row in report["candidates"])
    ship = next(row for row in report["candidates"] if row["source_table"] == "DataShip")
    assert ship["domains"]["Category"]["description"] == "Literal category"
    assert ship["domains"]["Category"]["relation_status"] == "nominal_match_without_fk"
    assert ship["domains"]["OperatorCountry"]["status"] == "code_not_found"
    assert ship["technical_fields"]["Length"]["value"] == 15.5
    assert ship["technical_fields"]["Length"]["sqlite_type"] == "REAL"
    assert ship["technical_fields"]["Length"]["unit"] is None
    assert ship["technical_fields"]["MaxDepth"]["value"] == 0
    assert all(field["validation_status"] == "pending_unit_and_semantics" for field in ship["technical_fields"].values())
    aircraft = next(row for row in report["candidates"] if row["source_table"] == "DataAircraft")
    assert aircraft["domains"]["Category"]["status"] == "domain_missing"
    assert hashes == (digest(source), digest(review))
    original_review = review.read_bytes()
    for sql, params in [
        ("UPDATE candidates SET source_name=? WHERE source_table='DataShip'", ("Changed name",)),
        ("UPDATE candidates SET external_id=? WHERE source_table='DataShip'", ("999",)),
        ("UPDATE candidates SET raw_codes_json=? WHERE source_table='DataShip'", ('{"Category":2002,"OperatorCountry":9999}',)),
        ("UPDATE candidates SET raw_codes_json=? WHERE source_table='DataShip'", ('{}',)),
    ]:
        with closing(sqlite3.connect(review)) as db, db:
            db.execute(sql, params)
        try:
            inspect_domains(source, review)
        except ValueError:
            pass
        else:
            raise AssertionError("Tampered candidate was accepted")
        review.write_bytes(original_review)
    with closing(sqlite3.connect(source)) as db, db:
        db.execute("CREATE TABLE added_later(id INTEGER)")
    try:
        inspect_domains(source, review)
    except ValueError:
        pass
    else:
        raise AssertionError("Mismatching source version was accepted")
    print("PASS: literal labels, explicit uncertainty, missing domains, read-only inputs and source mismatch")
