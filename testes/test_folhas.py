# Testes básicos: tudo gera sem erro; o gabarito calculado bate; nenhum texto sai da página nem fica
# sobre outro texto ou sobre uma linha. Rodar com: .venv/bin/pytest
import os
import pytest
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import mm

from motor import folha as motor_folha
from motor.folha import M, W, H
from motor.render import gerar, gerar_pacote
from motor.especificacao import RAIZ, carregar_pacotes

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


# Gabarito calculado das figuras (bicos) = seção 6.3 do plano
GABARITO_81_89 = {
    'G1 81a': [75, 85, 80, 90], 'G1 81b': [40, 30, 30, 50],
    'G1 85a': [75, 60, 45, 35], 'G1 85b': [60, 65, 40, 50],
    'G1 89a': [15, 10], 'G1 89b': ['C'],
}

def test_gabarito_81_89(tmp_path):
    pacote = next(p for p in carregar_pacotes(os.path.join(RAIZ, 'exemplos', 'pacotes.yaml'))
                  if p['folhas'] == ['G1 81', 'G1 85', 'G1 89'])
    _, gab = gerar_pacote(pacote, str(tmp_path))
    obtido = {}
    for (pag, item), resp in sorted(gab.items()): obtido.setdefault(pag, []).append(resp)
    assert obtido == GABARITO_81_89
