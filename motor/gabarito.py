# Degrau — gabarito a partir das especificações (sem desenhar nada)
import csv
from .especificacao import ErroEspecificacao
from .bicos import angulos, resolver_x

MAX_ITENS_PAGINA = 12   # campos por página no formulário do CASD


def _lista(r):
    """respostas aceitas; {conjunto: [...]} = itens em qualquer ordem (o script de correção entende)"""
    if isinstance(r, dict) and list(r) == ['conjunto']:
        return ['conjunto:' + ','.join(str(x) for x in r['conjunto'])]
    return [str(x) for x in r] if isinstance(r, list) else [str(r)]


def _x_bico(bico, onde):
    """x dos rótulos do bico, conferido contra os ângulos calculados"""
    marks = [tuple(m) for m in bico['marcas']]
    try:
        return resolver_x(marks, angulos([d for d, _ in bico['segmentos']], marks))
    except ValueError as e:
        raise ErroEspecificacao(f'{onde}: {e}') from None


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
            elif tipo == 'exemplo' and 'bico' in d.get('figura', {}):
                _x_bico(d['figura']['bico'], onde + ', figura')
            elif tipo == 'figura' and 'bico' in d:
                x_pagina = _x_bico(d['bico'], onde)
            elif tipo == 'grade':
                for i, it in enumerate(d['itens'], 1):
                    x = _x_bico(it['bico'], f'{onde}, item {i}') if 'bico' in it else None
                    if 'resposta' in it:
                        if x is not None and _lista(it['resposta']) != [str(x)]:
                            raise ErroEspecificacao(f'{onde}, item {i}: resposta {it["resposta"]} mas os rótulos dão x = {x}')
                        its.append((_lista(it['resposta']), None))
                    elif x is not None:
                        its.append(([str(x)], None))
                    else:
                        raise ErroEspecificacao(f'{onde}, item {i}: sem resposta (escreva resposta ou marque o x no bico)')
            elif tipo == 'alternativas':
                letra = d['resposta']; texto = d['itens'][ord(letra) - 65]
                if x_pagina is not None and texto.replace('°', '').strip() != str(x_pagina):
                    raise ErroEspecificacao(f'{onde}: alternativa {letra} ({texto}), mas a figura dá x = {x_pagina}')
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


def escrever_planilha(folhas, curso, caminho):
    """Aba Gabarito da planilha do CASD: uma linha por campo do formulário.
    Campo = '<k>ª folha (<lado>) · <n>', com k a posição da folha no bloco diário."""
    por_bloco = curso['bloco_diario']['folhas']
    tempos = {n['codigo']: max(n['tempo_padrao_min']) for n in curso['niveis'] if 'tempo_padrao_min' in n}
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Bloco', 'Campo', 'Respostas aceitas', 'Pontos', 'Tempo-padrão do bloco (min)'])
        for i in range(0, len(folhas), por_bloco):
            grupo = folhas[i:i + por_bloco]
            nivel = grupo[0]['folha'].split()[0]
            nums = [g['folha'].split()[1] for g in grupo]
            codigo = f'{nivel} {nums[0]}-{nums[-1]}'
            if nivel not in tempos:
                raise ErroEspecificacao(f'currículo {curso["curso"]}: nível {nivel} sem tempo_padrao_min')
            tempo = tempos[nivel] * len(grupo)   # soma dos tempos-padrão das folhas
            for k, folha in enumerate(grupo, 1):
                linhas = respostas_folha(folha)
                for lado in 'ab':
                    da_pagina = [l for l in linhas if l['pagina'].endswith(lado)]
                    if len(da_pagina) > MAX_ITENS_PAGINA:
                        raise ErroEspecificacao(f'{folha["_caminho"]}, lado {lado}: {len(da_pagina)} itens; '
                                                f'o formulário tem {MAX_ITENS_PAGINA} campos por página')
                    for n, l in enumerate(da_pagina, 1):
                        w.writerow([codigo, f'{k}ª folha ({lado}) · {n}', '|'.join(l['respostas']),
                                    '' if l['pontos'] is None else l['pontos'], tempo])
