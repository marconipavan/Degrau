# Envio por e-mail com servidor SMTP simulado (nada sai da máquina).
import os, smtplib
import pytest
from motor import envio
from motor.especificacao import RAIZ, ErroEspecificacao

ESTADO = {'curso': 'frances-delf-b1', 'aluno': 'Teste', 'inicio': '6A 1', 'unidades': [
    {'pacote': 1, 'codigo': '6A 1-5', 'folhas': [f'6A {n}' for n in range(1, 6)], 'versoes': [1] * 5,
     'data': '2026-09-30', 'limite_min': 10, 'status': 'pendente', 'nota': None, 'tempo_min': None,
     'arquivo': 'Pacote_001_6A_1-5.pdf'}]}
PASTA = os.path.join(RAIZ, 'exemplos', 'pdf')


class SMTPFalso:
    enviados, logins = [], []
    def __init__(self, servidor, porta, timeout=None): assert (servidor, porta) == ('smtp.gmail.com', 465)
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def login(self, u, s):
        if s != 'senha-certa': raise smtplib.SMTPAuthenticationError(535, b'bad')
        SMTPFalso.logins.append(u)
    def send_message(self, m): SMTPFalso.enviados.append(m)


@pytest.fixture
def smtp(monkeypatch):
    SMTPFalso.enviados, SMTPFalso.logins = [], []
    monkeypatch.setattr(envio.smtplib, 'SMTP_SSL', SMTPFalso)
    monkeypatch.setenv('DEGRAU_EMAIL_DE', 'aluno@gmail.com')
    monkeypatch.delenv('DEGRAU_EMAIL_PARA', raising=False)
    return monkeypatch


def test_envia_pdf_e_audio_sem_gabarito(smtp):
    smtp.setenv('DEGRAU_EMAIL_SENHA', 'senha-certa')
    envio.enviar(envio.montar(ESTADO, 1, PASTA))
    m = SMTPFalso.enviados[0]
    assert m['To'] == 'aluno@gmail.com' and SMTPFalso.logins == ['aluno@gmail.com']
    anexos = [p.get_filename() for p in m.iter_attachments()]
    assert anexos == ['Pacote_001_6A_1-5.pdf', 'Pacote_001_6A_1-5.audio.txt']
    corpo = m.get_body().get_content()
    assert 'Esconda o texto antes de ouvir em: 6A 3a, 6A 5b' in corpo and '[Rafael] Merci !' in corpo
    assert 'gabarito' not in ' '.join(anexos)


def test_senha_errada_e_falta_de_configuracao(smtp):
    smtp.setenv('DEGRAU_EMAIL_SENHA', 'outra')
    with pytest.raises(ErroEspecificacao, match='senha de app'):
        envio.enviar(envio.montar(ESTADO, 1, PASTA))
    smtp.delenv('DEGRAU_EMAIL_SENHA')
    with pytest.raises(ErroEspecificacao, match='não configurado'):
        envio.enviar(envio.montar(ESTADO, 1, PASTA))
    with pytest.raises(ErroEspecificacao, match='pacote 7 não está'):
        envio.montar(ESTADO, 7, PASTA)
