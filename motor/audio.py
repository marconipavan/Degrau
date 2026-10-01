# Degrau — bloco de áudio do pacote, para colar no leitor (leitor/leitor-frances.html)
# Convenção: cada folha abre com "Feuille N x."; falas de personagem em linha própria, "[Nome] fala".
import re

_U = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix', 'onze',
      'douze', 'treize', 'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf']
_D = {2: 'vingt', 3: 'trente', 4: 'quarante', 5: 'cinquante', 6: 'soixante'}

def numero_fr(n):
    """1 a 199 por extenso em francês"""
    if n < 20: return _U[n]
    if n < 70:
        d, u = divmod(n, 10)
        return _D[d] if u == 0 else _D[d] + (' et un' if u == 1 else '-' + _U[u])
    if n < 80: return 'soixante' + (' et onze' if n == 71 else '-' + _U[n - 60])
    if n < 100: return 'quatre-vingts' if n == 80 else 'quatre-vingt-' + _U[n - 80]
    if n < 200: return 'cent' + ('' if n == 100 else ' ' + numero_fr(n - 100))
    raise ValueError(f'número {n} fora do intervalo')

def _maiuscula(s): return s[:1].upper() + s[1:]

def _ponto(s): return s if s[-1:] in '.!?»' else s + '.'

_FALA = re.compile(r'^(.+?)\s*:\s*«\s*(.+?)\s*»\s*$')   # "L'hôtesse : « Bienvenue ! »"

def _linha_leitura(l):
    m = _FALA.match(l)
    return f'[{m.group(1)}] {m.group(2)}' if m else l

# blocos em que o áudio contém a resposta: avisar para esconder o texto
COM_RESPOSTA = {'circular', 'ditado'}


def faixas(folha):
    """[(página, texto da faixa, esconder_texto)] das páginas que têm áudio"""
    num = numero_fr(int(folha['folha'].split()[1]))
    saida = []
    for lado in 'ab':
        linhas, esconder = [], False
        for bloco in folha[lado]['blocos']:
            tipo, d = next(iter(bloco.items()))
            if isinstance(d, list): d = {'itens': d}
            if tipo == 'palavras':
                linhas.append(' '.join(_ponto(_maiuscula(p[0])) for p in d['itens']))
            elif tipo == 'frases':
                linhas += [_ponto(i[0] if isinstance(i, list) else i) for i in d['itens']]
            elif tipo == 'circular':
                linhas += [f'{_maiuscula(numero_fr(n))}. {_ponto(_maiuscula(it["resposta"]))}' for n, it in enumerate(d['itens'], 1)]
            elif tipo == 'leitura':
                linhas += [_linha_leitura(l) for l in d['linhas']]
            elif tipo == 'ditado':
                linhas += [f'{_maiuscula(numero_fr(n))}. {_ponto(it["resposta"])}' for n, it in enumerate(d['itens'], 1)]
            else:
                continue
            esconder |= tipo in COM_RESPOSTA
        if linhas:
            saida.append((f'{folha["folha"]}{lado}', '\n'.join([f'Feuille {num} {lado}.'] + linhas), esconder))
    return saida


def escrever(folhas, caminho):
    """grava o bloco de áudio; devolve as páginas em que é preciso esconder o texto (ou None se não há áudio)"""
    todas = [fx for folha in folhas for fx in faixas(folha)]
    if not todas: return None
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write('\n'.join(texto for _, texto, _ in todas) + '\n')
    return [pag for pag, _, esc in todas if esc]
