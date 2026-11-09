"""Guard the distinction between raw values, display evidence and motor inputs."""
from technical_units import describe_fields, annotate_bundle

air=describe_fields('DataAircraft',{'ID':3,'Length':15.2,'WeightEmpty':6190,'Area':0})
assert air['Length']['display_unit']=='m'
assert air['WeightEmpty']['display_unit']=='kg'
assert air['Area']['unit'] is None
assert not any(info['calculation_ready'] for info in air.values())
assert describe_fields('DataGroundUnit',{'Area':25.96})['Area']['unit'] is None
assert describe_fields('DataSensor',{'RangeMax':35.5})['RangeMax']['candidate_unit']=='NM'
assert 'Comments' not in describe_fields('DataSensor',{'Comments':None})
assert describe_fields('DataPropulsion',{'NumberOfEngines':2})['NumberOfEngines']['display_unit']=='motores'
assert describe_fields('DataFuel',{'Type':2001,'Capacity':None})['Capacity']['candidate_unit']=='kg'
assert describe_fields('DataFuel',{'Type':2001,'Capacity':1490})['Capacity']['candidate_unit']=='kg'
for kind in [3001,3003,4001,4002,4003,5001,5002,5003]:
    info=describe_fields('DataFuel',{'Type':kind,'Capacity':15000})['Capacity']
    assert info['unit'] is None and info.get('candidate_unit') is None

nodes=[
 {'key':'ship','table':'DataShip','id':3,'rowid':1,'fields':{'ID':3}},
 {'key':'installation','table':'DataShipPropulsion','id':3,'rowid':1,'fields':{'ID':3,'ComponentID':50}},
 {'key':'engine','table':'DataPropulsion','id':50,'rowid':1,'fields':{'ID':50,'Type':2005,'SFCMilitary':0.464}},
 {'key':'profile','table':'DataPropulsionPerformance','id':50,'rowid':1,'fields':{'ID':50,'Throttle':2,'Speed':140,'AltitudeBand':1,'AltitudeMin':0.,'AltitudeMax':3657.6,'Consumption':7.75}},
 {'key':'battery-engine','table':'DataPropulsion','id':70,'rowid':2,'fields':{'ID':70,'Type':4001}},
 {'key':'battery-profile','table':'DataPropulsionPerformance','id':70,'rowid':2,'fields':{'ID':70,'Throttle':2,'Speed':10,'Consumption':0}},
]
links=[{'source':'installation','field':'ID','target':'ship'},
       {'source':'installation','field':'ComponentID','target':'engine'},
       {'source':'profile','field':'ID','target':'engine'},
       {'source':'battery-profile','field':'ID','target':'battery-engine'}]
profiles=annotate_bundle(nodes,links,'ship')
assert nodes[3]['measurements']['Consumption']['candidate_unit']=='kg/min'
assert nodes[3]['fields']['Consumption']==7.75
assert nodes[3]['measurements']['Consumption']['unit'] is None
assert nodes[5]['measurements']['Consumption'].get('candidate_unit') is None
assert nodes[5]['fields']['Consumption']==0
assert nodes[2]['measurements']['SFCMilitary']['unit'] is None
assert len(profiles)==2
assert profiles[0]['direct'] and len(profiles[0]['points'])==1
assert not profiles[1]['direct']
assert all(not p['calculation_ready'] for p in profiles)
assert profiles[0]['points'][0]['source_key']=='profile'
print('PASS: scoped unit evidence, unknown quantities, battery/fuel separation, raw zero and per-engine profiles')
