# Testes básicos: tudo gera sem erro; o gabarito bate com o plano; expressões conferidas; nenhum texto sai da página nem fica
# sobre outro texto ou sobre uma linha. Rodar com: .venv/bin/pytest
import os, shutil, subprocess
import pytest
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import mm

from motor import folha as motor_folha
from motor.folha import M, W, H
from motor.render import gerar
from motor.especificacao import RAIZ, ErroEspecificacao, carregar_folha
from motor.gabarito import respostas_folha
from motor.audio import faixas, numero_fr

FOLGA = 0.3  # pt: tolerância de arredondamento


class Gravador(rl_canvas.Canvas):
    """Canvas que guarda, por página, as caixas de texto e as linhas desenhadas."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.paginas, self.textos, self.linhas = [], [], []

    def _texto(self, x, y, s):
        if not s.strip(): return
        w = self.stringWidth(s, self._fontname, self._fontsize)
        # corpo da letra: da linha de base até 70% do tamanho (sem descendentes)
        self.textos.append((s, x, y, x + w, y + 0.7 * self._fontsize))

    def drawString(self, x, y, s, *a, **k):
        self._texto(x, y, s); return super().drawString(x, y, s, *a, **k)
    def drawRightString(self, x, y, s, *a, **k):
        self._texto(x - self.stringWidth(s, self._fontname, self._fontsize), y, s)
        return super().drawRightString(x, y, s, *a, **k)
    def drawCentredString(self, x, y, s, *a, **k):
        self._texto(x - self.stringWidth(s, self._fontname, self._fontsize) / 2, y, s)
        return super().drawCentredString(x, y, s, *a, **k)
    def line(self, x1, y1, x2, y2):
        self.linhas.append((x1, y1, x2, y2)); return super().line(x1, y1, x2, y2)
    def showPage(self):
        self.paginas.append((self._pageNumber, self.textos, self.linhas))
        self.textos, self.linhas = [], []
        return super().showPage()


GRAVADORES = []

def _gravar(monkeypatch, gerador, destino=None):
    GRAVADORES.clear()
    def criar(caminho, *a, **k):
        if destino: caminho = os.path.join(destino, os.path.basename(caminho))
        g = Gravador(caminho, *a, **k); GRAVADORES.append(g); return g
    monkeypatch.setattr(motor_folha.canvas, 'Canvas', criar)
    gerador()
    return [(os.path.basename(g._filename), n, t, l) for g in GRAVADORES for n, t, l in g.paginas]


def _cruza(seg, caixa):
    """o segmento cruza o retângulo? (recorte de Liang-Barsky)"""
    x1, y1, x2, y2 = seg; xa, ya, xb, yb = caixa
    t0, t1, dx, dy = 0.0, 1.0, x2 - x1, y2 - y1
    for p, q in ((-dx, x1 - xa), (dx, xb - x1), (-dy, y1 - ya), (dy, yb - y1)):
        if p == 0:
            if q < 0: return False
        else:
            t = q / p
            if p < 0: t0 = max(t0, t)
            else: t1 = min(t1, t)
            if t0 > t1: return False
    return True


def erros_fora_da_pagina(paginas):
    return [f'{arq} pág {n}: {s!r}' for arq, n, ts, _ in paginas for s, x0, y0, x1, y1 in ts
            if x0 < M - FOLGA or x1 > W - M + FOLGA or y0 < M - 5 * mm or y1 > H - M + 5 * mm]


def erros_texto_sobre_texto(paginas):
    erros = []
    for arq, n, ts, _ in paginas:
        for i, a in enumerate(ts):
            for b in ts[i + 1:]:
                if min(a[3], b[3]) - max(a[1], b[1]) > FOLGA and min(a[4], b[4]) - max(a[2], b[2]) > FOLGA:
                    erros.append(f'{arq} pág {n}: {a[0]!r} × {b[0]!r}')
    return erros


def erros_texto_sobre_linha(paginas):
    return [f'{arq} pág {n}: {s!r}' for arq, n, ts, ls in paginas for s, *cx in ts
            if any(_cruza(seg, (cx[0] + FOLGA, cx[1] + FOLGA, cx[2] - FOLGA, cx[3] - FOLGA)) for seg in ls)]


VERIFICACOES = [erros_fora_da_pagina, erros_texto_sobre_texto, erros_texto_sobre_linha]


@pytest.fixture(scope='module')
def paginas_yaml(tmp_path_factory):
    with pytest.MonkeyPatch.context() as mp:
        saida = str(tmp_path_factory.mktemp('pdf'))
        return _gravar(mp, lambda: gerar(os.path.join(RAIZ, 'exemplos', 'pacotes.yaml'), saida))


def test_yaml_gera_paginas(paginas_yaml):
    assert len(paginas_yaml) == 26


@pytest.mark.parametrize('verificar', VERIFICACOES, ids=lambda v: v.__name__)
def test_yaml(paginas_yaml, verificar):
    erros = verificar(paginas_yaml)
    assert not erros, '\n'.join(erros)


# ---------- gabarito (fase 2): igual à seção 6.3 do plano ----------
PLANO_6_3 = {
    'G1 1a': ['PQR', 'NMT', 'DCE', 'GFH'],
    'G1 1b': ['A', 'R', 'O', 'Ra', 'A', 'O', 'A', 'O', 'A', 'O'],
    'G1 2a': ['A', 'R', 'O', 'R', 'A', 'O'],
    'G1 2b': ['conjunto:PÔQ,QÔR,RÔS,PÔR,QÔS,PÔS', '10'],
    'G1 3a': ['R', 'R', 'O', 'A', 'O', 'O', 'Ra', 'A', 'A', 'Ra'],
    'G1 3b': ['Y', 'JKL obtuso', 'reto', '10', 'S'],
    'G1 81a': ['75', '85', '80', '90'], 'G1 81b': ['40', '30', '30', '50'],
    'G1 85a': ['75', '60', '45', '35'], 'G1 85b': ['60', '65', '40', '50'],
    'G1 89a': ['15', '10'], 'G1 89b': ['C'],
    '6A 3a': ['merci', 'un avion', 'un étudiant', 'fatigué', 'une ville', 'content'],
    '6A 4b': ["m'appelle", 'suis', 'avion', 'ville', 'Bienvenue'],
    '6A 5b': ['F', 'V', 'V', 'V', 'Je suis dans un avion.', 'Toulouse est une ville en France.'],
}

def test_gabarito_bate_com_o_plano():
    obtido = {}
    for curso, cods in [('geometria-plana-epcar', ['G1 1', 'G1 2', 'G1 3', 'G1 81', 'G1 85', 'G1 89']),
                        ('frances-delf-b1', ['6A 3', '6A 4', '6A 5'])]:
        for cod in cods:
            for l in respostas_folha(carregar_folha(curso, cod)):
                if l['pagina'] in PLANO_6_3: obtido.setdefault(l['pagina'], []).append(l['respostas'][0])
    assert obtido == PLANO_6_3


def _folha_89(mexer):
    f = carregar_folha('geometria-plana-epcar', 'G1 89'); mexer(f); return f

@pytest.mark.parametrize('mexer, msg', [
    (lambda f: f['b']['blocos'][1]['figura']['bico']['marcas'].__setitem__(2, [2, None, '100°']),
     'o ângulo desenhado é 80°'),
    (lambda f: f['a']['blocos'][0]['grade']['itens'][0]['bico']['marcas'].__setitem__(1, [1, None, '4x + 10°']),
     'valores diferentes de x'),
    (lambda f: f['a']['blocos'][0]['grade']['itens'][1].__setitem__('resposta', 12), 'os rótulos dão x = 10'),
    (lambda f: f['b']['blocos'][2]['alternativas'].__setitem__('resposta', 'B'), 'a figura dá x = 25'),
])
def test_expressoes_erradas_falham(mexer, msg):
    with pytest.raises(ErroEspecificacao, match=msg):
        respostas_folha(_folha_89(mexer))


def test_audio():
    assert [numero_fr(n) for n in (1, 21, 64, 71, 80, 91, 112)] == [
        'un', 'vingt et un', 'soixante-quatre', 'soixante et onze', 'quatre-vingts', 'quatre-vingt-onze', 'cent douze']
    fx = dict((p, (t, e)) for p, t, e in faixas(carregar_folha('frances-delf-b1', '6A 5')))
    assert fx['6A 5a'][0].splitlines()[0] == 'Feuille cinq a.'
    assert '[L\'hôtesse] Bienvenue à Toulouse !' in fx['6A 5a'][0]
    assert fx['6A 5b'] == ('Feuille cinq b.\nUn. Je suis dans un avion.\nDeux. Toulouse est une ville en France.', True)
    assert not fx['6A 5a'][1]


# ---------- correção do CASD (fase 3) ----------
def test_modelo_de_gabarito_atualizado(tmp_path):
    """correcao/modelos/gabarito.csv é o bloco G1 1-3 gerado do YAML (o simulador usa este arquivo)"""
    from motor.gabarito import escrever_planilha
    from motor.especificacao import carregar_curso
    novo = tmp_path / 'g.csv'
    escrever_planilha([carregar_folha('geometria-plana-epcar', f'G1 {n}') for n in (1, 2, 3)],
                      carregar_curso('geometria-plana-epcar'), str(novo))
    assert novo.read_text(encoding='utf-8') == open(os.path.join(RAIZ, 'correcao', 'modelos', 'gabarito.csv'), encoding='utf-8').read()


@pytest.mark.skipif(not shutil.which('node'), reason='node não instalado')
def test_correcao_simulada():
    r = subprocess.run(['node', os.path.join(RAIZ, 'correcao', 'teste', 'simular.js')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
