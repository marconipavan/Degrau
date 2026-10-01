# Testes básicos: tudo gera sem erro; o gabarito bate com o plano; expressões conferidas; nenhum texto sai da página nem fica
# sobre outro texto ou sobre uma linha. Rodar com: .venv/bin/pytest
import os, shutil, subprocess
import pytest
from motor import folha as motor_folha
from motor.verificar import Gravador, VERIFICACOES, verificar_folha
from motor.render import gerar
from motor.especificacao import RAIZ, ErroEspecificacao, carregar_folha
from motor.gabarito import respostas_folha
from motor.audio import faixas, numero_fr

GRAVADORES = []

def _gravar(monkeypatch, gerador, destino=None):
    GRAVADORES.clear()
    def criar(caminho, *a, **k):
        if destino: caminho = os.path.join(destino, os.path.basename(caminho))
        g = Gravador(caminho, *a, **k); GRAVADORES.append(g); return g
    monkeypatch.setattr(motor_folha.canvas, 'Canvas', criar)
    gerador()
    return [(os.path.basename(g._filename), n, t, l) for g in GRAVADORES for n, t, l in g.paginas]


@pytest.fixture(scope='module')
def paginas_yaml(tmp_path_factory):
    with pytest.MonkeyPatch.context() as mp:
        saida = str(tmp_path_factory.mktemp('pdf'))
        return _gravar(mp, lambda: gerar(os.path.join(RAIZ, 'exemplos', 'pacotes.yaml'), saida))


def test_yaml_gera_paginas(paginas_yaml):
    assert len(paginas_yaml) == 26


@pytest.mark.parametrize('verificar', VERIFICACOES, ids=lambda v: v.__name__)
def test_yaml(paginas_yaml, verificar):
    erros = verificar(paginas_yaml)
    assert not erros, '\n'.join(erros)


# ---------- gabarito (fase 2): igual à seção 6.3 do plano ----------
PLANO_6_3 = {
    'G1 1a': ['PQR', 'NMT', 'DCE', 'GFH'],
    'G1 1b': ['A', 'R', 'O', 'Ra', 'A', 'O', 'A', 'O', 'A', 'O'],
    'G1 2a': ['A', 'R', 'O', 'R', 'A', 'O'],
    'G1 2b': ['conjunto:PÔQ,QÔR,RÔS,PÔR,QÔS,PÔS', '10'],
    'G1 3a': ['R', 'R', 'O', 'A', 'O', 'O', 'Ra', 'A', 'A', 'Ra'],
    'G1 3b': ['Y', 'JKL obtuso', 'reto', '10', 'S'],
    'G1 81a': ['75', '85', '80', '90'], 'G1 81b': ['40', '30', '30', '50'],
    'G1 85a': ['75', '60', '45', '35'], 'G1 85b': ['60', '65', '40', '50'],
    'G1 89a': ['15', '10'], 'G1 89b': ['C'],
    '6A 3a': ['merci', 'un avion', 'un étudiant', 'fatigué', 'une ville', 'content'],
    '6A 4b': ["m'appelle", 'suis', 'avion', 'ville', 'Bienvenue'],
    '6A 5b': ['F', 'V', 'V', 'V', 'Je suis dans un avion.', 'Toulouse est une ville en France.'],
}

def test_gabarito_bate_com_o_plano():
    obtido = {}
    for curso, cods in [('geometria-plana-epcar', ['G1 1', 'G1 2', 'G1 3', 'G1 81', 'G1 85', 'G1 89']),
                        ('frances-delf-b1', ['6A 3', '6A 4', '6A 5'])]:
        for cod in cods:
            for l in respostas_folha(carregar_folha(curso, cod)):
                if l['pagina'] in PLANO_6_3: obtido.setdefault(l['pagina'], []).append(l['respostas'][0])
    assert obtido == PLANO_6_3


def _folha_89(mexer):
    f = carregar_folha('geometria-plana-epcar', 'G1 89'); mexer(f); return f

@pytest.mark.parametrize('mexer, msg', [
    (lambda f: f['b']['blocos'][1]['figura']['bico']['marcas'].__setitem__(2, [2, None, '100°']),
     'o ângulo desenhado é 80°'),
    (lambda f: f['a']['blocos'][0]['grade']['itens'][0]['bico']['marcas'].__setitem__(1, [1, None, '4x + 10°']),
     'valores diferentes de x'),
    (lambda f: f['a']['blocos'][0]['grade']['itens'][1].__setitem__('resposta', 12), 'os rótulos dão x = 10'),
    (lambda f: f['b']['blocos'][2]['alternativas'].__setitem__('resposta', 'B'), 'a figura dá x = 25'),
])
def test_expressoes_erradas_falham(mexer, msg):
    with pytest.raises(ErroEspecificacao, match=msg):
        respostas_folha(_folha_89(mexer))


def test_audio():
    assert [numero_fr(n) for n in (1, 21, 64, 71, 80, 91, 112)] == [
        'un', 'vingt et un', 'soixante-quatre', 'soixante et onze', 'quatre-vingts', 'quatre-vingt-onze', 'cent douze']
    fx = dict((p, (t, e)) for p, t, e in faixas(carregar_folha('frances-delf-b1', '6A 5')))
    assert fx['6A 5a'][0].splitlines()[0] == 'Feuille cinq a.'
    assert '[L\'hôtesse] Bienvenue à Toulouse !' in fx['6A 5a'][0]
    assert fx['6A 5b'] == ('Feuille cinq b.\nUn. Je suis dans un avion.\nDeux. Toulouse est une ville en France.', True)
    assert not fx['6A 5a'][1]


# ---------- correção do CASD (fase 3) ----------
def test_modelo_de_gabarito_atualizado(tmp_path):
    """correcao/modelos/gabarito.csv é o bloco G1 1-3 gerado do YAML (o simulador usa este arquivo)"""
    from motor.gabarito import escrever_planilha
    from motor.especificacao import carregar_curso
    novo = tmp_path / 'g.csv'
    escrever_planilha([carregar_folha('geometria-plana-epcar', f'G1 {n}') for n in (1, 2, 3)],
                      carregar_curso('geometria-plana-epcar'), str(novo))
    assert novo.read_text(encoding='utf-8') == open(os.path.join(RAIZ, 'correcao', 'modelos', 'gabarito.csv'), encoding='utf-8').read()


@pytest.mark.skipif(not shutil.which('node'), reason='node não instalado')
def test_correcao_simulada():
    r = subprocess.run(['node', os.path.join(RAIZ, 'correcao', 'teste', 'simular.js')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_verificar_folha_aponta_frase_longa():
    """a geração automática usa verificar_folha: uma frase que vaza a margem tem que aparecer"""
    from motor.especificacao import carregar_curso
    curso = carregar_curso('frances-delf-b1')
    f = carregar_folha('frances-delf-b1', '6A 4')
    assert verificar_folha(f, curso) == []
    f['a']['blocos'][0]['frases']['itens'][0][0] = "Je m'appelle Rafael et je suis un étudiant brésilien très content."
    assert any('sai da área útil' in e for e in verificar_folha(f, curso))
