"""Planejamento com referência real não concede prontidão física."""
import sqlite3
import unittest
import uuid
from contextlib import closing
from unittest.mock import patch
import app, map_groups, map_units
import planning_catalog
from check_map_groups import seed, TEACHER, BLUE, RED
from unit_groups import RegistroGrupamentos

class PlanningCatalogTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');seed(self.db);self.addCleanup(self.db.close)
        self.body=dict(command_id=str(uuid.uuid4()),table='DataShip',id='1351',team='AZUL',quantity=2)
        self.source=dict(source=dict(sha256='a'*64,file_name='test.db3'),fields=dict(ID=1351,Name='Nome da fonte',YearCommissioned=2000))
        self.reader=patch('planning_catalog.source_catalog.detail',return_value=self.source);self.reader.start();self.addCleanup(self.reader.stop)
    def create(self,**changes):
        return planning_catalog.create(self.db,TEACHER,'unused',dict(self.body,**changes))
    def test_identidades_distintas_sem_duplicar_reenvio(self):
        first=self.create();self.assertEqual(first,self.create());self.assertEqual(len(first['asset_ids']),2)
        self.assertEqual(len(set(first['asset_ids'])),2)
        self.assertEqual(self.db.execute('SELECT count(*) FROM planning_units').fetchone()[0],2)
        self.assertEqual(len([u for u in map_units.listing(self.db,BLUE,'AZUL')['units'] if u['id'] in first['asset_ids']]),2)
        self.assertFalse(any(u['id'] in first['asset_ids'] for u in map_units.listing(self.db,RED,'VERMELHO')['units']))
        with self.assertRaises(ValueError):self.create(quantity=3)
    def test_snapshot_de_planejamento_compoe_grupo_sem_aprovar_calculo(self):
        created=self.create();view=map_groups.view(self.db,BLUE,'AZUL')
        records=[r for r in view['inventory'].values() if r['snapshot']['source_kind']=='catalog_planning']
        self.assertEqual(len(records),2)
        for r in records:
            self.assertFalse(r['snapshot']['official_calculation_ready']);self.assertNotIn('fuel',r['snapshot'])
            self.assertEqual(r['domain'],'naval')
        group=RegistroGrupamentos().criar_grupamento(view['context'],view['inventory'],dict(command_id=str(uuid.uuid4()),designation='GT teste',domain='naval',member_unit_ids=[r['unit_id'] for r in records]))
        self.assertEqual(len(group['members']),2)
    def test_autorizacao_fechamento_e_entrada(self):
        for user in (BLUE,RED,dict(uid=99,role='instructor')):
            with self.assertRaises(PermissionError):planning_catalog.create(self.db,user,'unused',self.body)
        for changes in (dict(quantity=True),dict(quantity=0),dict(quantity=51),dict(table='DataWeapon'),dict(table=[]),dict(team='OUTRO'),dict(id='bad')):
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.create(**changes)
        self.db.execute("UPDATE exercises SET state='closed'")
        with self.assertRaises(ValueError):self.create()
    def test_falha_preserva_todas_as_tabelas(self):
        before=list(self.db.iterdump())
        with patch('planning_catalog.source_catalog.detail',return_value=None):
            with self.assertRaises(ValueError):self.create()
        self.assertEqual(list(self.db.iterdump()),before)
        self.db.execute("CREATE TRIGGER fail_planning BEFORE INSERT ON planning_units BEGIN SELECT RAISE(ABORT,'test'); END")
        before=list(self.db.iterdump())
        with self.assertRaises(sqlite3.IntegrityError):self.create()
        self.assertEqual(list(self.db.iterdump()),before)
    def test_categorias_planejaveis_sem_dominio_inventado(self):
        for table in ('DataAircraft','DataSubmarine','DataGroundUnit','DataFacility','DataSatellite'):
            self.create(command_id=str(uuid.uuid4()),table=table,quantity=1)
        view=map_groups.view(self.db,BLUE,'AZUL')
        planning=[r for r in view['inventory'].values() if r['snapshot']['source_kind']=='catalog_planning']
        self.assertEqual([r['domain'] for r in planning],['aereo'])
    def test_instancias_persistem_sem_entrar_no_motor_sintetico(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import engine_units
        self.create();self.db.commit()
        with TemporaryDirectory() as folder:
            target=sqlite3.connect(str(Path(folder)/'test.sqlite3'))
            self.db.backup(target);target.close()
            with closing(sqlite3.connect(str(Path(folder)/'test.sqlite3'))) as reopened:
                reopened.row_factory=sqlite3.Row
                self.assertEqual(len(planning_catalog.instances(reopened,BLUE,'AZUL')),2)
                self.assertEqual(len(engine_units.list_units(reopened,TEACHER)['units']),2)
                with self.assertRaises(sqlite3.IntegrityError):reopened.execute("UPDATE planning_units SET snapshot_json='{}'")

if __name__=='__main__':unittest.main()
