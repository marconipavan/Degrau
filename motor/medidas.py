# Degrau — medidas das figuras e conferência dos rótulos (a regra de ouro: figura e gabarito do mesmo cálculo).
# Ângulos em minutos inteiros (35°30' = 2130), para aceitar graus e minutos sem erro de arredondamento.
import re
from fractions import Fraction


def minutos(graus):
    """graus (pode ter fração: -35.5) -> minutos inteiros"""
    return round(graus * 60)


def gms(m):
    """minutos -> texto da resposta: 2130 -> "35°30'", 900 -> "15" """
    d, r = divmod(int(m), 60)
    return f'{d}' if r == 0 else f"{d}°{r}'"


def gms_rotulo(m):
    """minutos -> texto escrito na figura: 900 -> "15°", 2130 -> "35°30'" """
    d, r = divmod(int(m), 60)
    return f'{d}°' if r == 0 else f"{d}°{r}'"


_MEDIDA = re.compile(r"^(?:(\d+)°)?(?:(\d+)')?$")


def ler_medida(texto, exige_simbolo=False):
    """"35", "35°", "35°30'", "30'" -> minutos; None se não for medida"""
    s = str(texto).strip().replace(' ', '').replace('’', "'").replace('′', "'")
    if not exige_simbolo and re.fullmatch(r'\d+', s): return int(s) * 60
    m = _MEDIDA.fullmatch(s)
    if not s or not m or (m.group(1) is None and m.group(2) is None): return None
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


_EXPR = re.compile(r'^(\d*)([xy])(?:/(\d+))?(?:([+-])(.+))?$')


def ler_rotulo(rot):
    """('nome',) para identificação (1, a, B); ('valor', minutos); ('expr', var, coef, divisor, minutos)"""
    s = str(rot).strip().replace('−', '-').replace(' ', '')
    v = ler_medida(s, exige_simbolo=True)
    if v is not None: return ('valor', v)
    m = _EXPR.fullmatch(s)
    if m:
        b = 0
        if m.group(4):
            b = ler_medida(m.group(5))
            if b is None: raise ValueError(f'rótulo {rot!r}: não entendi a parte {m.group(5)!r}')
            if m.group(4) == '-': b = -b
        return ('expr', m.group(2), int(m.group(1) or 1), int(m.group(3) or 1), b)
    return ('nome',)


def resolver(pares):
    """pares: [(ângulo desenhado em minutos, rótulo, onde)]. Confere valores escritos e expressões:
    cada incógnita (x, y) tem que dar o mesmo valor em todos os rótulos. Devolve {incógnita: minutos}."""
    achados = {}
    for valor, rot, onde in pares:
        if rot is None: continue
        r = ler_rotulo(rot)
        if r[0] == 'valor':
            if r[1] != valor:
                raise ValueError(f'rótulo {rot!r} {onde}, mas o ângulo desenhado é {gms_rotulo(valor)}')
        elif r[0] == 'expr':
            _, var, a, den, b = r
            x = Fraction(valor - b) * den / a          # valor = a·x/den + b
            if x.denominator != 1 or x < 0:
                raise ValueError(f'rótulo {rot!r} {onde} ({gms_rotulo(valor)}) dá {var} = {float(x) / 60:g}°, não exato')
            achados.setdefault(var, []).append((int(x), rot, onde))
    saida = {}
    for var, lista in achados.items():
        if len({x for x, _, _ in lista}) > 1:
            raise ValueError(f'os rótulos dão valores diferentes de {var}: '
                             + ', '.join(f'{r!r} {o} → {var} = {gms(x)}' for x, r, o in lista))
        saida[var] = lista[0][0]
    return saida


def arco(a, b):
    """(início, abertura) do menor ângulo entre as direções a e b, em graus"""
    a %= 360; b %= 360; d = (b - a) % 360
    return (a, d) if d <= 180 else (b, 360 - d)


# ---------- ângulos de cada figura: [(minutos, rótulo, onde)] ----------

def arco_bico(dirs, vi, lado):
    """(início, abertura) do arco do vértice vi do bico; dirs = direções dos segmentos"""
    if vi == 0:
        a = 0 if lado == 'dir' else 180; b = dirs[0]
    elif vi == len(dirs):
        a = 0 if lado == 'dir' else 180; b = dirs[-1] + 180
    else:
        a = dirs[vi - 1] + 180; b = dirs[vi]
    return arco(a, b)


POSICOES = ('acima-direita', 'acima-esquerda', 'abaixo-esquerda', 'abaixo-direita')


def arco_transversal(t, posicao):
    """(início, abertura) do ângulo na posição dada, num cruzamento de reta horizontal com a transversal t"""
    ini = {'acima-direita': 0, 'acima-esquerda': t, 'abaixo-esquerda': 180, 'abaixo-direita': t + 180}[posicao]
    fim = {'acima-direita': t, 'acima-esquerda': 180, 'abaixo-esquerda': t + 180, 'abaixo-direita': 360}[posicao]
    return ini % 360, fim - ini


def pares(tipo, d):
    if tipo == 'bico':
        dirs = [s[0] for s in d['segmentos']]
        return [(minutos(arco_bico(dirs, vi, lado)[1]), rot, f'no vértice {vi}') for vi, lado, rot in d['marcas']]
    if tipo == 'angulo':
        return [(minutos(arco(*d['direcoes'])[1]), d.get('rotulo'), 'no ângulo')]
    if tipo == 'semirretas':
        dirs = dict(zip(d['nomes'], d['direcoes']))
        return [(minutos(arco(dirs[p], dirs[q])[1]), m[3] if len(m) > 3 else None, f'entre {p} e {q}')
                for m in d.get('marcas', []) for p, q in [m[:2]]]
    if tipo == 'cruzadas':
        return [(minutos(arco(a, b)[1]), rot, f'entre {a:g}° e {b:g}°') for a, b, rot in d['marcas']]
    if tipo == 'transversal':
        return [(minutos(arco_transversal(d['direcao'], pos)[1]), rot, f'em {reta}, {pos}')
                for reta, pos, rot in d['marcas']]
    return []


def incognitas(fig):
    """{incógnita: minutos} de uma figura ({'bico': {...}} etc.), conferindo todos os rótulos"""
    tipo, d = next(iter(fig.items()))
    return resolver(pares(tipo, d))
