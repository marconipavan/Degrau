# Fase 5: autor automático com um cliente da API simulado (nenhuma chamada real, nenhum custo).
import json, os, re, shutil
from types import SimpleNamespace
import pytest
from motor import especificacao, autor
from motor.especificacao import ErroEspecificacao, RAIZ
from motor.gerador import planejar, proximo, registrar


@pytest.fixture
def biblioteca(tmp_path, monkeypatch):
    for d in ('curriculos', 'folhas/frances-delf-b1'):
        shutil.copytree(os.path.join(RAIZ, d), tmp_path / d)
    os.makedirs(tmp_path / 'exemplos')
    for arq in ('CLAUDE.md', 'exemplos/pacotes.yaml'):
        shutil.copy(os.path.join(RAIZ, arq), tmp_path / arq)
    monkeypatch.setattr(especificacao, 'RAIZ', str(tmp_path))
    monkeypatch.setattr(autor, 'RAIZ', str(tmp_path))
    return tmp_path


def _renumerar(n_origem, codigo):
    t = open(os.path.join(RAIZ, 'folhas/frances-delf-b1/6A', f'{n_origem}.yaml'), encoding='utf-8').read()
    return re.sub(r'^folha: .*$', f'folha: {codigo}', t, count=1, flags=re.M)


class _Stream:
    def __init__(self, msg): self.msg = msg
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def get_final_message(self): return self.msg


class ClienteFalso:
    """Imita client.beta.messages.stream(...).get_final_message() e guarda os pedidos."""
    def __init__(self, respostas):
        self.respostas, self.pedidos = list(respostas), []
        self.beta = SimpleNamespace(messages=self)

    def stream(self, **kw):
        self.pedidos.append(kw)
        texto = json.dumps(self.respostas.pop(0), ensure_ascii=False)
        return _Stream(SimpleNamespace(
            stop_reason='end_turn', content=[SimpleNamespace(type='text', text=texto)],
            usage=SimpleNamespace(input_tokens=2000, output_tokens=10000,
                                  cache_creation_input_tokens=7000, cache_read_input_tokens=0)))


def _resposta(folhas):
    return {'folhas': folhas, 'vocabulario_novo': ['un professeur'], 'estruturas_novas': [], 'observacoes': ''}


def _estado_depois_do_pacote_1(saida):
    est = {'curso': 'frances-delf-b1', 'aluno': 'Teste', 'inicio': '6A 1', 'unidades': [],
           'vocabulario': {}, 'estruturas': {}, 'erros_recorrentes': []}
    proximo(est, hoje='2026-10-01', saida=str(saida))   # 6A 1-5 existem
    registrar(est, '6A 1-5', 95, 9)
    return est


def test_corrige_e_grava(biblioteca, tmp_path):
    est = _estado_depois_do_pacote_1(biblioteca / 'p1')
    plano = planejar(est)
    assert [(c, v) for c, v, _ in plano['faltam']] == [(f'6A {n}', 1) for n in range(6, 11)]
    boas = [{'codigo': f'6A {n}', 'versao': 1, 'yaml': _renumerar((n - 1) % 5 + 1, f'6A {n}')} for n in range(6, 11)]
    ruim = [dict(f) for f in boas]
    ruim[0]['yaml'] = ruim[0]['yaml'].replace('- palavras:', '- palavra:', 1)              # tipo errado
    ruim[3]['yaml'] = ruim[3]['yaml'].replace("Je m'appelle Rafael.",
                                              "Je m'appelle Rafael et je suis un étudiant brésilien très content.", 1)
    cliente = ClienteFalso([_resposta(ruim), _resposta(boas)])
    custo = autor.escrever_folhas(est, plano, cliente=cliente, registro=lambda s: None)

    assert len(cliente.pedidos) == 2
    p1, p2 = cliente.pedidos
    assert p1['model'] == 'claude-opus-5-5' and p1['fallbacks'] == 'default'
    assert p1['system'][0]['cache_control'] == {'type': 'ephemeral'}
    retorno = p2['messages'][-1]['content']                      # os erros voltaram para o modelo
    assert "tipo de bloco desconhecido 'palavra'" in retorno and 'sai da área útil' in retorno
    for n in range(6, 11):
        assert os.path.exists(biblioteca / f'folhas/frances-delf-b1/6A/{n}.yaml')
    assert est['vocabulario']['6A 6-10'] == ['un professeur']
    assert custo == pytest.approx(2 * (2000 * 4 + 10000 * 20 + 7000 * 5) / 1e6)
    arquivos, _ = proximo(est, hoje='2026-10-02', saida=str(tmp_path / 'p'))
    assert os.path.basename(arquivos[0]) == 'Pacote_002_6A_6-10.pdf'


def test_desiste_depois_de_tres_tentativas(biblioteca):
    est = _estado_depois_do_pacote_1(biblioteca / 'p1')
    plano = planejar(est)
    incompleta = _resposta([{'codigo': '6A 6', 'versao': 1, 'yaml': _renumerar(1, '6A 6')}])
    with pytest.raises(ErroEspecificacao, match='faltou a folha 6A 7'):
        autor.escrever_folhas(est, plano, cliente=ClienteFalso([incompleta] * 3), registro=lambda s: None)
    assert not os.path.exists(biblioteca / 'folhas/frances-delf-b1/6A/6.yaml')   # nada gravado


def test_repeticao_manda_a_versao_anterior(biblioteca):
    est = _estado_depois_do_pacote_1(biblioteca / 'p1')
    est['unidades'][-1]['status'] = 'repetir'
    plano = planejar(est)
    assert [(c, v) for c, v, _ in plano['faltam']] == [(f'6A {n}', 2) for n in range(1, 6)]
    pedido = autor.pedido_do_dia(est, plano)
    assert 'É uma repetição' in pedido and 'Mots familiers 1' in pedido
