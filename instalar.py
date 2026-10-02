#!/usr/bin/env python3
"""Instala o Degrau neste computador (Windows, Linux ou macOS).

    python instalar.py        (no Windows: py instalar.py)

Cria o ambiente do programa (.venv), instala as bibliotecas, prepara os arquivos de configuração e confere tudo.
Pode ser rodado de novo a qualquer momento: só completa o que faltar.
"""
import os, shutil, subprocess, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
WINDOWS = os.name == 'nt'
PYTHON = os.path.join(RAIZ, '.venv', 'Scripts' if WINDOWS else 'bin', 'python.exe' if WINDOWS else 'python')
COMANDO = 'degrau' if WINDOWS else './degrau'

MODELO_ENV = """# Segredos deste computador. Este arquivo não vai para o git e não deve ser compartilhado.
# E-mail que envia os pacotes (Gmail com senha de app; veja docs/ADMINISTRACAO.md):
DEGRAU_EMAIL_DE=
DEGRAU_EMAIL_SENHA=
# Opcional: chave da API da Anthropic, só para gerar folhas automaticamente (degrau automatico).
# ANTHROPIC_API_KEY=
"""


def passo(texto): print(f'\n== {texto}')


def falha(texto):
    print(f'\nNão foi possível instalar: {texto}')
    sys.exit(1)


def main():
    print('Instalação do Degrau em', RAIZ)
    if sys.version_info < (3, 10):
        falha(f'este Python é a versão {sys.version.split()[0]}; instale o Python 3.10 ou mais novo (python.org)')

    passo('Ambiente do programa')
    if not os.path.exists(PYTHON):
        try:
            import venv
            venv.create(os.path.join(RAIZ, '.venv'), with_pip=True)
        except Exception as e:
            dica = ' (no Ubuntu/Debian: sudo apt install python3-venv)' if not WINDOWS else ''
            falha(f'não consegui criar o ambiente: {e}{dica}')
        print('criado em .venv')
    else:
        print('já existe')

    passo('Bibliotecas')
    r = subprocess.run([PYTHON, '-m', 'pip', 'install', '--upgrade', '--quiet', '-r',
                        os.path.join(RAIZ, 'requirements.txt')])
    if r.returncode != 0: falha('o pip não conseguiu instalar as bibliotecas (confira a internet e tente de novo)')
    print('instaladas')

    passo('Arquivos de configuração')
    config = os.path.join(RAIZ, 'config.local.yaml')
    if not os.path.exists(config):
        shutil.copy(os.path.join(RAIZ, 'config.exemplo.yaml'), config); print('criado config.local.yaml')
    else:
        print('config.local.yaml já existe')
    env = os.path.join(RAIZ, '.env.local')
    if not os.path.exists(env):
        with open(env, 'w', encoding='utf-8') as f: f.write(MODELO_ENV)
        print('criado .env.local (vazio)')
    else:
        print('.env.local já existe')

    passo('Ferramentas do Google (para a planilha e o formulário)')
    if shutil.which('clasp'):
        print('clasp encontrada')
    elif shutil.which('npm'):
        print('falta a clasp: rode  npm install -g @google/clasp')
    else:
        print('falta o Node.js (nodejs.org, versão LTS) e depois:  npm install -g @google/clasp')

    passo('Conferência')
    r = subprocess.run([PYTHON, '-m', 'motor', 'validar'], cwd=RAIZ, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONPATH=RAIZ))
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:]); falha('as folhas não passaram na conferência')
    print('folhas conferidas')

    print(f'\nPronto. Próximo passo:  {COMANDO} configurar')


if __name__ == '__main__':
    try:
        main()
    finally:   # aberto com dois cliques no Windows: a janela espera antes de fechar
        if WINDOWS and sys.stdin and sys.stdin.isatty(): input('\nPressione Enter para fechar.')
