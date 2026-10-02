# Assistente de configuração: respostas simuladas, arquivos numa pasta temporária.
import os, shutil
import pytest
from motor import assistente, especificacao
from motor.especificacao import RAIZ


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    shutil.copy(os.path.join(RAIZ, 'config.exemplo.yaml'), tmp_path)
    shutil.copytree(os.path.join(RAIZ, 'curriculos'), tmp_path / 'curriculos')
    monkeypatch.setattr(especificacao, 'RAIZ', str(tmp_path))
    return tmp_path


def _respostas(monkeypatch, *rs):
    it = iter(rs)
    monkeypatch.setattr('builtins.input', lambda *_: next(it))


def test_turma_e_link(pasta, monkeypatch):
    _respostas(monkeypatch, '', '2')                                   # curso padrão, 2 dias
    assistente.passo_turma()
    _respostas(monkeypatch, 'https://forms.gle/abc')
    assistente.passo_link()
    texto = (pasta / 'config.local.yaml').read_text(encoding='utf-8')
    assert 'curso: geometria-plana-epcar' in texto and 'blocos_por_pacote: 2  #' in texto
    assert 'link_formulario: https://forms.gle/abc' in texto and texto.startswith('# Configuração da turma')
    from motor.turma import carregar_config
    c = carregar_config(str(pasta / 'config.local.yaml'))
    assert c['blocos_por_pacote'] == 2 and c['link_formulario'] == 'https://forms.gle/abc'


def test_email_grava_sem_apagar_o_resto(pasta, monkeypatch):
    (pasta / '.env.local').write_text('# comentário\nDEGRAU_EMAIL_DE=\nANTHROPIC_API_KEY=xyz\n', encoding='utf-8')
    monkeypatch.delenv('DEGRAU_EMAIL_DE', raising=False); monkeypatch.delenv('DEGRAU_EMAIL_SENHA', raising=False)
    _respostas(monkeypatch, 'casd@gmail.com', 'n')                    # endereço; não mandar teste
    monkeypatch.setattr(assistente.getpass, 'getpass', lambda *_: 'abcd efgh ijkl mnop')
    assistente.passo_email()
    linhas = (pasta / '.env.local').read_text(encoding='utf-8').splitlines()
    assert linhas == ['# comentário', 'DEGRAU_EMAIL_DE=casd@gmail.com', 'ANTHROPIC_API_KEY=xyz',
                      'DEGRAU_EMAIL_SENHA=abcdefghijklmnop']
