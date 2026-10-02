# Degrau — assistente de configuração e menu, para quem não usa linha de comando.
#   degrau configurar   passo a passo: turma, e-mail, projeto no Google (planilha, formulário, gabarito), link
#   degrau              (sem nada) menu com as tarefas do dia a dia
# Cada passo mostra se já está feito e pergunta antes de mexer; pode ser rodado de novo quando quiser.
import getpass, glob, json, os, shutil, subprocess, sys
import yaml
from . import especificacao as esp

MANIFESTO = {"timeZone": "America/Sao_Paulo", "dependencies": {}, "exceptionLogging": "STACKDRIVER",
             "runtimeVersion": "V8"}


def _caminho(*p): return os.path.join(esp.RAIZ, *p)


def perguntar(texto, padrao=''):
    r = input(f'{texto}{f" [{padrao}]" if padrao else ""}: ').strip()
    return r or padrao


def sim(texto, padrao=True):
    r = input(f'{texto} [{"S/n" if padrao else "s/N"}]: ').strip().lower()
    return padrao if not r else r in ('s', 'sim', 'y')


def titulo(t): print(f'\n=== {t} ===')


# ---------- arquivos de configuração ----------

def ler_config():
    c = _caminho('config.local.yaml')
    if not os.path.exists(c): shutil.copy(_caminho('config.exemplo.yaml'), c)
    with open(c, encoding='utf-8') as f: return yaml.safe_load(f) or {}


def gravar_config(dados):
    """reescreve config.local.yaml mantendo os comentários do modelo"""
    linhas = []
    for l in open(_caminho('config.exemplo.yaml'), encoding='utf-8'):
        chave = l.split(':', 1)[0].strip()
        if chave in dados and not l.startswith('#'):
            comentario = '  #' + l.split('#', 1)[1].rstrip('\n') if '#' in l else ''
            linhas.append(f'{chave}: {dados[chave]}{comentario}\n')
        else:
            linhas.append(l)
    with open(_caminho('config.local.yaml'), 'w', encoding='utf-8') as f: f.writelines(linhas)


def gravar_env(valores):
    """atualiza NOME=valor em .env.local, mantendo o resto"""
    caminho = _caminho('.env.local')
    linhas = open(caminho, encoding='utf-8').read().splitlines() if os.path.exists(caminho) else []
    for nome, valor in valores.items():
        nova = f'{nome}={valor}'
        for i, l in enumerate(linhas):
            if l.split('=', 1)[0].strip() == nome: linhas[i] = nova; break
        else: linhas.append(nova)
        os.environ[nome] = valor
    with open(caminho, 'w', encoding='utf-8') as f: f.write('\n'.join(linhas) + '\n')


# ---------- passos ----------

def passo_turma():
    titulo('1. Turma')
    c = ler_config()
    cursos = sorted(os.path.basename(p)[:-5] for p in glob.glob(_caminho('curriculos', '*.yaml')))
    print('cursos disponíveis:', ', '.join(cursos))
    c['curso'] = perguntar('Curso', c.get('curso', cursos[0] if cursos else ''))
    if c['curso'] not in cursos: print('curso desconhecido; mantido mesmo assim')
    c['blocos_por_pacote'] = int(perguntar('Dias de treino entre uma aula e a seguinte (blocos por pacote)',
                                           str(c.get('blocos_por_pacote', 3))))
    gravar_config(c)
    print('gravado em config.local.yaml')


def passo_email():
    titulo('2. E-mail que envia os pacotes')
    de = os.environ.get('DEGRAU_EMAIL_DE', '')
    print(f'configurado: {de}' if de and os.environ.get('DEGRAU_EMAIL_SENHA') else 'ainda não configurado')
    if de and not sim('Configurar de novo?', False): return
    print('Use a conta Gmail da instituição. A senha NÃO é a senha da conta: é uma "senha de app" de 16 letras,')
    print('criada em https://myaccount.google.com/apppasswords (precisa da verificação em duas etapas ligada).')
    de = perguntar('Endereço do Gmail', de)
    senha = getpass.getpass('Senha de app (não aparece ao digitar): ').replace(' ', '')
    gravar_env({'DEGRAU_EMAIL_DE': de, 'DEGRAU_EMAIL_SENHA': senha})
    print('gravado em .env.local')
    if sim(f'Mandar um e-mail de teste para {de}?'):
        from email.message import EmailMessage
        from . import envio
        m = EmailMessage(); m['From'] = m['To'] = de; m['Subject'] = 'Degrau — e-mail de teste'
        m.set_content('Se você recebeu esta mensagem, o envio de pacotes do Degrau está funcionando.\n')
        try:
            envio.enviar(m); print('enviado: confira a caixa de entrada')
        except esp.ErroEspecificacao as e:
            print(f'falhou: {e}')


def _clasp(*args, capturar=False):
    return subprocess.run(['clasp', *args], cwd=_caminho('correcao'), text=True,
                          capture_output=capturar)


def passo_google():
    titulo('3. Planilha, formulário e correção automática (Google)')
    if not shutil.which('clasp'):
        print('falta a clasp. Instale o Node.js (nodejs.org) e rode:  npm install -g @google/clasp'); return
    r = _clasp('show-authorized-user', capturar=True)
    conta = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ''
    if 'logged in as' not in conta.lower():
        print('A clasp ainda não tem acesso a uma conta Google.')
        print('Antes, ligue a "API do Google Apps Script" em https://script.google.com/home/usersettings (conta da instituição).')
        if not sim('Fazer o login agora (abre o navegador)?'): return
        _clasp('login')
        conta = _clasp('show-authorized-user', capturar=True).stdout.strip().splitlines()[0]
    print(conta)
    if not sim('Esta é a conta da instituição (onde ficam os dados dos alunos)?'):
        print('Rode  clasp logout  e depois este passo de novo, escolhendo a conta da instituição.'); return
    projeto = _caminho('correcao', '.clasp.json')
    if os.path.exists(projeto):
        print('o projeto do Google já existe neste computador')
    else:
        if not sim('Criar a planilha "Degrau" e o script de correção nessa conta?'): return
        if _clasp('create-script', '--type', 'sheets', '--title', 'Degrau', '--rootDir', '.').returncode != 0:
            print('a criação falhou (veja a mensagem acima)'); return
        with open(_caminho('correcao', 'appsscript.json'), 'w', encoding='utf-8') as f:   # a criação troca o fuso
            json.dump(MANIFESTO, f, indent=2); f.write('\n')
    from .ferramentas import atualizar_gabarito
    atualizar_gabarito(ler_config().get('curso'))
    print('\nAgora, no navegador (o editor do script vai abrir):')
    print('  a) escolha a função "montar" no alto e clique em Executar; autorize com a conta da instituição;')
    print('  b) na planilha "Degrau", aba Alunos: um aluno por linha, nome na coluna A e e-mail na coluna B;')
    print('  c) execute "montar" mais uma vez: ele cria o formulário e a correção automática.')
    if sim('Abrir o editor agora?'): _clasp('open-script')


def passo_link():
    titulo('4. Link do formulário')
    c = ler_config()
    atual = c.get('link_formulario', '')
    print('No formulário criado pelo "montar": Enviar > ícone de link > Copiar.')
    link = perguntar('Cole o link', '' if 'COLE-AQUI' in atual else atual)
    if link: c['link_formulario'] = link; gravar_config(c); print('gravado em config.local.yaml')


def configurar():
    print('Configuração do Degrau. Pode parar a qualquer momento (Ctrl+C) e voltar depois.')
    for p in (passo_turma, passo_email, passo_google, passo_link):
        p()
    print('\nPronto. No dia a dia: abra o Degrau e escolha "Rotina da semana".')


# ---------- escolha da planilha e menu ----------

def escolher_planilha():
    """abre uma janela para escolher a planilha baixada; sem janela disponível, pergunta o caminho"""
    inicio = next((p for p in (os.path.expanduser('~/Downloads'), os.path.expanduser('~/Transferências')) if os.path.isdir(p)),
                  os.path.expanduser('~'))
    try:
        import tkinter
        from tkinter import filedialog
        raiz = tkinter.Tk(); raiz.withdraw()
        caminho = filedialog.askopenfilename(title='Escolha a planilha baixada (Excel)', initialdir=inicio,
                                             filetypes=[('Planilha do Excel', '*.xlsx')])
        raiz.destroy()
        return caminho or None
    except Exception:
        return perguntar('Caminho da planilha baixada (.xlsx)') or None


def menu():
    opcoes = [('Rotina da semana (planilha -> pacotes -> e-mails)', ['semana']),
              ('Atualizar o gabarito no Google (depois de mudar folhas)', ['atualizar-gabarito']),
              ('Conferir todas as folhas', ['validar']),
              ('Configurar (turma, e-mail, Google)', ['configurar'])]
    print('Degrau\n')
    for i, (t, _) in enumerate(opcoes, 1): print(f'  {i}. {t}')
    print('  0. Sair')
    escolha = perguntar('\nEscolha')
    if escolha in ('', '0') or not escolha.isdigit() or not 1 <= int(escolha) <= len(opcoes): return None
    return opcoes[int(escolha) - 1][1]
