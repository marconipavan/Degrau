# Degrau — converte os esqueletos de folha (formato de docs/prompts/esqueletos-g1.md) para o YAML do motor.
# uso: .venv/bin/python ferramentas/esqueletos.py <pasta com G1_NNN.md> <curso>   (só grava folhas que não existem)
#      --sobrescrever regrava as que já existem; --mostrar N imprime o YAML de uma folha sem gravar
# Qualquer frase de figura que o conversor não conheça faz ele parar: nada é adivinhado.
import glob, os, re, sys
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from motor.especificacao import caminho_folha


class ErroConversao(Exception):
    pass


def _num(s):
    """'−35°30'' -> -35.5 ; '22,5°' -> 22.5"""
    s = s.strip().replace('−', '-').replace(',', '.')
    m = re.fullmatch(r"(-?)(\d+(?:\.\d+)?)°(?:(\d+)')?", s) or re.fullmatch(r"(-?)(\d+(?:\.\d+)?)()", s)
    if not m: raise ErroConversao(f'medida que não entendi: {s!r}')
    v = float(m.group(2)) + (int(m.group(3)) / 60 if m.group(3) else 0)
    v = -v if m.group(1) else v
    return int(v) if v == int(v) else round(v, 4)


def _rotulo(s):
    s = s.strip()
    return None if s in ('', 'nada') else s


IGNORAR = ('nos outros, nada', 'sem valor escrito', 'sem valores escritos', 'as semirretas dão a volta completa em O')


def figura(texto):
    partes = [p.strip() for p in texto.strip().split(';') if p.strip()]
    cab = partes[0]

    if cab.startswith('ângulo de vértice'):
        m = re.fullmatch(r'ângulo de vértice (\w), ponta (\w) na direção (\S+), ponta (\w) na direção (\S+)', cab)
        if not m: raise ErroConversao(f'ângulo: {cab!r}')
        d = {'direcoes': [_num(m.group(3)), _num(m.group(5))], 'nomes': [m.group(1), m.group(2), m.group(4)]}
        for p in partes[1:]:
            if p == 'marca de arco': d['marca'] = 'arco'
            elif p == 'marca de ângulo reto': d['marca'] = 'reto'
            elif p.startswith('escrever'): d['rotulo'] = _rotulo(p.split(':', 1)[1])
            elif p not in IGNORAR: raise ErroConversao(f'ângulo, parte desconhecida: {p!r}')
        return {'angulo': d}

    if cab.startswith('semirretas de mesma origem'):
        m = re.fullmatch(r'semirretas de mesma origem (\w): (.+)', cab)
        nomes, dirs = [], []
        for tok in m.group(2).split(', ') if m else []:
            n, a = tok.split(' ', 1); nomes.append(n); dirs.append(_num(a))
        # direções com vírgula decimal ("M 22,5°") se partem no split; junta de novo
        if not m or len(nomes) != len(dirs): raise ErroConversao(f'semirretas: {cab!r}')
        d = {'direcoes': dirs, 'nomes': nomes, 'vertice': m.group(1)}
        marcas, tracejadas, externas = [], [], []   # ângulo todo: por último, arco de raio maior
        for p in partes[1:]:
            q = re.sub(r'^escrever ', '', p)
            if q in IGNORAR or re.fullmatch(r'\w e \w formam uma reta', q): continue
            mm_ = re.fullmatch(r'marca de ângulo reto entre (\w) e (\w)', q)
            if mm_: marcas.append([mm_.group(1), mm_.group(2), 'reto', None]); continue
            mm_ = re.fullmatch(r'entre (\w) e (\w) \(o ângulo todo, arco externo\): (.+)', q)
            if mm_: externas.append([mm_.group(1), mm_.group(2), 'arco', _rotulo(mm_.group(3))]); continue
            mm_ = re.fullmatch(r'entre (\w) e (\w): (.+)', q)
            if mm_: marcas.append([mm_.group(1), mm_.group(2), None, _rotulo(mm_.group(3))]); continue
            mm_ = re.fullmatch(r'(O\w(?:, O\w)*) e (O\w) tracejadas?', q) or re.fullmatch(r'(O\w) tracejada', q)
            if mm_: tracejadas += [g[1] for g in re.findall(r'O\w', q)]; continue
            raise ErroConversao(f'semirretas, parte desconhecida: {p!r}')
        marcas += externas
        if marcas: d['marcas'] = marcas
        if tracejadas: d['tracejadas'] = tracejadas
        return {'semirretas': d}

    if cab.startswith('retas que se cruzam'):
        m = re.fullmatch(r'retas que se cruzam no ponto (\w), nas direções (\S+) \(e \S+\) e (\S+) \(e \S+\)', cab)
        if not m: raise ErroConversao(f'retas que se cruzam: {cab!r}')
        d = {'direcoes': [_num(m.group(2)), _num(m.group(3))], 'ponto': m.group(1), 'marcas': []}
        for p in partes[1:]:
            q = re.sub(r'^escrever ', '', p)
            if q in IGNORAR: continue
            mm_ = re.fullmatch(r'no ângulo entre (\S+) e (\S+): (.+)', q)
            if not mm_: raise ErroConversao(f'retas que se cruzam, parte desconhecida: {p!r}')
            d['marcas'].append([_num(mm_.group(1)), _num(mm_.group(2)), _rotulo(mm_.group(3))])
        return {'cruzadas': d}

    if cab.startswith('retas r (acima) e s (abaixo) horizontais e paralelas'):
        d = {'direcao': None, 'marcas': []}
        for p in partes[1:]:
            q = re.sub(r'^escrever: ?', '', p)
            if q in IGNORAR: continue
            mm_ = re.fullmatch(r'transversal t com direção (\S+)', q)
            if mm_: d['direcao'] = _num(mm_.group(1)); continue
            mm_ = re.fullmatch(r'em ([rs]), (acima|abaixo) à (direita|esquerda): (.+)', q)
            if not mm_: raise ErroConversao(f'transversal, parte desconhecida: {p!r}')
            d['marcas'].append([mm_.group(1), f'{mm_.group(2)}-{mm_.group(3)}', _rotulo(mm_.group(4))])
        if d['direcao'] is None: raise ErroConversao(f'transversal sem direção: {texto!r}')
        return {'transversal': d}

    if cab.startswith('bico entre paralelas'):
        m = re.fullmatch(r'bico entre paralelas: retas r \(acima\) e s \(abaixo\) horizontais, distância (\d+) mm', cab)
        if not m: raise ErroConversao(f'bico: {cab!r}')
        d = {'altura': int(m.group(1)), 'segmentos': [], 'marcas': []}
        for p in partes[1:]:
            q = re.sub(r'^escrever ', '', p)
            if q == 'poligonal começa em r' or q in IGNORAR: continue
            if q.startswith('segmentos nas direções '):
                for a, comp in re.findall(r'(\S+) \((\d+ mm|até s)\)', q[len('segmentos nas direções '):]):
                    d['segmentos'].append([_num(a), 0 if comp == 'até s' else int(comp.split()[0])])
                continue
            mm_ = re.fullmatch(r'em ([rs]) \((?:início|fim)\), lado (direito|esquerdo): (.+)', q)
            if mm_:
                vi = 0 if mm_.group(1) == 'r' else None
                d['marcas'].append([vi, 'dir' if mm_.group(2) == 'direito' else 'esq', _rotulo(mm_.group(3))]); continue
            mm_ = re.fullmatch(r'no vértice (\d+): (.+)', q)
            if mm_: d['marcas'].append([int(mm_.group(1)), None, _rotulo(mm_.group(2))]); continue
            raise ErroConversao(f'bico, parte desconhecida: {p!r}')
        fim = len(d['segmentos'])
        d['marcas'] = [[fim if vi is None else vi, lado, rot] for vi, lado, rot in d['marcas']]
        return {'bico': d}

    raise ErroConversao(f'figura desconhecida: {cab!r}')


def _semirretas_com_decimal(texto):
    """'A 0°, M 22,5°, B 45°' tem vírgula decimal: troca por ponto antes de separar por ', '"""
    return re.sub(r'(\d),(\d)', r'\1.\2', texto)


def item(linha):
    campos = {}
    for parte in re.sub(r'^\d+\.\s*', '', linha).split(' | '):
        k, _, v = parte.partition(': ')
        campos[k.strip()] = v.strip()
    it = {'texto': campos['Enunciado']}
    if 'Figura' in campos and campos['Figura'] != 'a mesma figura':
        it['_figura'] = figura(_semirretas_com_decimal(campos['Figura']))
    elif campos.get('Figura') == 'a mesma figura':
        it['_mesma'] = True
    if 'Alternativas' in campos:
        it['alternativas'] = [a.strip() for _, a in re.findall(r'\(([A-E])\)\s*(.+?)(?=\s*\([A-E]\)|$)', campos['Alternativas'])]
    resp = campos['Resposta']
    if resp.endswith('(conjunto, qualquer ordem)'):
        it['resposta'] = {'conjunto': [x.strip() for x in resp.replace('(conjunto, qualquer ordem)', '').split(',')]}
    else:
        aceitas = [resp] + [a.strip() for a in campos.get('Aceitar também', '').split(';') if a.strip()]
        it['resposta'] = list(dict.fromkeys(aceitas)) if len(aceitas) > 1 else resp
    m = re.search(r'(?:Ache|Calcule|Encontre|valor de|vale)\s+([xy])\s*(?:é|\.|:|\?|$)', it['texto'])
    if m: it['incognita'] = m.group(1)
    if 'Fonte' in campos: it['_fonte'] = campos['Fonte']
    return it


def pagina(texto):
    campos, itens = {}, []
    for l in texto.splitlines():
        if re.match(r'^\d+\. ', l): itens.append(item(l))
        elif ': ' in l and not l.startswith('Itens'):
            k, _, v = l.partition(': '); campos[k.strip()] = v.strip()
    lado = {'instrucao': campos['Instrução'], 'icone': 'escrever'}
    pts = campos.get('Pontos', '')
    m = re.fullmatch(r'(\d+) cada', pts)
    if m: lado['pontos_cada'] = int(m.group(1))
    elif pts: lado['pontos'] = 100
    blocos = []
    if campos.get('Exemplo resolvido'): blocos.append({'exemplo': {'texto': [campos['Exemplo resolvido']]}})
    figs = [it.get('_figura') for it in itens]
    compartilhada = bool(itens) and figs[0] and all(it.get('_mesma') for it in itens[1:])
    questao = any('alternativas' in it for it in itens)
    saida = []
    for it in itens:
        f = it.pop('_figura', None); it.pop('_mesma', None); it.pop('_fonte', None)
        if f and not compartilhada:
            if 'semirretas' in f:   # uma figura por item: semirretas menores, se não houver ângulo muito fechado
                ds = sorted(f['semirretas']['direcoes'])
                f['semirretas']['comprimento'] = 15 if min(b - a for a, b in zip(ds, ds[1:])) >= 20 else 17
            it.update(f)
        saida.append(it)
    if compartilhada:
        blocos.append({'figura': figs[0]})
    textos = [len(it['texto']) for it in saida]
    if questao: colunas = 1
    elif any(k in it for it in saida for k in ('bico', 'transversal')): colunas = 1 if len(saida) <= 2 else 2
    elif any(k in it for it in saida for k in ('angulo', 'semirretas', 'cruzadas')): colunas = 2
    else: colunas = 2 if max(textos) <= 24 else 1
    blocos.append({'grade': {'colunas': colunas, 'itens': saida}})
    lado['blocos'] = blocos
    return lado


def folha(caminho):
    texto = open(caminho, encoding='utf-8').read()
    m = re.match(r'# (\w+ \d+) — (.+)', texto)
    if not m: raise ErroConversao(f'{caminho}: cabeçalho fora do formato')
    secoes = re.split(r'^## ', texto, flags=re.M)[1:]
    if len(secoes) != 2: raise ErroConversao(f'{caminho}: esperava frente e verso')
    try:
        return {'folha': m.group(1), 'unidade': m.group(2).strip(), 'a': pagina(secoes[0]), 'b': pagina(secoes[1])}
    except ErroConversao as e:
        raise ErroConversao(f'{os.path.basename(caminho)}: {e}') from None


def gravar(d, destino, origem):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, 'w', encoding='utf-8') as f:
        f.write(f'# convertido de {os.path.basename(origem)} (esqueletos gerados numa conversa do Claude; revisar)\n')
        yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False, width=110, default_flow_style=None)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    pasta, curso = args[0], args[1]
    if '--mostrar' in sys.argv:
        n = int(args[2]); print(yaml.safe_dump(folha(os.path.join(pasta, f'G1_{n:03d}.md')), allow_unicode=True,
                                               sort_keys=False, width=110, default_flow_style=None)); sys.exit()
    gravadas = puladas = 0
    for caminho in sorted(glob.glob(os.path.join(pasta, '*_[0-9][0-9][0-9].md'))):
        d = folha(caminho)
        destino = caminho_folha(curso, d['folha'])
        if os.path.exists(destino) and '--sobrescrever' not in sys.argv:
            puladas += 1; continue
        gravar(d, destino, caminho); gravadas += 1
    print(f'{gravadas} gravada(s), {puladas} já existia(m)')
