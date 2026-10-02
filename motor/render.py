# Degrau — renderizador: lê as especificações em YAML e desenha com o motor
import io, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from .especificacao import (ErroEspecificacao, carregar_curso, carregar_folha,
                            carregar_pacotes, _chaves, RAIZ)
from .folha import Folha, LIMITE, ESPACO
from .geo import FolhaGeo
from .bicos import Bico
from . import gabarito, audio

MARCA = 'DEGRAU  ·  '
ICONES = ('ouvir', 'escrever', 'ligar', 'circular', 'ler')
TEXTOS = {'fr': {'cada': 'chacun', 'exemplo': 'Exemple'},
          'pt-BR': {'cada': 'cada', 'exemplo': 'Exemplo'}}


def _icone(nome, onde):
    if nome not in ICONES:
        raise ErroEspecificacao(f'{onde}: ícone desconhecido {nome!r} (use {", ".join(ICONES)})')
    return nome


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
    f.palavras([tuple(p) for p in d['itens']], cols=d.get('colunas', 2), size=d.get('tamanho', 19), altura=ctx.get('altura'))

def _ligar(f, d, ctx):
    if 'itens_de' in d:   # reaproveita os pares do primeiro bloco do outro lado
        outro = ctx['folha'][d['itens_de']]['blocos'][0]
        pares = next(iter(outro.values()))['itens']
    elif 'itens' in d: pares = d['itens']
    else: raise ErroEspecificacao(f'{ctx["onde"]}: ligar precisa de itens ou itens_de')
    f.ligar([tuple(p) for p in pares], seed=d.get('semente', 1), altura=ctx.get('altura'))

def _circular(f, d, ctx):
    its = _itens(d, ctx['onde'], ('opcoes', 'resposta'))
    for i, it in enumerate(its):
        if it['resposta'] not in it['opcoes']:
            raise ErroEspecificacao(f'{ctx["onde"]}, item {i + 1}: resposta {it["resposta"]!r} não está nas opções')
    f.circular([it['opcoes'] for it in its], altura=ctx.get('altura'))

def _copiar(f, d, ctx):
    f.copiar(d['itens'], size=d.get('tamanho', 20), altura=ctx.get('altura'))

def _frases(f, d, ctx):
    its = d['itens']
    if all(isinstance(i, list) for i in its):
        f.frases([i[0] for i in its], size=d.get('tamanho', 15), gloss=[i[1] for i in its], altura=ctx.get('altura'))
    else:
        f.frases(its, size=d.get('tamanho', 15), altura=ctx.get('altura'))

def _banco(f, d, ctx):
    f.banco(d['itens'])

def _lacunas(f, d, ctx):
    its = _itens(d, ctx['onde'], ('texto', 'resposta'))
    f.lacunas([it['texto'] for it in its], size=d.get('tamanho', 14), altura=ctx.get('altura'))

def _leitura(f, d, ctx):
    f.leitura(d['linhas'], fois=d.get('vezes', 3), size=d.get('tamanho', 14))

def _verdadeiro_falso(f, d, ctx):
    its = _itens(d, ctx['onde'], ('texto', 'resposta'))
    for i, it in enumerate(its):
        if it['resposta'] not in ('V', 'F'):
            raise ErroEspecificacao(f'{ctx["onde"]}, item {i + 1}: resposta deve ser V ou F')
    f.verdadeiro_falso([it['texto'] for it in its], size=d.get('tamanho', 13.5), altura=ctx.get('altura'))

def _ditado(f, d, ctx):
    its = _itens(d, ctx['onde'], ('resposta',))
    titulo = None
    if 'instrucao' in d:
        p = _pontos(d, ctx)
        titulo = d['instrucao'] + (f'   [{p}]' if p else '')
    f.ditado(len(its), titre=titulo, gloss=d.get('traducao'))

def _texto(f, d, ctx):
    f.texto(d['paragrafos'], size=d.get('tamanho', 12), box=d.get('quadro', False))

def _exemplo(f, d, ctx):
    if 'frase' in d:      # frase complexa e sua decomposição (idiomas)
        _chaves(d, ctx['onde'], ('frase', 'decomposicao'), ('tamanho',))
        f.exemplo_frase(ctx['textos']['exemplo'], d['frase'], d['decomposicao'], size=d.get('tamanho', 11))
    else:                 # figura e texto (geometria)
        _chaves(d, ctx['onde'], ('texto',), ('figura',))
        if 'figura' in d: _validar_figura(d['figura'], ctx['onde'] + ', figura')
        f.exemplo_figura(ctx['textos']['exemplo'], d['texto'], d.get('figura'))

def _perguntas(f, d, ctx):
    its = _itens(d, ctx['onde'], ('pergunta',), ('linhas', 'pontos', 'resposta'))
    qs = [(it['pergunta'] + (f' [{it["pontos"]}]' if 'pontos' in it else ''), it.get('linhas')) for it in its]
    f.perguntas(qs, size=d.get('tamanho', 11))

def _ordenar(f, d, ctx):
    its = _itens(d, ctx['onde'], ('texto', 'resposta'))
    if sorted(it['resposta'] for it in its) != list(range(1, len(its) + 1)):
        raise ErroEspecificacao(f'{ctx["onde"]}: as respostas devem ser 1 a {len(its)}, sem repetir')
    f.ordenar([it['texto'] for it in its], size=d.get('tamanho', 11))

def _decompor(f, d, ctx):
    its = _itens(d, ctx['onde'], ('frase', 'partes'), ('resposta',))
    for i, it in enumerate(its):
        f.decompor(i + 1, it['frase'], it['partes'], size=d.get('tamanho', 11))

def _subinstrucao(f, d, ctx):
    f.subinstrucao(_icone(d['icone'], ctx['onde']), d['instrucao'], _pontos(d, ctx))


# ---------- geometria ----------
FIGURAS = {'angulo':     (('direcoes',), ('nomes', 'marca', 'comprimento')),
           'semirretas': (('direcoes', 'nomes', 'vertice'), ('comprimento',)),
           'bico':       (('altura', 'segmentos', 'marcas'), ('tamanho',))}

def _validar_figura(fig, onde):
    figs = [k for k in fig if k in FIGURAS]
    if len(figs) != 1:
        raise ErroEspecificacao(f'{onde}: precisa de exatamente uma figura ({", ".join(FIGURAS)})')
    _chaves(fig[figs[0]], f'{onde} ({figs[0]})', *FIGURAS[figs[0]])
    return figs[0]

def _grade(f, d, ctx):
    its = d['itens']
    for i, it in enumerate(its):
        onde = f'{ctx["onde"]}, item {i + 1}'
        _chaves(it, onde, (), ('angulo', 'semirretas', 'bico', 'texto', 'resposta'))
        if any(k in FIGURAS for k in it): _validar_figura(it, onde)
        elif 'texto' not in it: raise ErroEspecificacao(f'{onde}: item sem figura e sem texto')
    f.grade(its, colunas=d.get('colunas', 2), tamanho=d.get('tamanho', 12), altura=ctx.get('altura'))

def _figura(f, d, ctx):
    _validar_figura(d, ctx['onde'])
    f.figura(d)

def _alternativas(f, d, ctx):
    letras = [chr(65 + k) for k in range(len(d['itens']))]
    if d['resposta'] not in letras:
        raise ErroEspecificacao(f'{ctx["onde"]}: resposta deve ser uma de {", ".join(letras)}')
    f.alternativas(d['itens'], tamanho=d.get('tamanho', 12))


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
    'exemplo':          (_exemplo, (), ('frase', 'decomposicao', 'tamanho', 'texto', 'figura')),
    'perguntas':        (_perguntas, ('itens',), ('tamanho',)),
    'ordenar':          (_ordenar, ('itens',), ('tamanho',)),
    'decompor':         (_decompor, ('itens',), ('tamanho',)),
    'subinstrucao':     (_subinstrucao, ('instrucao', 'icone'), ('pontos', 'pontos_cada')),
    'grade':            (_grade, ('itens',), ('colunas', 'tamanho')),
    'figura':           (_figura, (), ('angulo', 'semirretas', 'bico')),
    'alternativas':     (_alternativas, ('itens', 'resposta'), ('tamanho',)),
}


# blocos de itens espaçados: dividem entre si a altura que sobra na página
ELASTICOS = {'palavras', 'ligar', 'circular', 'copiar', 'frases', 'lacunas', 'verdadeiro-falso', 'grade'}


def _tipo(bloco, onde):
    if not isinstance(bloco, dict) or len(bloco) != 1:
        raise ErroEspecificacao(f'{onde}: cada bloco é um mapa com uma única chave (o tipo)')
    return next(iter(bloco))


def _medir(f, bloco, ctx):
    """altura de um bloco fixo: desenha num canvas descartável e vê quanto o cursor desceu"""
    c, y = f.c, f.y
    f.c = canvas.Canvas(io.BytesIO(), pagesize=A5)
    try:
        desenhar_bloco(f, bloco, ctx)
        return y - f.y
    finally:
        f.c, f.y = c, y


def desenhar_bloco(f, bloco, ctx):
    tipo = _tipo(bloco, ctx['onde']); dados = bloco[tipo]
    if tipo not in TIPOS:
        raise ErroEspecificacao(f'{ctx["onde"]}: tipo de bloco desconhecido {tipo!r}')
    if isinstance(dados, list): dados = {'itens': dados}   # atalho: "banco: [a, b, c]"
    func, obrig, opc = TIPOS[tipo]
    _chaves(dados, ctx['onde'] + f' ({tipo})', obrig, opc)
    try:
        func(f, dados, dict(ctx, onde=ctx['onde'] + f' ({tipo})'))
    except ValueError as e:
        raise ErroEspecificacao(f'{ctx["onde"]} ({tipo}): {e}') from None


def desenhar_folha(f, folha, curso, codigo_bloco=None):
    textos = TEXTOS[curso['idioma_folha']]
    for lado in 'ab':
        L = folha[lado]
        codigo = f'{folha["folha"]}{lado}'
        onde = f'{folha["_caminho"]}, lado {lado}'
        icone, pontos = _icone(L['icone'], onde), _pontos(L, {'textos': textos})
        if isinstance(f, FolhaGeo):
            if 'traducao' in L: raise ErroEspecificacao(f'{onde}: folha de caderno não tem traducao')
            f.pagina(codigo, folha['unidade'], L['instrucao'], icone, pontos, bloco=codigo_bloco)
        else:
            f.pagina(codigo, folha['unidade'], L['instrucao'], L.get('traducao'), icone, pontos)
        ctxs = [{'folha': folha, 'textos': textos, 'onde': f'{onde}, bloco {i + 1}'}
                for i in range(len(L['blocos']))]
        elasticos = [_tipo(b, cx['onde']) in ELASTICOS for b, cx in zip(L['blocos'], ctxs)]
        fixos = sum(_medir(f, b, cx) for b, cx, e in zip(L['blocos'], ctxs, elasticos) if not e)
        if any(elasticos):
            parte = (f.y - LIMITE - fixos) / sum(elasticos) - ESPACO
            if parte <= 0:
                raise ErroEspecificacao(f'{onde}: os blocos não cabem na página')
            for cx, e in zip(ctxs, elasticos):
                if e: cx['altura'] = parte
        for bloco, cx in zip(L['blocos'], ctxs):
            desenhar_bloco(f, bloco, cx)
        if f.y < LIMITE - ESPACO - 0.5:
            raise ErroEspecificacao(f'{onde}: o conteúdo passa {(LIMITE - f.y) / mm:.1f} mm do limite da página')
        f.fim(codigo)


def gerar_pacote(pacote, saida):
    """Gera o PDF e, ao lado, o gabarito (.gabarito.csv), a aba Gabarito da planilha
    (.planilha.csv, só folhas de caderno) e o bloco de áudio (.audio.txt, se houver).
    Devolve (arquivos gerados, páginas em que é preciso esconder o texto ao ouvir)."""
    curso = carregar_curso(pacote['curso'])
    versoes = pacote.get('versoes') or [1] * len(pacote['folhas'])
    folhas = [carregar_folha(pacote['curso'], cod, v) for cod, v in zip(pacote['folhas'], versoes)]  # valida tudo antes de desenhar
    os.makedirs(saida, exist_ok=True)
    caminho = os.path.join(saida, pacote['arquivo'])
    f = (Bico if curso['folha']['campos'] == 'caderno' else Folha)(caminho, pacote['titulo'])
    f.MARCA = MARCA + curso['folha']['marca']
    blocos = pacote.get('blocos') or [None] * len(folhas)   # código do bloco de cada folha (CASD)
    for folha, bloco in zip(folhas, blocos):
        desenhar_folha(f, folha, curso, bloco)
    f.save()
    base = caminho[:-4]
    linhas = [l for folha in folhas for l in gabarito.respostas_folha(folha)]
    gabarito.escrever_csv(linhas, base + '.gabarito.csv')
    arquivos = [caminho, base + '.gabarito.csv']
    if curso['folha']['campos'] == 'caderno':
        gabarito.escrever_planilha(folhas, curso, base + '.planilha.csv')
        arquivos.append(base + '.planilha.csv')
    esconder = audio.escrever(folhas, base + '.audio.txt')
    if esconder is not None: arquivos.append(base + '.audio.txt')
    return arquivos, esconder or []


def gerar(caminho_pacotes, saida=None):
    saida = saida or os.path.join(os.path.dirname(os.path.abspath(caminho_pacotes)), 'pdf')
    return [gerar_pacote(p, saida) for p in carregar_pacotes(caminho_pacotes)]
