# Degrau — desenho das figuras de ângulos: rótulos sem encostar, retas que se cruzam, transversal entre paralelas.
import io, math
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from .folha import INK
from .medidas import arco, arco_transversal


class Medidor(rl_canvas.Canvas):
    """Canvas que não desenha nada: só guarda a caixa de tudo o que seria desenhado (textos, linhas, pontos).
    Mede uma figura com os rótulos já afastados das linhas, antes de reservar espaço para ela."""
    def __init__(self):
        super().__init__(io.BytesIO(), pagesize=A5); self.caixa = None
    def _junta(self, x0, y0, x1, y1):
        c = self.caixa
        self.caixa = (x0, y0, x1, y1) if c is None else (min(c[0], x0), min(c[1], y0), max(c[2], x1), max(c[3], y1))
    def _texto(self, x, y, s):
        self._junta(x, y - 0.25 * self._fontsize, x + self.stringWidth(s, self._fontname, self._fontsize), y + 0.75 * self._fontsize)
    def drawString(self, x, y, s, *a, **k): self._texto(x, y, s)
    def drawRightString(self, x, y, s, *a, **k): self._texto(x - self.stringWidth(s, self._fontname, self._fontsize), y, s)
    def drawCentredString(self, x, y, s, *a, **k): self._texto(x - self.stringWidth(s, self._fontname, self._fontsize) / 2, y, s)
    def line(self, x1, y1, x2, y2): self._junta(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
    def circle(self, x, y, r, *a, **k): self._junta(x - r, y - r, x + r, y + r)
    def arc(self, *a, **k): pass


def cruza(seg, caixa):
    """o segmento cruza o retângulo (xa, ya, xb, yb)? (recorte de Liang-Barsky)"""
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


def sobrepoe(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def _dir(d): return math.cos(math.radians(d)), math.sin(math.radians(d))


def caminho_bico(P, segs, ys):
    """vértices da poligonal que sai de P; o último segmento vai até a reta y = ys"""
    pts = [P]; dirs = []
    x, y = P
    for i, (d, L) in enumerate(segs):
        dx, dy = _dir(d)
        if i == len(segs) - 1: L = (ys - y) / dy
        x, y = x + dx * L, y + dy * L; pts.append((x, y)); dirs.append(d)
    return pts, dirs


def escala_bico(d, largura):
    """fator (até 1) que faz a poligonal caber na largura: reduz altura e segmentos juntos (ângulos iguais)"""
    segs = [(a, L * mm) for a, L in d['segmentos']]
    pts, _ = caminho_bico((0, 0), segs, -d['altura'] * mm)
    xs = [p[0] for p in pts]; w = max(xs) - min(xs)
    util = largura - 10 * mm
    return 1.0 if w <= util else util / w * 0.98


def rotular(c, x, y, ini, abertura, txt, linhas, ocupados, r=4.5 * mm, size=9.5, arco_visivel=True):
    """Arco do ângulo (vértice x, y; de ini a ini+abertura graus) e o texto na bissetriz, afastado até não
    encostar em nenhuma linha nem em outro rótulo. Guarda a caixa do texto em ocupados."""
    if arco_visivel:
        c.setStrokeColor(INK); c.setLineWidth(.7); c.arc(x - r, y - r, x + r, y + r, ini, abertura)
    if not txt: return
    tw = c.stringWidth(txt, 'And', size)

    def caixa(rr, m, f=0.6 * mm):
        cx, cy = x + rr * math.cos(m), y + rr * math.sin(m) - 1.3 * mm
        return (cx - tw / 2 - f, cy - f, cx + tw / 2 + f, cy + 0.7 * size + f)
    # pela bissetriz primeiro; se não houver lugar, um pouco desviado para os lados (ainda dentro do ângulo)
    for desvio in (0, 0.2, -0.2, 0.35, -0.35):
        m = math.radians(ini + abertura * (0.5 + desvio))
        rr = r + 2.8 * mm + 0.5 * tw * abs(math.cos(m)) + (1.2 * mm if abertura < 35 else 0)
        while rr <= r + 32 * mm and (any(cruza(l, caixa(rr, m)) for l in linhas) or any(sobrepoe(caixa(rr, m), o) for o in ocupados)):
            rr += 0.5 * mm
        if rr <= r + 32 * mm: break
    else:
        raise ValueError(f'não há lugar para o rótulo {txt!r}')
    ocupados.append(caixa(rr, m))
    c.setFont('And', size); c.setFillColor(INK)
    c.drawCentredString(x + rr * math.cos(m), y + rr * math.sin(m) - 1.3 * mm, txt)


def nome_do_vertice(c, x, y, nome, direcoes, linhas, padrao=None):
    """escreve o nome do vértice; se a posição padrão encostar numa linha, vai para o meio do maior vão"""
    c.setFont('AndB', 10); c.setFillColor(INK)
    tw = c.stringWidth(nome, 'AndB', 10)
    def caixa(px, py): return (px - 0.3 * mm, py - 0.3 * mm, px + tw + 0.3 * mm, py + 3.6 * mm)
    if padrao and not any(cruza(l, caixa(*padrao)) for l in linhas):
        c.drawString(*padrao, nome); return
    ds = sorted(a % 360 for a in direcoes)
    vaos = [((ds[(i + 1) % len(ds)] - a) % 360 or 360, a) for i, a in enumerate(ds)]
    vao, ini = max(vaos)
    u = _dir(ini + vao / 2)
    for r in (4.5 * mm, 5.5 * mm, 6.5 * mm, 8 * mm):
        px, py = x + r * u[0] - tw / 2, y + r * u[1] - 1.6 * mm
        if not any(cruza(l, caixa(px, py)) for l in linhas): break
    c.drawString(px, py, nome)


# ---------- retas que se cruzam ----------
L_CRUZ = 16 * mm


def desenhar_cruzadas(c, x, y, d, size=9.5, ocupados=None):
    """duas retas pelo ponto (x, y) nas direções d['direcoes']; marcas: [[dir. inicial, dir. final, rótulo]]"""
    linhas = []
    c.setStrokeColor(INK); c.setLineWidth(1)
    for a in d['direcoes']:
        u = _dir(a)
        seg = (x - L_CRUZ * u[0], y - L_CRUZ * u[1], x + L_CRUZ * u[0], y + L_CRUZ * u[1])
        c.line(*seg); linhas.append(seg)
    c.setFillColor(INK); c.circle(x, y, .8 * mm, fill=1, stroke=0)
    if d.get('ponto'):
        nome_do_vertice(c, x, y, d['ponto'], [a for b in d['direcoes'] for a in (b, b + 180)], linhas)
    ocupados = [] if ocupados is None else ocupados
    for i, (a, b, rot) in enumerate(d.get('marcas', [])):
        ini, ab = arco(a, b)
        rotular(c, x, y, ini, ab, rot, linhas, ocupados, r=(4.5 + 1.5 * i) * mm, size=size)


# ---------- transversal entre paralelas ----------
DIST = 16 * mm      # distância entre r e s (diminui se a transversal for muito deitada)
EXT = 7 * mm        # quanto a transversal passa de r e de s


def _geometria_transversal(t, largura):
    """(distância entre r e s, deslocamento horizontal entre os cruzamentos) para caber na largura"""
    util = largura - 24 * mm
    tg = abs(math.tan(math.radians(t)))
    dist = DIST if tg == float('inf') else min(DIST, max(0.0, util - 2 * EXT * abs(math.cos(math.radians(t)))) * tg)
    if dist < 12 * mm:
        raise ValueError(f'transversal muito deitada ({t}°) para o espaço: use direção mais perto de 90°')
    return dist, (dist / math.tan(math.radians(t)) if tg != float('inf') else 0)


def desenhar_transversal(c, x, y_topo, largura, d, numero=True, size=9.5, ocupados=None, linhas_pagina=None):
    """r e s horizontais, transversal t na direção d['direcao']; marcas: [[r|s, posição, rótulo]]"""
    t = d['direcao']
    dist, dx = _geometria_transversal(t, largura)
    yr = y_topo - (6 * mm if numero else 2 * mm) - EXT * math.sin(math.radians(t)); ys = yr - dist
    x0, x1 = x + 4 * mm, x + largura - 6 * mm
    xs = (x0 + x1) / 2 - dx / 2; xr = xs + dx           # cruzamentos centralizados
    u = _dir(t)
    c.setStrokeColor(INK); c.setLineWidth(1)
    retas = [(x0, yr, x1, yr), (x0, ys, x1, ys)]
    trans = (xs - EXT * u[0], ys - EXT * u[1], xr + EXT * u[0], yr + EXT * u[1])
    for seg in retas + [trans]: c.line(*seg)
    c.setFont('AndB', 10); c.setFillColor(INK)
    c.drawString(x1 + 1.5 * mm, yr - 1.2 * mm, 'r'); c.drawString(x1 + 1.5 * mm, ys - 1.2 * mm, 's')
    c.drawString(trans[2] + 1 * mm, trans[3] - 1 * mm, 't')
    ocupados = [] if ocupados is None else ocupados
    ocupados.append((trans[2] + 0.4 * mm, trans[3] - 1.6 * mm, trans[2] + 3.2 * mm, trans[3] + 2.2 * mm))   # o "t"
    pontos = {'r': (xr, yr), 's': (xs, ys)}
    for reta, pos, rot in d.get('marcas', []):
        ini, ab = arco_transversal(t, pos)
        px, py = pontos[reta]
        rotular(c, px, py, ini, ab, rot, retas + [trans] + (linhas_pagina or []), ocupados, r=4 * mm, size=size)
    if linhas_pagina is not None: linhas_pagina.extend(retas + [trans])
