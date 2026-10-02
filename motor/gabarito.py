# Degrau — gabarito a partir das especificações (sem desenhar nada)
import csv
from .especificacao import ErroEspecificacao, carregar_folha
from .medidas import incognitas, ler_medida, gms

FIGURAS = ('angulo', 'semirretas', 'bico', 'cruzadas', 'transversal')

MAX_ITENS_PAGINA = 12   # campos por página no formulário do CASD


def _lista(r):
    """respostas aceitas; {conjunto: [...]} = itens em qualquer ordem (o script de correção entende)"""
    if isinstance(r, dict) and list(r) == ['conjunto']:
        return ['conjunto:' + ','.join(str(x) for x in r['conjunto'])]
    return [str(x) for x in r] if isinstance(r, list) else [str(r)]


def _incognitas(item, onde):
    """{x: minutos, y: ...} da figura do item (ou {}), conferindo todos os rótulos contra os ângulos desenhados"""
    fig = {k: v for k, v in item.items() if k in FIGURAS}
    if not fig: return {}
    try:
        return incognitas(fig)
    except (ValueError, KeyError) as e:
        raise ErroEspecificacao(f'{onde}: {e}') from None


def _confere(texto, valor, var, onde):
    m = ler_medida(texto)
    if m is not None and m != valor:
        raise ErroEspecificacao(f'{onde}: resposta {texto} mas a figura dá {var} = {gms(valor)}')


def _pares_ligar(d, folha):
    if 'itens_de' in d:
        return next(iter(folha[d['itens_de']]['blocos'][0].values()))['itens']
    return d['itens']


def respostas_folha(folha):
    """Linhas do gabarito: {pagina, bloco, item, respostas, pontos}. Itens sem
    resposta escrita (perguntas abertas) saem com respostas vazias."""
    linhas = []
    for lado in 'ab':
        L = folha[lado]; pagina = f'{folha["folha"]}{lado}'
        onde_lado = f'{folha["_caminho"]}, lado {lado}'
        cada, total = L.get('pontos_cada'), L.get('pontos')
        x_pagina = None
        da_pagina = []
        for b, bloco in enumerate(L['blocos'], 1):
            tipo, d = next(iter(bloco.items()))
            if isinstance(d, list): d = {'itens': d}
            onde = f'{onde_lado}, bloco {b} ({tipo})'
            its = []   # (respostas, pontos do item ou None)
            if tipo == 'subinstrucao':
                cada, total = d.get('pontos_cada'), d.get('pontos')
            elif tipo == 'ligar':
                its = [([p[1]], None) for p in _pares_ligar(d, folha)]
            elif tipo == 'copiar':
                its = [([w], None) for w in d['itens']]
            elif tipo in ('circular', 'lacunas', 'verdadeiro-falso', 'ordenar'):
                its = [(_lista(it['resposta']), None) for it in d['itens']]
            elif tipo == 'ditado':
                its = [(_lista(it['resposta']), d.get('pontos_cada')) for it in d['itens']]
            elif tipo == 'perguntas':
                its = [(_lista(it['resposta']) if 'resposta' in it else [], it.get('pontos')) for it in d['itens']]
            elif tipo == 'decompor':
                its = [([' / '.join(_lista(it['resposta']))] if 'resposta' in it else [], None) for it in d['itens']]
            elif tipo == 'exemplo' and d.get('figura'):
                _incognitas(d['figura'], onde + ', figura')
            elif tipo == 'figura':
                x_pagina = _incognitas(d, onde) or None
            elif tipo == 'grade':
                for i, it in enumerate(d['itens'], 1):
                    o = f'{onde}, item {i}'
                    proprias = _incognitas(it, o)
                    var = it.get('incognita', 'x')
                    # sem figura própria, a pergunta pode ser sobre a figura da página ("Ache y.")
                    fonte = proprias or ((x_pagina or {}) if 'incognita' in it else {})
                    if 'alternativas' in it:
                        letra = it['resposta']; letras = [chr(65 + k) for k in range(len(it['alternativas']))]
                        if letra not in letras: raise ErroEspecificacao(f'{o}: resposta deve ser uma de {", ".join(letras)}')
                        if 'incognita' in it and var in fonte:   # "O valor de x é" (e não "a medida de AÔB")
                            _confere(it['alternativas'][ord(letra) - 65], fonte[var], var, o + f', alternativa {letra}')
                        its.append(([letra], it.get('pontos')))
                    elif 'resposta' in it:
                        # compara com x só se a pergunta é x (incógnita declarada) ou se o item é só a figura
                        if var in fonte and ('incognita' in it or 'texto' not in it):
                            _confere(_lista(it['resposta'])[0], fonte[var], var, o)
                        its.append((_lista(it['resposta']), it.get('pontos')))
                    elif var in fonte:
                        its.append(([gms(fonte[var])], it.get('pontos')))
                    else:
                        raise ErroEspecificacao(f'{o}: sem resposta (escreva resposta ou marque o x na figura)')
            elif tipo == 'alternativas':
                letra = d['resposta']; texto = d['itens'][ord(letra) - 65]
                if x_pagina and 'x' in x_pagina: _confere(texto, x_pagina['x'], 'x', f'{onde}: alternativa {letra} ({texto})')
                its = [([letra], None)]
            for n, (resp, pts) in enumerate(its, 1):
                da_pagina.append({'pagina': pagina, 'bloco': b, 'item': n, 'respostas': resp,
                                  'pontos': pts if pts is not None else cada})
        if total is not None and cada is None:   # "[100]" é o total da página
            for l in da_pagina:
                if l['pontos'] is None:
                    v = total / len(da_pagina); l['pontos'] = int(v) if v == int(v) else round(v, 2)
        linhas += da_pagina
    return linhas


def escrever_csv(linhas, caminho):
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Página', 'Bloco', 'Item', 'Respostas aceitas', 'Pontos'])
        for l in linhas:
            w.writerow([l['pagina'], l['bloco'], l['item'], '|'.join(l['respostas']),
                        '' if l['pontos'] is None else l['pontos']])


CABECALHO_PLANILHA = ['Folha', 'Versão', 'Página', 'Item', 'Respostas aceitas', 'Pontos', 'Tempo-padrão da folha (min)']


def linhas_planilha(folha, curso):
    """Linhas da aba Gabarito para uma folha: uma por item com resposta, numeradas como no formulário
    (o campo do formulário é '<k>ª folha (<página>) · <item>', k = posição da folha no bloco)."""
    nivel = folha['folha'].split()[0]
    n = next((n for n in curso['niveis'] if n['codigo'] == nivel and 'tempo_padrao_min' in n), None)
    if n is None:
        raise ErroEspecificacao(f'currículo {curso["curso"]}: nível {nivel} sem tempo_padrao_min')
    tempo = max(n['tempo_padrao_min'])
    linhas, saida = respostas_folha(folha), []
    for lado in 'ab':
        da_pagina = [l for l in linhas if l['pagina'].endswith(lado)]
        if len(da_pagina) > MAX_ITENS_PAGINA:
            raise ErroEspecificacao(f'{folha["_caminho"]}, lado {lado}: {len(da_pagina)} itens; '
                                    f'o formulário tem {MAX_ITENS_PAGINA} campos por página')
        for k, l in enumerate(da_pagina, 1):
            saida.append([folha['folha'], folha.get('_versao', 1), lado, k, '|'.join(l['respostas']),
                          '' if l['pontos'] is None else l['pontos'], tempo])
    return saida


def escrever_planilha(folhas, curso, caminho):
    """Linhas da aba Gabarito (por folha e versão) para as folhas dadas, sem repetir folha."""
    vistas = set()
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(CABECALHO_PLANILHA)
        for folha in folhas:
            chave = (folha['folha'], folha.get('_versao', 1))
            if chave in vistas: continue
            vistas.add(chave)
            w.writerows(linhas_planilha(folha, curso))


def escrever_planilha_biblioteca(curso, caminho):
    """Aba Gabarito inteira: todas as folhas escritas do curso, em todas as versões. Carrega-se uma vez
    na planilha (e de novo quando entrarem folhas novas)."""
    from .especificacao import biblioteca
    escrever_planilha([carregar_folha(curso['curso'], c, v) for c, v in biblioteca(curso['curso'])], curso, caminho)
