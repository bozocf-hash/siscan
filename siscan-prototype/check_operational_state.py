"""Estado/adjudicação didática: testes em SQLite descartável."""
import math
import sqlite3
import unittest
from unittest.mock import patch

import engine_units
import operational_state as state
from check_map_groups import seed, TEACHER, BLUE, RED


class ValidationTests(unittest.TestCase):
    def test_faixas_somente_superficie(self):
        for index, expected in [(0,'flutuar'),(39.999,'flutuar'),(40,'navegar'),
                (59.999,'navegar'),(60,'navegar'),(60.001,'combater'),(80,'combater'),(100,'combater')]:
            with self.subTest(index=index):
                self.assertEqual(state.classificar('superficie', index), expected)
                for domain in ('aereo','submarino','terrestre',None):
                    self.assertIsNone(state.classificar(domain,index))
        self.assertIsNone(state.classificar('superficie',None))

    def test_indice_invalido(self):
        for value in (True,False,-1,101,math.nan,math.inf,-math.inf,'80',{},[]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                state.validar_alteracoes({'index_percent':value})

    def test_alteracao_explicita_e_ausencia(self):
        self.assertEqual(state.validar_alteracoes({'index_percent':None}),{'index_percent':None})
        self.assertEqual(state.validar_alteracoes({'lost':False}),{'lost':False})
        for value in ({},{'lost':1},{'lost':None},{'index_percent':80,'role':'instructor'}):
            with self.subTest(value=value),self.assertRaises(ValueError):state.validar_alteracoes(value)

    def test_evidencia_publica_preserva_contrato(self):
        with sqlite3.connect(':memory:') as db:
            db.row_factory=sqlite3.Row;seed(db)
            unit=engine_units.list_units(db,TEACHER)['units'][0]
            self.assertEqual(engine_units.configuration_domain(db,unit)['domain'],'aereo')
            unit['snapshot']['model_id']='inventado'
            self.assertIsNone(engine_units.configuration_domain(db,unit))


if __name__=='__main__':unittest.main()
