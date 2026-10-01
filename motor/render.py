# Degrau — renderizador: lê as especificações em YAML e desenha com o motor
import os
from .especificacao import (ErroEspecificacao, carregar_curso, carregar_folha,
                            carregar_pacotes, _chaves, RAIZ)
from .folha import Folha

MARCA = 'DEGRAU  ·  '
ICONES = {'ouvir': 'ecoute', 'escrever': 'ecris', 'ligar': 'relie', 'circular': 'entoure', 'ler': 'lis'}
TEXTOS = {'fr': {'cada': 'chacun', 'exemplo': 'Exemple'},
          'pt-BR': {'cada': 'cada', 'exemplo': 'Exemplo'}}


def _icone(nome, onde):
    if nome not in ICONES:
        raise ErroEspecificacao(f'{onde}: ícone desconhecido {nome!r} (use {", ".join(ICONES)})')
    return ICONES[nome]


def _pontos(d, ctx):
    if 'pontos_cada' in d: return f'{d["pontos_cada"]} {ctx["textos"]["cada"]}'
    if 'pontos' in d: return str(d['pontos'])
    return None


def _itens(d, onde, obrig, opc=()):
    for i, it in enumerate(d['itens']):
        _chaves(it, f'{onde}, item {i + 1}', obrig, opc)
    return d['itens']


# ---------- tipos de bloco: função(folha_pdf, dados, contexto) ----------

def _palavras(f, d, ctx):
    f.mots([tuple(p) for p in d['itens']], cols=d.get('colunas', 2), size=d.get('tamanho', 19))

def _ligar(f, d, ctx):
    if 'itens_de' in d:   # reaproveita os pares do primeiro bloco do outro lado
        outro = ctx['folha'][d['itens_de']]['blocos'][0]
        pares = next(iter(outro.values()))['itens']
    elif 'itens' in d: pares = d['itens']
    else: raise ErroEspecificacao(f'{ctx["onde"]}: ligar precisa de itens ou itens_de')
    f.relie([tuple(p) for p in pares], seed=d.get('semente', 1))

def _circular(f, d, ctx):
    its = _itens(d, ctx['onde'], ('opcoes', 'resposta'))
    for i, it in enumerate(its):
        if it['resposta'] not in it['opcoes']:
            raise ErroEspecificacao(f'{ctx["onde"]}, item {i + 1}: resposta {it["resposta"]!r} não está nas opções')
    f.entoure([it['opcoes'] for it in its])

def _copiar(f, d, ctx):
    f.recopie(d['itens'], size=d.get('tamanho', 20))

def _frases(f, d, ctx):
    its = d['itens']
    if all(isinstance(i, list) for i in its):
        f.phrases([i[0] for i in its], size=d.get('tamanho', 15), gloss=[i[1] for i in its])
    else:
        f.phrases(its, size=d.get('tamanho', 15))

def _banco(f, d, ctx):
    f.banque(d['itens'])

def _lacunas(f, d, ctx):
    its = _itens(d, ctx['onde'], ('texto', 'resposta'))
    f.trous([it['texto'] for it in its], size=d.get('tamanho', 14))

def _leitura(f, d, ctx):
    f.lecture(d['linhas'], fois=d.get('vezes', 3), size=d.get('tamanho', 14))

def _verdadeiro_falso(f, d, ctx):
    its = _itens(d, ctx['onde'], ('texto', 'resposta'))
    for i, it in enumerate(its):
        if it['resposta'] not in ('V', 'F'):
            raise ErroEspecificacao(f'{ctx["onde"]}, item {i + 1}: resposta deve ser V ou F')
    f.vraifaux([it['texto'] for it in its], size=d.get('tamanho', 13.5))

def _ditado(f, d, ctx):
    its = _itens(d, ctx['onde'], ('resposta',))
    titulo = None
    if 'instrucao' in d:
        p = _pontos(d, ctx)
        titulo = d['instrucao'] + (f'   [{p}]' if p else '')
    f.dictee(len(its), titre=titulo, gloss=d.get('traducao'))

def _texto(f, d, ctx):
    f.texte(d['paragrafos'], size=d.get('tamanho', 12), box=d.get('quadro', False))

def _exemplo(f, d, ctx):
    f.exemple(ctx['textos']['exemplo'], d['frase'], d['decomposicao'], size=d.get('tamanho', 11))

def _perguntas(f, d, ctx):
    its = _itens(d, ctx['onde'], ('pergunta',), ('linhas', 'pontos', 'resposta'))
    qs = [(it['pergunta'] + (f' [{it["pontos"]}]' if 'pontos' in it else ''), it.get('linhas')) for it in its]
    f.questions(qs, size=d.get('tamanho', 11))

def _ordenar(f, d, ctx):
    its = _itens(d, ctx['onde'], ('texto', 'resposta'))
    if sorted(it['resposta'] for it in its) != list(range(1, len(its) + 1)):
        raise ErroEspecificacao(f'{ctx["onde"]}: as respostas devem ser 1 a {len(its)}, sem repetir')
    f.ordre([it['texto'] for it in its], size=d.get('tamanho', 11))

def _decompor(f, d, ctx):
    its = _itens(d, ctx['onde'], ('frase', 'partes'), ('resposta',))
    for i, it in enumerate(its):
        f.decompose(i + 1, it['frase'], it['partes'], size=d.get('tamanho', 11))

def _subinstrucao(f, d, ctx):
    f.sousinstr(_icone(d['icone'], ctx['onde']), d['instrucao'], _pontos(d, ctx))


# nome: (função, chaves obrigatórias, chaves opcionais)
TIPOS = {
    'palavras':         (_palavras, ('itens',), ('colunas', 'tamanho')),
    'ligar':            (_ligar, (), ('itens', 'itens_de', 'semente')),
    'circular':         (_circular, ('itens',), ()),
    'copiar':           (_copiar, ('itens',), ('tamanho',)),
    'frases':           (_frases, ('itens',), ('tamanho',)),
    'banco':            (_banco, ('itens',), ()),
    'lacunas':          (_lacunas, ('itens',), ('tamanho',)),
    'leitura':          (_leitura, ('linhas',), ('vezes', 'tamanho')),
    'verdadeiro-falso': (_verdadeiro_falso, ('itens',), ('tamanho',)),
    'ditado':           (_ditado, ('itens',), ('instrucao', 'traducao', 'pontos', 'pontos_cada')),
    'texto':            (_texto, ('paragrafos',), ('tamanho', 'quadro')),
    'exemplo':          (_exemplo, ('frase', 'decomposicao'), ('tamanho',)),
    'perguntas':        (_perguntas, ('itens',), ('tamanho',)),
    'ordenar':          (_ordenar, ('itens',), ('tamanho',)),
    'decompor':         (_decompor, ('itens',), ('tamanho',)),
    'subinstrucao':     (_subinstrucao, ('instrucao', 'icone'), ('pontos', 'pontos_cada')),
}


def desenhar_bloco(f, bloco, ctx):
    if not isinstance(bloco, dict) or len(bloco) != 1:
        raise ErroEspecificacao(f'{ctx["onde"]}: cada bloco é um mapa com uma única chave (o tipo)')
    tipo, dados = next(iter(bloco.items()))
    if tipo not in TIPOS:
        raise ErroEspecificacao(f'{ctx["onde"]}: tipo de bloco desconhecido {tipo!r}')
    if isinstance(dados, list): dados = {'itens': dados}   # atalho: "banco: [a, b, c]"
    func, obrig, opc = TIPOS[tipo]
    _chaves(dados, ctx['onde'] + f' ({tipo})', obrig, opc)
    func(f, dados, dict(ctx, onde=ctx['onde'] + f' ({tipo})'))


def desenhar_folha(f, folha, curso):
    textos = TEXTOS[curso['idioma_folha']]
    for lado in 'ab':
        L = folha[lado]
        codigo = f'{folha["folha"]}{lado}'
        onde = f'{folha["_caminho"]}, lado {lado}'
        f.page(codigo, folha['unidade'], L['instrucao'], L.get('traducao'),
               _icone(L['icone'], onde), _pontos(L, {'textos': textos}))
        for i, bloco in enumerate(L['blocos']):
            desenhar_bloco(f, bloco, {'folha': folha, 'textos': textos, 'onde': f'{onde}, bloco {i + 1}'})
        f.fim(codigo)


def gerar_pacote(pacote, saida):
    curso = carregar_curso(pacote['curso'])
    folhas = [carregar_folha(pacote['curso'], cod) for cod in pacote['folhas']]  # valida tudo antes de desenhar
    os.makedirs(saida, exist_ok=True)
    caminho = os.path.join(saida, pacote['arquivo'])
    f = Folha(caminho, pacote['titulo'])
    f.MARCA = MARCA + curso['folha']['marca']
    for folha in folhas:
        desenhar_folha(f, folha, curso)
    f.save()
    return caminho


def gerar(caminho_pacotes, saida=None):
    saida = saida or os.path.join(os.path.dirname(os.path.abspath(caminho_pacotes)), 'pdf')
    return [gerar_pacote(p, saida) for p in carregar_pacotes(caminho_pacotes)]
