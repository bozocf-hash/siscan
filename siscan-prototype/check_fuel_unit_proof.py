"""Prova documental delimitada, sem liberação operacional dos dados."""
from copy import deepcopy
from decimal import Decimal
import unittest
from fuel_unit_proof import compare_point,fuel_kind,mass_to_kg,SOURCE_SHA256,IMAGE_SHA256


class FuelUnitProofTests(unittest.TestCase):
    def engine(self):return dict(ID=734,Name='2x F119-PW-100',Type=2002,NumberOfEngines=2,ThrustPerEngineMilitary=11350,SFCMilitary=0.76,ThrustPerEngineAfterburner=16798,SFCAfterburner=1.9)
    def point(self):return dict(ID=734,AltitudeBand=1,Throttle=3,AltitudeMin=0,AltitudeMax=3657.6,Speed=650,Consumption=267.47)
    def compare(self,point=None,**kw):return compare_point(self.engine(),point or self.point(),source_sha256=kw.get('source_sha256',SOURCE_SHA256),image_sha256=kw.get('image_sha256',IMAGE_SHA256))

    def test_correspondencia_exata_delimita_unidades_e_nao_homologa_motor(self):
        p=self.point();before=deepcopy(p);r=self.compare(p)
        self.assertTrue(r['all_fields_match']);self.assertEqual(r['measurements']['Consumption']['unit'],'kg/min')
        self.assertEqual(r['measurements']['Speed']['unit'],'kn');self.assertEqual(r['measurements']['AltitudeMax']['unit'],'m')
        self.assertEqual(r['rate_basis'],'modeled_propulsion_set');self.assertEqual(r['additional_engine_multiplier'],1)
        self.assertFalse(r['calculation_ready']);self.assertEqual(p,before)

    def test_hashes_divergentes_nao_produzem_unidades_comprovadas(self):
        for kwargs in [{'source_sha256':'0'*64},{'image_sha256':'0'*64}]:
            r=self.compare(**kwargs);self.assertFalse(r['all_fields_match']);self.assertTrue(all(m['unit'] is None for m in r['measurements'].values()))

    def test_diferenca_preservada_por_campo_sem_tolerancia_inventada(self):
        p=self.point();p['Consumption']=267.48;r=self.compare(p)
        self.assertFalse(r['all_fields_match']);self.assertIsNone(r['measurements']['Consumption']['unit']);self.assertEqual(r['measurements']['Consumption']['raw_value'],267.48)
        self.assertEqual(r['measurements']['Speed']['unit'],'kn')

    def test_limite_superior_nao_esconde_diferenca_no_inferior(self):
        p=dict(self.point(),AltitudeBand=2,AltitudeMin=3657.6,AltitudeMax=7315.2,Speed=750,Consumption=250.53)
        r=self.compare(p);self.assertFalse(r['all_fields_match']);self.assertIsNone(r['measurements']['AltitudeMin']['unit'])
        self.assertIsNone(r['measurements']['Consumption']['unit']);self.assertEqual(r['measurements']['Consumption']['document_value'],250.54)

    def test_identidade_e_faixa_fora_da_amostra_nao_herdam_prova(self):
        p=dict(self.point(),ID=34);r=self.compare(p);self.assertFalse(r['sample_applicable'])
        engine=self.engine();engine['NumberOfEngines']=1
        r=compare_point(engine,self.point(),source_sha256=SOURCE_SHA256,image_sha256=IMAGE_SHA256)
        self.assertFalse(r['sample_applicable'])

    def test_conversoes_explicitas_sem_densidade_padrao(self):
        self.assertEqual(mass_to_kg('4.7','t'),Decimal('4700'))
        self.assertEqual(mass_to_kg('10860','lb'),Decimal('4926.0131382'))
        self.assertEqual(mass_to_kg(0,'kg'),0)
        for value,unit in [(1,'L'),(1,'gal'),(True,'kg'),(-1,'kg'),('NaN','kg'),('Infinity','kg')]:
            with self.subTest(value=value,unit=unit):
                with self.assertRaises(ValueError):mass_to_kg(value,unit)

    def test_bateria_aip_tempo_e_combustivel_nao_viram_mesma_grandeza(self):
        self.assertEqual(fuel_kind(2001)['quantity_kind'],'liquid_fuel')
        self.assertEqual(fuel_kind(4001)['quantity_kind'],'electrical_resource')
        self.assertEqual(fuel_kind(4002)['quantity_kind'],'aip_resource')
        self.assertEqual(fuel_kind(5003)['quantity_kind'],'duration')
        self.assertEqual(fuel_kind(3003)['quantity_kind'],'combustion_resource_phase_unconfirmed')
        self.assertTrue(all(fuel_kind(k)['sql_unit'] is None for k in [2001,3001,4001,4002,5003,9999]))
        self.assertEqual(fuel_kind(9999)['quantity_kind'],'unknown')


if __name__=='__main__':unittest.main()
