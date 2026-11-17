"""Estado operativo didático; avaliação de origem distinta dos recursos."""
import math


def validar_alteracoes(changes):
    if not isinstance(changes,dict) or not changes or set(changes)-{'index_percent','lost'}:
        raise ValueError('Informe índice e/ou declaração explícita de perda.')
    if 'index_percent' in changes:
        value=changes['index_percent']
        if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=100):
            raise ValueError('Índice deve ser número finito entre 0 e 100 ou null.')
    if 'lost' in changes and type(changes['lost']) is not bool:
        raise ValueError('Declaração de perda deve ser booleana.')
    return dict(changes)


def classificar(domain, index):
    validar_alteracoes({'index_percent':index})
    if domain!='superficie' or index is None:return None
    return 'combater' if index>60 else 'navegar' if index>=40 else 'flutuar'
