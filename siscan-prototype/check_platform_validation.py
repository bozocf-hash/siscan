"""Auditoria em fontes sintéticas; nenhum dado DB3K é publicado na fixture."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from tools.compile_db3k import compile_source
from tools.stage_db3k import digest
from tools.validate_platform_data import validate_platform_data,diagnose_fields


class PlatformValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name);self.source=self.folder/'source.db3';self.compiled=self.folder/'compiled.sqlite3'
        with closing(sqlite3.connect(self.source)) as db,db:
            db.executescript('''
            CREATE TABLE DataAircraft(ID INTEGER PRIMARY KEY,Name TEXT);
            CREATE TABLE DataShip(ID INTEGER PRIMARY KEY,Name TEXT);
            CREATE TABLE DataFacility(ID INTEGER PRIMARY KEY,Name TEXT);
            CREATE TABLE DataAircraftSensors(ID INTEGER REFERENCES DataAircraft(ID),ComponentID INTEGER);
            CREATE TABLE DataSensor(ID INTEGER PRIMARY KEY,Name TEXT,RangeMin REAL,RangeMax REAL,MasqueradeAs INTEGER);
            CREATE TABLE DataSensorSensorGroups(ID INTEGER REFERENCES DataSensor(ID),ComponentID INTEGER);
            CREATE TABLE DataAircraftLoadouts(ID INTEGER REFERENCES DataAircraft(ID),ComponentID INTEGER);
            CREATE TABLE DataLoadout(ID INTEGER PRIMARY KEY,Name TEXT);
            CREATE TABLE DataLoadoutWeapons(ID INTEGER REFERENCES DataLoadout(ID),ComponentID INTEGER);
            CREATE TABLE DataWeaponRecord(ID INTEGER PRIMARY KEY,ComponentID INTEGER,DefaultLoad INTEGER,MaxLoad INTEGER,Multiple INTEGER);
            CREATE TABLE DataWeapon(ID INTEGER PRIMARY KEY,Name TEXT,AirPoK REAL,Weight REAL);
            CREATE TABLE DataAircraftFuel(ID INTEGER REFERENCES DataAircraft(ID),ComponentID INTEGER);
            CREATE TABLE DataWeaponFuel(ID INTEGER REFERENCES DataWeapon(ID),ComponentID INTEGER);
            CREATE TABLE DataFuel(ID INTEGER PRIMARY KEY,Type INTEGER,Capacity REAL);
            CREATE TABLE EnumFuelType(ID INTEGER PRIMARY KEY,Description TEXT);
            CREATE TABLE DataAircraftPropulsion(ID INTEGER REFERENCES DataAircraft(ID),ComponentID INTEGER);
            CREATE TABLE DataPropulsion(ID INTEGER PRIMARY KEY,Name TEXT,Type INTEGER,NumberOfEngines REAL);
            CREATE TABLE DataPropulsionPerformance(ID INTEGER REFERENCES DataPropulsion(ID),AltitudeBand INTEGER,Throttle INTEGER,Speed REAL,AltitudeMin REAL,AltitudeMax REAL,Consumption REAL);
            INSERT INTO DataAircraft VALUES(1,'=Nome sintético'),(2,'Sem registros');
            INSERT INTO DataShip VALUES(1,'Outro domínio');
            INSERT INTO DataFacility VALUES(1,'Fixa');
            INSERT INTO DataAircraftSensors VALUES(1,10),(1,10),(1,999),(999,10);
            INSERT INTO DataSensor VALUES(10,'Radar sintético',0,50,11),(11,'Referência de aparência',0,0,11);
            INSERT INTO DataSensorSensorGroups VALUES(10,10);
            INSERT INTO DataAircraftLoadouts VALUES(1,20),(1,21);
            INSERT INTO DataLoadout VALUES(20,'Alternativa A'),(21,'Alternativa B');
            INSERT INTO DataLoadoutWeapons VALUES(20,30),(21,31);
            INSERT INTO DataWeaponRecord VALUES(30,40,2,4,1),(31,40,0,1,2);
            INSERT INTO DataWeapon VALUES(40,'Arma sintética',85,0);
            INSERT INTO DataAircraftFuel VALUES(1,50);
            INSERT INTO DataWeaponFuel VALUES(40,51);
            INSERT INTO DataFuel VALUES(50,2001,0),(51,3001,20);
            INSERT INTO EnumFuelType VALUES(2001,'Aviation'),(3001,'Outro combustível');
            INSERT INTO DataAircraftPropulsion VALUES(1,60);
            INSERT INTO DataPropulsion VALUES(60,'Propulsor sintético',2001,2);
            INSERT INTO DataPropulsionPerformance VALUES(60,1,1,100,0,1000,2),(60,2,2,0,1000,2000,0);
            ''')
        compile_source(self.source,self.compiled)

    def run_audit(self):return validate_platform_data(self.source,self.compiled,self.folder/'report')
    def lines(self,name):return [json.loads(line) for line in (self.folder/'report'/name).read_text(encoding='utf-8').splitlines()]

    def test_todas_plataformas_alternativas_instalacoes_e_combustivel_separados(self):
        before=digest(self.source),digest(self.compiled);report=self.run_audit()
        self.assertEqual(report['platform_count'],4);self.assertFalse(report['calculation_ready'])
        p=next(p for p in self.lines('platforms.jsonl') if p['table']=='DataAircraft' and p['id']==1)
        self.assertEqual(p['direct_installation_counts']['DataAircraftSensors'],3)
        self.assertEqual(p['direct_components']['DataSensor'],[10])
        self.assertEqual(p['reachable_components']['DataLoadout'],[20,21])
        self.assertEqual(p['reachable_components']['DataWeapon'],[40])
        self.assertEqual(p['direct_components']['DataFuel'],[50])
        self.assertEqual(p['chain_components']['DataFuel'],[51])
        self.assertEqual(p['direct_performance_rows'],2)
        self.assertIsNone(p['current_fuel']);self.assertIsNone(p['average_consumption'])
        self.assertEqual(before,(digest(self.source),digest(self.compiled)))
        self.assertNotIn(11,p['reachable_components']['DataSensor'])  # Masquerade is not an installation.

    def test_lacunas_zeros_orfaos_e_evidencia_nao_promovidos(self):
        result=self.run_audit()
        self.assertGreater(result['link_status_counts'].get('missing',0),0)
        components=self.lines('components.jsonl');fuel=next(c for c in components if c['table']=='DataFuel' and c['id']==50)
        self.assertEqual(fuel['fields']['Capacity'],0);self.assertFalse(fuel['calculation_ready'])
        p=next(p for p in self.lines('platforms.jsonl') if p['table']=='DataAircraft' and p['id']==2)
        self.assertEqual(p['source_presence']['DataFuel'],'no_direct_rows_in_source')
        self.assertIsNone(p['current_fuel'])
        weapon=next(c for c in components if c['table']=='DataWeapon')
        self.assertEqual(weapon['fields']['AirPoK'],85)
        evidence=json.loads((self.folder/'report/field_evidence.json').read_text(encoding='utf-8'))
        self.assertTrue(all(not v['calculation_ready'] for e in evidence.values() for v in e.values()))

    def test_vinculo_adulterado_ou_ausente_nao_gera_relatorio_completo(self):
        with closing(sqlite3.connect(self.compiled)) as db,db:
            rule=db.execute("SELECT id FROM relations WHERE from_table='DataAircraftSensors' AND from_column='ComponentID'").fetchone()[0]
            db.execute('DELETE FROM links WHERE relation_id=? AND from_rowid=1',(rule,))
        with self.assertRaisesRegex(ValueError,'[Vv]ínculo'):self.run_audit()
        self.assertFalse((self.folder/'report/summary.json').exists())

    def test_literal_adulterado_interrompe(self):
        with closing(sqlite3.connect(self.compiled)) as db,db:
            db.execute("UPDATE records SET payload_json=json_set(payload_json,'$.Capacity',999) WHERE table_name='DataFuel' AND source_rowid=50")
        with self.assertRaises(ValueError):self.run_audit()
        self.assertFalse((self.folder/'report/summary.json').exists())

    def test_limites_e_quantidades_sem_reparo_ou_conversao(self):
        self.assertTrue(diagnose_fields('DataSensor',dict(RangeMin=20,RangeMax=10)))
        self.assertTrue(diagnose_fields('DataWeapon',dict(AirPoK=101,Weight=None)))
        self.assertTrue(diagnose_fields('DataWeaponRecord',dict(DefaultLoad=5,MaxLoad=2,Multiple=0)))
        self.assertTrue(diagnose_fields('DataPropulsionPerformance',dict(Speed=10,Consumption=-1,AltitudeMin=2,AltitudeMax=1)))

    def test_destino_exclusivo_e_csv_seguro(self):
        self.run_audit()
        with self.assertRaises(FileExistsError):self.run_audit()
        text=(self.folder/'report/platforms.csv').read_text(encoding='utf-8-sig')
        self.assertIn("'=Nome sintético",text)


if __name__=='__main__':unittest.main()
