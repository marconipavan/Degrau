# Degrau — envio do pacote por e-mail (Gmail, SMTP com senha de app). Só biblioteca padrão.
#
# Configuração em .env.local (fora do git):
#   DEGRAU_EMAIL_DE=voce@gmail.com          conta que envia
#   DEGRAU_EMAIL_SENHA=xxxx xxxx xxxx xxxx  senha de app do Google (não é a senha da conta)
#   DEGRAU_EMAIL_PARA=voce@gmail.com        destinatário (opcional; padrão: o mesmo endereço)
# Vai o PDF e o bloco de áudio (no corpo e em anexo). O gabarito nunca vai: tem as respostas.
import os, smtplib
from email.message import EmailMessage
from .especificacao import ErroEspecificacao, carregar_folha
from . import audio

SERVIDOR, PORTA = 'smtp.gmail.com', 465


def configurado():
    return bool(os.environ.get('DEGRAU_EMAIL_DE') and os.environ.get('DEGRAU_EMAIL_SENHA'))


def montar(estado, pacote, pasta):
    """E-mail do pacote número `pacote`, com os arquivos que estão em `pasta`."""
    unidades = [u for u in estado['unidades'] if u['pacote'] == pacote]
    if not unidades:
        raise ErroEspecificacao(f'pacote {pacote} não está no estado')
    arquivo = unidades[0]['arquivo']
    pdf = os.path.join(pasta, arquivo)
    if not os.path.exists(pdf):
        raise ErroEspecificacao(f'PDF não encontrado: {pdf}')
    base = pdf[:-4]
    codigos = ', '.join(u['codigo'] for u in unidades)
    folhas = [carregar_folha(estado['curso'], f, v) for u in unidades for f, v in zip(u['folhas'], u['versoes'])]
    esconder = [p for folha in folhas for p, _, esc in audio.faixas(folha) if esc]
    texto_audio = open(base + '.audio.txt', encoding='utf-8').read() if os.path.exists(base + '.audio.txt') else ''

    de = os.environ.get('DEGRAU_EMAIL_DE', '')
    msg = EmailMessage()
    msg['Subject'] = f'Degrau — pacote {pacote} ({codigos})'
    msg['From'] = de
    msg['To'] = os.environ.get('DEGRAU_EMAIL_PARA') or de
    corpo = [f'Pacote {pacote}: {codigos}. Entrega até 23:59 de hoje.',
             'Anote início e fim de cada folha.']
    if texto_audio:
        corpo.append('Cole o bloco abaixo no leitor de francês e toque em "Preparar texto".')
        if esconder:
            corpo.append('Esconda o texto antes de ouvir em: ' + ', '.join(esconder) + ' (o áudio diz a resposta).')
        corpo += ['', '---- áudio ----', texto_audio.rstrip(), '---- fim do áudio ----']
    msg.set_content('\n'.join(corpo) + '\n')
    with open(pdf, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=arquivo)
    if texto_audio:
        msg.add_attachment(texto_audio.encode('utf-8'), maintype='text', subtype='plain',
                           filename=os.path.basename(base) + '.audio.txt')
    return msg


def enviar(msg):
    if not configurado():
        raise ErroEspecificacao('e-mail não configurado: defina DEGRAU_EMAIL_DE e DEGRAU_EMAIL_SENHA em .env.local')
    try:
        with smtplib.SMTP_SSL(SERVIDOR, PORTA, timeout=60) as s:
            s.login(os.environ['DEGRAU_EMAIL_DE'], os.environ['DEGRAU_EMAIL_SENHA'])
            s.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        raise ErroEspecificacao('o Gmail recusou o login: confira o endereço e a senha de app (não a senha da conta)') from None
    except (smtplib.SMTPException, OSError) as e:
        raise ErroEspecificacao(f'falha ao enviar o e-mail: {e}') from None
