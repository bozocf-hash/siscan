"""Ponte autorizada entre unidades individuais e o mapa, sem criar instâncias."""
from contextlib import contextmanager
import uuid

import engine_units
import map_units


@contextmanager
def _read_view(db):
    db.execute('SAVEPOINT map_groups_view')
    try:
        yield
        db.execute('RELEASE map_groups_view')
    except Exception:
        db.execute('ROLLBACK TO map_groups_view')
        db.execute('RELEASE map_groups_view')
        raise


def _controlled_domain(db, unit):
    """Reconhece somente o contrato aéreo controlado criado por prepare_units."""
    snapshot = unit['snapshot']
    payload = engine_units.controlled_example()
    validation = engine_units.validate_input(payload)
    if not validation['accepted']:
        return None
    manifest = validation['manifest']
    model = 'SYN-AIR-MODEL-001'
    expected = str(uuid.uuid5(uuid.NAMESPACE_URL, engine_units.input_hash(
        dict(model=model, input=payload, manifest=manifest))))
    configuration = db.execute('SELECT * FROM engine_configurations WHERE version_id=?',
                               (unit['configuration_version_id'],)).fetchone()
    identity = db.execute('SELECT purpose FROM engine_units WHERE unit_id=?', (unit['unit_id'],)).fetchone()
    if (not configuration or not identity or identity['purpose'] != 'synthetic-engine-01'
            or unit['configuration_version_id'] != expected
            or snapshot.get('model_id') != model
            or snapshot.get('source_kind') != 'synthetic_controlled'
            or snapshot.get('official_calculation_ready') is not False
            or snapshot.get('input_template') != payload or snapshot.get('input_manifest') != manifest
            or snapshot.get('configuration_id') != payload['configuration_id']
            or configuration['model_id'] != model
            or configuration['configuration_id'] != payload['configuration_id']
            or configuration['input_json'] != engine_units.encoded(payload)
            or configuration['manifest_json'] != engine_units.encoded(manifest)):
        return None
    return dict(domain='aereo', basis='synthetic_controlled',
                reference='engine_units.prepare_units/synthetic-engine-01/' + expected)


def view(db, user: dict, team: str) -> dict:
    """Vista SQL consistente do partido; não reserva disponibilidade futura."""
    with _read_view(db):
        exercise = map_units.context(db, user, team)
        assets = map_units.listing(db, user, team)['units']
        instances = {u['asset_id']: u for u in engine_units.list_units(db, user)['units']
                     if u['team'] == team and u['allocated']}
        inventory, units = {}, []
        for asset in assets:
            instance = instances.get(asset['id'])
            evidence = _controlled_domain(db, instance) if instance else None
            item = dict(asset_id=asset['id'], unit_id=instance['unit_id'] if instance else None,
                        code=asset['code'], name=asset['name'], latitude=asset['latitude'],
                        longitude=asset['longitude'], position_revision=asset['position_revision'],
                        eligible=evidence is not None, domain=evidence['domain'] if evidence else None,
                        reason=None if evidence else ('Snapshot/instância não disponível.' if not instance
                                                     else 'Domínio/configuração sem mapeamento demonstrado.'))
            units.append(item)
            if evidence:
                uid = instance['unit_id']
                inventory[uid] = dict(unit_id=uid, exercise_id=exercise['id'], team=team,
                    domain=evidence['domain'], domain_evidence=evidence, allocated=True,
                    snapshot_id=instance['snapshot_id'], snapshot_sha256=instance['snapshot_sha256'],
                    configuration_version_id=instance['configuration_version_id'], snapshot=instance['snapshot'])
        return dict(context=dict(exercise_id=exercise['id'], team=team),
                    exercise_open=exercise['state'] == 'open', inventory=inventory, units=units)
