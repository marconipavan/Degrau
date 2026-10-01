# Degrau — verificação do desenho: nenhum texto fora da página, sobre outro texto ou sobre uma linha.
# Usada pelos testes e pela geração automática (o conteúdo novo passa pelas mesmas regras).
import io
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from .folha import Folha, M, W, H
from .bicos import Bico, cruza

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


# páginas: [(nome, número, textos, linhas)]
def erros_fora_da_pagina(paginas):
    return [f'{arq} pág {n}: {s!r} sai da área útil' for arq, n, ts, _ in paginas for s, x0, y0, x1, y1 in ts
            if x0 < M - FOLGA or x1 > W - M + FOLGA or y0 < M - 5 * mm or y1 > H - M + 5 * mm]


def erros_texto_sobre_texto(paginas):
    erros = []
    for arq, n, ts, _ in paginas:
        for i, a in enumerate(ts):
            for b in ts[i + 1:]:
                if min(a[3], b[3]) - max(a[1], b[1]) > FOLGA and min(a[4], b[4]) - max(a[2], b[2]) > FOLGA:
                    erros.append(f'{arq} pág {n}: {a[0]!r} sobre {b[0]!r}')
    return erros


def erros_texto_sobre_linha(paginas):
    return [f'{arq} pág {n}: {s!r} sobre uma linha' for arq, n, ts, ls in paginas for s, *cx in ts
            if any(cruza(seg, (cx[0] + FOLGA, cx[1] + FOLGA, cx[2] - FOLGA, cx[3] - FOLGA)) for seg in ls)]


VERIFICACOES = [erros_fora_da_pagina, erros_texto_sobre_texto, erros_texto_sobre_linha]


def verificar_folha(folha, curso):
    """Desenha uma folha num canvas gravador e devolve a lista de problemas de desenho."""
    from .render import desenhar_folha, MARCA
    f = (Bico if curso['folha']['campos'] == 'caderno' else Folha)(io.BytesIO(), 'verificação')
    f.c = Gravador(io.BytesIO(), pagesize=A5)
    f.MARCA = MARCA + curso['folha']['marca']
    desenhar_folha(f, folha, curso)
    paginas = [(folha['folha'] + 'ab'[n - 1], n, t, l) for n, t, l in f.c.paginas]
    return [e for v in VERIFICACOES for e in v(paginas)]
