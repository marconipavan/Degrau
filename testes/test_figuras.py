# Figuras novas (fase 6): medidas em minutos, várias incógnitas, conversor dos esqueletos, biblioteca inteira.
import os, sys
import pytest
from motor.medidas import incognitas, gms, ler_rotulo
from motor.especificacao import RAIZ

sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
import esqueletos


def test_bico_com_minutos():
    b = {'segmentos': [[-35.5, 15], [-137.25, 0]], 'marcas': [[0, 'dir', "35°30'"], [1, None, 'x'], [2, 'dir', "42°45'"]]}
    assert gms(incognitas({'bico': b})['x']) == "78°15'"


def test_transversal_com_x_e_y():
    t = {'direcao': 80, 'marcas': [['r', 'acima-direita', '2x + 10°'], ['s', 'acima-direita', '80°'],
                                   ['s', 'acima-esquerda', 'y']]}
    assert {k: gms(v) for k, v in incognitas({'transversal': t}).items()} == {'x': '35', 'y': '100'}


def test_rotulo_que_nao_fecha():
    c = {'direcoes': [0, 90], 'marcas': [[0, 90, '5x − 10°'], [180, 270, '2x + 40°']]}
    with pytest.raises(ValueError, match='valores diferentes de x'):
        incognitas({'cruzadas': c})


def test_numeros_de_identificacao_nao_sao_medidas():
    assert ler_rotulo('3') == ('nome',) and ler_rotulo('x/2 + 10°')[0] == 'expr'


def test_conversor_le_as_frases_de_figura():
    f = esqueletos.figura("bico entre paralelas: retas r (acima) e s (abaixo) horizontais, distância 45 mm; "
                          "poligonal começa em r; segmentos nas direções −35°30' (15 mm), −137°15' (até s); "
                          "escrever em r (início), lado direito: 35°30'; no vértice 1: x; em s (fim), lado direito: 42°45'")
    assert f == {'bico': {'altura': 45, 'segmentos': [[-35.5, 15], [-137.25, 0]],
                          'marcas': [[0, 'dir', "35°30'"], [1, None, 'x'], [2, 'dir', "42°45'"]]}}
    with pytest.raises(esqueletos.ErroConversao, match='figura desconhecida'):
        esqueletos.figura('um triângulo qualquer')


def test_biblioteca_inteira_valida(capsys):
    """todas as folhas escritas passam por estrutura, desenho, gabarito e limite do formulário"""
    from motor.ferramentas import validar
    assert validar(['geometria-plana-epcar', 'frances-delf-b1']) == 0, capsys.readouterr().out
