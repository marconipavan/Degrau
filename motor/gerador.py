# Degrau — gerador de pacotes: decide as próximas folhas pelo estado do aluno e pelas regras do método.
#
# Regras (CLAUDE.md, seção 3):
# - Domínio = nota >= nota mínima do curso E tempo <= soma dos tempos-padrão das folhas.
# - A próxima folha é a primeira, na ordem do currículo a partir do início do aluno, ainda sem domínio.
#   Sem domínio, o trecho volta com exercícios novos (a versão seguinte de cada folha).
# - Pacote pendente (não corrigido) bloqueia o próximo: o pendente vem primeiro.
import os
from datetime import date
from .especificacao import ErroEspecificacao, carregar_curso, caminho_folha
from .render import gerar_pacote


def folhas_por_unidade(curso):
    if 'pacote' in curso: return curso['pacote']['folhas_por_dia']
    return curso['bloco_diario']['folhas']


def sequencia(curso, inicio):
    """códigos das folhas na ordem do currículo, a partir de inicio ('6A 1')"""
    nivel0, num0 = inicio.split(); num0 = int(num0)
    niveis = [n['codigo'] for n in curso['niveis']]
    if nivel0 not in niveis: raise ErroEspecificacao(f'nível {nivel0} não está no currículo {curso["curso"]}')
    for n in curso['niveis'][niveis.index(nivel0):]:
        if 'folhas' not in n:
            raise ErroEspecificacao(f'currículo {curso["curso"]}: nível {n["codigo"]} sem número de folhas')
        for k in range(num0 if n['codigo'] == nivel0 else 1, n['folhas'] + 1):
            yield f'{n["codigo"]} {k}'


def dominadas(estado):
    return {f for u in estado['unidades'] if u['status'] == 'dominio' for f in u['folhas']}


def proxima_folha(estado, curso):
    feitas = dominadas(estado)
    return next((f for f in sequencia(curso, estado['inicio']) if f not in feitas), None)


def _tempo(curso, folha):
    nivel = folha.split()[0]
    n = next(n for n in curso['niveis'] if n['codigo'] == nivel)
    return max(n['tempo_padrao_min'])


def _codigo(folhas):
    """'6A 6-10'; se cruzar de nível, '6A 99-5A 3'"""
    (n1, a), (n2, b) = folhas[0].split(), folhas[-1].split()
    return f'{n1} {a}-{b}' if n1 == n2 else f'{folhas[0]}-{folhas[-1]}'


def pendentes(estado):
    return [u for u in estado['unidades'] if u['status'] == 'pendente']


def planejar(estado, dias=1):
    """Folhas do próximo pacote: {'curso', 'unidades': [[folha, ...], ...], 'todas', 'versoes',
    'faltam': [(folha, versão, caminho)]}. Não grava nada."""
    curso = carregar_curso(estado['curso'])
    pend = pendentes(estado)
    if pend:
        raise ErroEspecificacao('pacote pendente: ' + ', '.join(f'{u["codigo"]} ({u["arquivo"]})' for u in pend)
                                + '. O pendente vem primeiro: registre a correção com "degrau registrar".')
    feitas, k = dominadas(estado), folhas_por_unidade(curso)
    livres = (f for f in sequencia(curso, estado['inicio']) if f not in feitas)
    unidades = []
    for _ in range(dias):
        fs = [f for _, f in zip(range(k), livres)]
        if not fs: break
        unidades.append(fs)
    if not unidades: raise ErroEspecificacao('currículo concluído: não há folhas sem domínio')
    # versão = quantas vezes a folha já saiu + 1 (repetição usa exercícios novos)
    saidas = {}
    for u in estado['unidades']:
        for f in u['folhas']: saidas[f] = saidas.get(f, 0) + 1
    todas = [f for fs in unidades for f in fs]
    versoes = [saidas.get(f, 0) + 1 for f in todas]
    faltam = [(f, v, caminho_folha(curso['curso'], f, v)) for f, v in zip(todas, versoes)
              if not os.path.exists(caminho_folha(curso['curso'], f, v))]
    return {'curso': curso, 'unidades': unidades, 'todas': todas, 'versoes': versoes, 'faltam': faltam}


def proximo(estado, dias=1, hoje=None, saida='pacotes'):
    """Gera o próximo pacote (dias = unidades diárias no pacote) e o registra como pendente.
    Devolve (arquivos gerados, páginas em que é preciso esconder o texto)."""
    p = planejar(estado, dias)
    curso, unidades, todas, versoes = p['curso'], p['unidades'], p['todas'], p['versoes']
    if p['faltam']:
        raise ErroEspecificacao('faltam folhas na biblioteca (escreva antes de gerar; versão 2 em diante = '
                                'exercícios novos para a repetição):\n  '
                                + '\n  '.join(os.path.relpath(c) for _, _, c in p['faltam']))
    hoje = hoje or date.today().isoformat()
    n = max((u['pacote'] for u in estado['unidades']), default=0) + 1
    nivel, de = todas[0].split(); ate = todas[-1].split()[1]
    arquivo = curso['folha'].get('arquivo', 'Pacote_{pacote:03d}_{nivel}_{de}-{ate}.pdf').format(
        pacote=n, nivel=nivel, de=de, ate=ate)
    titulo = f'Pacote {n} — ' + ', '.join(_codigo(fs) for fs in unidades)
    arquivos, esconder = gerar_pacote({'arquivo': arquivo, 'titulo': titulo, 'curso': curso['curso'],
                                       'folhas': todas, 'versoes': versoes}, saida)
    i = 0
    for fs in unidades:
        estado['unidades'].append({'pacote': n, 'codigo': _codigo(fs), 'folhas': fs, 'versoes': versoes[i:i + len(fs)],
                                   'data': hoje, 'limite_min': sum(_tempo(curso, f) for f in fs),
                                   'status': 'pendente', 'nota': None, 'tempo_min': None, 'arquivo': arquivo})
        i += len(fs)
    return arquivos, esconder


def registrar(estado, codigo, nota, tempo=None):
    """Registra a correção da unidade pendente 'codigo' e decide domínio ou repetição."""
    curso = carregar_curso(estado['curso'])
    alvo = [u for u in estado['unidades'] if u['codigo'] == codigo and u['status'] == 'pendente']
    if not alvo:
        pend = [u['codigo'] for u in estado['unidades'] if u['status'] == 'pendente']
        raise ErroEspecificacao(f'não há unidade pendente {codigo!r}; pendentes: {", ".join(pend) or "nenhuma"}')
    u = alvo[0]
    u['nota'], u['tempo_min'] = nota, tempo
    ok_tempo = tempo is None or tempo <= u['limite_min']
    u['status'] = 'dominio' if nota >= curso['dominio']['nota_minima'] and ok_tempo else 'repetir'
    return u
