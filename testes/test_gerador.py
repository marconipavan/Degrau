# Fase 4: gerador de pacotes. Aceite: 5 dias seguidos de francês e 2 pacotes de geometria sem editar código.
# A biblioteca de teste é temporária: cópias renumeradas das folhas reais (o conteúdo não importa aqui).
import os, re, shutil
import pytest
from motor import especificacao, estado as E
from motor.especificacao import ErroEspecificacao, RAIZ
from motor.gerador import proximo, registrar, proxima_folha
from motor.especificacao import carregar_curso
from conftest import TEM_FRANCES, requer_frances


def _copiar(origem, destino, codigo):
    t = open(origem, encoding='utf-8').read()
    t = re.sub(r'^folha: .*$', f'folha: {codigo}', t, count=1, flags=re.M)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    open(destino, 'w', encoding='utf-8').write(t)


@pytest.fixture
def biblioteca(tmp_path, monkeypatch):
    shutil.copytree(os.path.join(RAIZ, 'curriculos'), tmp_path / 'curriculos')
    fr = os.path.join(RAIZ, 'folhas', 'frances-delf-b1', '6A')
    for n in (range(1, 26) if TEM_FRANCES else []):
        _copiar(os.path.join(fr, f'{(n - 1) % 5 + 1}.yaml'), str(tmp_path / f'folhas/frances-delf-b1/6A/{n}.yaml'), f'6A {n}')
    for n in (range(6, 11) if TEM_FRANCES else []):   # exercícios novos para repetir 6A 6-10
        _copiar(os.path.join(fr, f'{n % 5 + 1}.yaml'), str(tmp_path / f'folhas/frances-delf-b1/6A/{n}.v2.yaml'), f'6A {n}')
    g = os.path.join(RAIZ, 'folhas', 'geometria-plana-epcar', 'G1')
    for n in range(1, 13):
        _copiar(os.path.join(g, f'{(n - 1) % 3 + 1}.yaml'), str(tmp_path / f'folhas/geometria-plana-epcar/G1/{n}.yaml'), f'G1 {n}')
    monkeypatch.setattr(especificacao, 'RAIZ', str(tmp_path))
    return tmp_path


def _novo(curso, inicio, aluno='Teste'):
    return {'curso': curso, 'aluno': aluno, 'inicio': inicio, 'unidades': [],
            'vocabulario': {}, 'estruturas': {}, 'erros_recorrentes': []}


@requer_frances
def test_cinco_dias_de_frances(biblioteca):
    est, saida, caminho = _novo('frances-delf-b1', '6A 1'), str(biblioteca / 'pacotes'), str(biblioteca / 'est.json')
    # (dia, nota, tempo) -> esperado: pacote gerado no dia e status depois da correção
    dias = [('2026-10-01', 95, 9,  '6A 1-5',   [1] * 5, 'dominio'),
            ('2026-10-02', 80, 9,  '6A 6-10',  [1] * 5, 'repetir'),   # nota baixa
            ('2026-10-03', 95, 9,  '6A 6-10 v2', [2] * 5, 'dominio'), # mesmo trecho, exercícios novos
            ('2026-10-04', 100, 12, '6A 11-15', [1] * 5, 'repetir'),  # passou do tempo (limite 10)
            ('2026-10-05', 92, 10, '6A 11-15', None, None)]           # falta a versão 2: erro
    for n, (dia, nota, tempo, codigo, versoes, status) in enumerate(dias, 1):
        if versoes is None:
            with pytest.raises(ErroEspecificacao, match=r'6A/11\.v2\.yaml'):
                proximo(est, hoje=dia, saida=saida)
            break
        arquivos, esconder = proximo(est, hoje=dia, saida=saida)
        E.salvar(caminho, est); est = E.carregar(caminho)
        u = est['unidades'][-1]
        assert (u['codigo'], u['versoes'], u['pacote'], u['data']) == (codigo, versoes, n, dia)
        assert [os.path.basename(a) for a in arquivos] == [
            f'Pacote_{n:03d}_6A_{codigo.split()[1]}.{ext}' for ext in ('pdf', 'gabarito.csv', 'audio.txt')]
        assert all(os.path.getsize(a) > 0 for a in arquivos)
        with pytest.raises(ErroEspecificacao, match='pendente'):
            proximo(est, hoje=dia, saida=saida)                     # o pendente vem primeiro
        assert registrar(est, codigo, nota, tempo)['status'] == status
    assert proxima_folha(est, carregar_curso('frances-delf-b1')) == '6A 11'


def test_dois_pacotes_de_geometria(biblioteca):
    est, saida = _novo('geometria-plana-epcar', 'G1 1'), str(biblioteca / 'pacotes')
    for n, blocos in enumerate([['G1 1-3', 'G1 4-6'], ['G1 7-9', 'G1 10-12']], 1):
        arquivos, _ = proximo(est, dias=2, hoje=f'2026-10-0{n}', saida=saida)
        de, ate = blocos[0].split()[1].split('-')[0], blocos[-1].split('-')[-1]
        assert [os.path.basename(a) for a in arquivos] == [
            f'G1_pacote{n:02d}_folhas{de}-{ate}.{ext}' for ext in ('pdf', 'gabarito.csv', 'planilha.csv')]
        planilha = open(arquivos[2], encoding='utf-8').read()
        primeira = 1 + 6 * (n - 1)
        assert all(f'\nG1 {k},1,' in planilha for k in range(primeira, primeira + 6))   # gabarito por folha
        assert [u['codigo'] for u in est['unidades'][-2:]] == blocos
        for b in blocos: registrar(est, b, 95, 10)
    assert proxima_folha(est, carregar_curso('geometria-plana-epcar')) == 'G1 13'


@requer_frances
def test_registrar_codigo_errado(biblioteca):
    est = _novo('frances-delf-b1', '6A 1')
    proximo(est, hoje='2026-10-01', saida=str(biblioteca / 'p'))
    with pytest.raises(ErroEspecificacao, match="pendentes: 6A 1-5"):
        registrar(est, '6A 6-10', 95)


def test_estados_locais_com_pendente_bloqueiam():
    """estados reais deste computador (estado/*.local.json): se há pacote pendente, o próximo não sai"""
    import glob
    reais = [E.carregar(c) for c in glob.glob(os.path.join(RAIZ, 'estado', '*.local.json'))]
    reais = [e for e in reais if any(u['status'] == 'pendente' for u in e['unidades'])]
    if not reais: pytest.skip('nenhum estado local com pacote pendente')
    for est in reais:
        with pytest.raises(ErroEspecificacao, match='pendente'):
            proximo(est, saida='/nao/usado')



def test_validar_aponta_erros_e_faltas(biblioteca, capsys):
    from motor.ferramentas import validar
    assert validar(['geometria-plana-epcar']) == 0
    caminho = biblioteca / 'folhas/geometria-plana-epcar/G1/3.yaml'
    t = caminho.read_text(encoding='utf-8')
    caminho.write_text(t.replace('- grade:', '- gradee:', 1), encoding='utf-8')
    (biblioteca / 'folhas/geometria-plana-epcar/G1/14.yaml').write_text(t.replace('folha: G1 1', 'folha: G1 99', 1), encoding='utf-8')
    capsys.readouterr()
    assert validar(['geometria-plana-epcar']) == 1
    saida = capsys.readouterr().out
    assert 'ERRO G1 3' in saida and "tipo de bloco desconhecido 'gradee'" in saida
    assert "ERRO G1 14" in saida and "esperado 'G1 14'" in saida
    assert 'faltam no G1 (87): 13, 15-100' in saida
