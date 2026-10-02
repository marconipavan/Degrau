# Degrau — ferramentas para quem escreve as folhas: validar a biblioteca, ver uma folha, exportar o gabarito.
import glob, os, re, sys
from . import especificacao as esp
from .especificacao import ErroEspecificacao, carregar_curso, carregar_folha, biblioteca
from .gabarito import respostas_folha, linhas_planilha, escrever_planilha_biblioteca
from .verificar import verificar_folha


def _faixas(nums):
    """[4, 5, 6, 9] -> '4-6, 9'"""
    saida, ini = [], None
    for i, n in enumerate(nums):
        if ini is None: ini = n
        if i + 1 == len(nums) or nums[i + 1] != n + 1:
            saida.append(f'{ini}' if ini == n else f'{ini}-{n}'); ini = None
    return ', '.join(saida)


def _nome_esperado(curso, codigo):
    nivel, num = codigo.split(); num = int(num)
    n = next((n for n in curso['niveis'] if n['codigo'] == nivel), {})
    for u in n.get('unidades', []):
        a, b = u['folhas']
        if a <= num <= b: return f'{u["nome"]} {num - a + 1}'
    return None


def validar(cursos):
    if not cursos:
        cursos = sorted(os.path.basename(d) for d in glob.glob(os.path.join(esp.RAIZ, 'folhas', '*')) if os.path.isdir(d))
    total_erros = 0
    for nome in cursos:
        curso = carregar_curso(nome)
        caderno = curso['folha']['campos'] == 'caderno'
        lista = biblioteca(nome)
        ok = 0
        print(f'== {nome}: {len(lista)} arquivo(s)')
        for cod, v in lista:
            rotulo = cod + (f' v{v}' if v > 1 else '')
            try:
                folha = carregar_folha(nome, cod, v)
                erros = verificar_folha(folha, curso)      # blocos, layout, margens, sobreposição
                respostas_folha(folha)                     # gabarito e expressões dos bicos
                if caderno: linhas_planilha(folha, curso)  # até 12 itens por página do formulário
            except ErroEspecificacao as e:
                erros = [str(e).replace(esp.RAIZ + os.sep, '')]
            if erros:
                total_erros += 1
                print(f'  ERRO {rotulo}:'); [print('       ' + e) for e in erros]
            else:
                ok += 1
                esperado = _nome_esperado(curso, cod)
                if esperado and folha['unidade'] != esperado:
                    print(f'  aviso {rotulo}: unidade "{folha["unidade"]}"; pelo currículo seria "{esperado}"')
        print(f'  {ok} ok, {len(lista) - ok} com erro')
        escritas = {c for c, v in lista if v == 1}
        for n in curso['niveis']:
            nums = [k for k in range(1, n.get('folhas', 0) + 1) if f'{n["codigo"]} {k}' not in escritas]
            if n.get('folhas') and len(nums) < n['folhas']:   # só níveis já começados
                print(f'  faltam no {n["codigo"]} ({len(nums)}): {_faixas(nums) or "nenhuma"}')
    return 1 if total_erros else 0


def _curso_do_nivel(nivel):
    achados = [os.path.basename(os.path.dirname(d)) for d in glob.glob(os.path.join(esp.RAIZ, 'folhas', '*', nivel))]
    if len(achados) != 1:
        raise ErroEspecificacao(f'nível {nivel}: encontrado em {achados or "nenhum curso"}')
    return achados[0]


def ver(codigo, versao):
    m = re.fullmatch(r'\s*(\w+)\s+(\d+)(?:-(\d+))?\s*', ' '.join(codigo))
    if not m: raise ErroEspecificacao('use: degrau ver G1 12  ou  degrau ver G1 4-6')
    nivel, de, ate = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
    nome = _curso_do_nivel(nivel)
    curso = carregar_curso(nome)
    folhas = [f'{nivel} {k}' for k in range(de, ate + 1)]
    for f in folhas:   # mostra os problemas antes de tentar desenhar
        problemas = verificar_folha(carregar_folha(nome, f, versao), curso)
        for p in problemas: print('  problema:', p)
    from .render import gerar_pacote
    sufixo = f'_v{versao}' if versao > 1 else ''
    bloco = (f'{nivel} {de}' if de == ate else f'{nivel} {de}-{ate}') + (f' v{versao}' if versao > 1 else '')
    arquivos, esconder = gerar_pacote({'arquivo': f'{nivel}_{de}-{ate}{sufixo}.pdf', 'titulo': f'Prévia {bloco}',
                                       'curso': nome, 'folhas': folhas, 'versoes': [versao] * len(folhas),
                                       'blocos': [bloco] * len(folhas)}, os.path.join(esp.RAIZ, 'saida', 'ver'))
    print(arquivos[0])
    for f in folhas:   # numeração por página = a dos campos do formulário
        contagem = {}
        for l in respostas_folha(carregar_folha(nome, f, versao)):
            k = contagem[l['pagina']] = contagem.get(l['pagina'], 0) + 1
            print(f'  {l["pagina"]} · {k}: {" | ".join(l["respostas"]) or "(correção manual)"}'
                  + (f'  [{l["pontos"]}]' if l['pontos'] is not None else ''))
    return 0


def executar(a):
    if a.comando == 'validar': sys.exit(validar(a.cursos))
    if a.comando == 'ver': return ver(a.codigo, a.versao)
    curso = carregar_curso(a.curso)
    destino = a.arquivo or os.path.join(esp.RAIZ, 'saida', f'gabarito-{a.curso}.csv')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    escrever_planilha_biblioteca(curso, destino)
    print(destino)
