# Degrau — leitura e validação das especificações em YAML (curso, folha, pacote)
import os
import yaml

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ErroEspecificacao(Exception):
    pass


def _ler(caminho):
    if not os.path.exists(caminho):
        raise ErroEspecificacao(f'{caminho}: arquivo não encontrado')
    with open(caminho, encoding='utf-8') as f:
        return yaml.safe_load(f)


def _chaves(d, onde, obrig, opc=()):
    if not isinstance(d, dict):
        raise ErroEspecificacao(f'{onde}: esperava um mapa de chaves, veio {type(d).__name__}')
    falta = [k for k in obrig if k not in d]
    sobra = [k for k in d if k not in obrig and k not in opc]
    if falta: raise ErroEspecificacao(f'{onde}: falta {", ".join(falta)}')
    if sobra: raise ErroEspecificacao(f'{onde}: chave desconhecida {", ".join(sobra)}')


def carregar_curso(curso):
    caminho = os.path.join(RAIZ, 'curriculos', f'{curso}.yaml')
    d = _ler(caminho)
    if 'folha' not in d:
        raise ErroEspecificacao(f'{caminho}: falta a chave folha (marca, campos)')
    _chaves(d['folha'], f'{caminho}, folha', ('marca', 'campos'), ('arquivo',))
    if d['folha']['campos'] not in ('papel', 'caderno'):
        raise ErroEspecificacao(f'{caminho}, folha.campos: use papel ou caderno')
    d['idioma_folha'] = d.get('idioma_alvo') or d.get('idioma')
    return d


def caminho_folha(curso, codigo, versao=1):
    """'G1 81' -> folhas/<curso>/G1/81.yaml; versão 2 -> 81.v2.yaml (repetição com exercícios novos)"""
    nivel, num = str(codigo).split()
    return os.path.join(RAIZ, 'folhas', curso, nivel, f'{num}.yaml' if versao == 1 else f'{num}.v{versao}.yaml')


def carregar_folha(curso, codigo, versao=1):
    caminho = caminho_folha(curso, codigo, versao)
    return validar_folha(_ler(caminho), caminho, codigo)


def validar_folha(d, caminho, codigo):
    """estrutura da folha (chaves de folha e lados); os blocos são validados ao desenhar"""
    _chaves(d, caminho, ('folha', 'unidade', 'a', 'b'))
    if str(d['folha']) != str(codigo):
        raise ErroEspecificacao(f'{caminho}: folha diz {d["folha"]!r}, esperado {codigo!r}')
    for lado in 'ab':
        onde = f'{caminho}, lado {lado}'
        _chaves(d[lado], onde, ('instrucao', 'icone', 'blocos'), ('traducao', 'pontos', 'pontos_cada'))
        if not isinstance(d[lado]['blocos'], list) or not d[lado]['blocos']:
            raise ErroEspecificacao(f'{onde}: blocos deve ser uma lista não vazia')
    d['_caminho'] = caminho
    return d


def carregar_pacotes(caminho):
    d = _ler(caminho)
    if not isinstance(d, list):
        raise ErroEspecificacao(f'{caminho}: esperava uma lista de pacotes')
    for i, p in enumerate(d):
        _chaves(p, f'{caminho}, pacote {i + 1}', ('arquivo', 'titulo', 'curso', 'folhas'))
    return d
