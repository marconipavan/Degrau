# Linha de comando. Use ./degrau <comando> (ou python -m motor <comando>):
#   exemplos  <pacotes.yaml> [saída]            gera pacotes fixos (PDF + gabarito + áudio)
#   proximo   <estado.json> [--dias N]          gera o próximo pacote do aluno e o marca como pendente
#   registrar <estado.json> <código> --nota N [--tempo MIN]   registra a correção: domínio ou repetir
#   estado    <estado.json>                     resumo: próxima folha, pendentes, últimas notas
#   automatico <estado.json> [--pedido]         o Claude escreve as folhas que faltam (API) e gera o pacote;
#                                               --pedido só grava o pedido em saida/pedido.txt, sem chamar a API;
#                                               com o e-mail configurado (.env.local), envia o pacote no fim
#   enviar    <estado.json> [--pacote N] [--pasta DIR]   envia por e-mail o pacote (padrão: o último)
#   validar   [curso ...]                       confere a biblioteca inteira e lista as folhas que faltam
#   ver       G1 12 | G1 4-6 [--versao N]       gera o PDF dessas folhas em saida/ver/ e mostra o gabarito
#   gabarito  <curso> [arquivo.csv]             aba Gabarito da planilha com a biblioteca inteira
#   atualizar-gabarito [curso] [--sem-enviar]  gera correcao/gabarito.gs e envia ao Google (clasp)
#   semana    <planilha.xlsx> [--sim] [--sem-enviar] [--config arquivo]
#             rotina da turma: resultados do Painel, próximos pacotes e e-mails (pergunta antes de enviar)
import argparse, os, sys
from .especificacao import ErroEspecificacao, RAIZ, carregar_curso, carregar_folha, biblioteca


def carregar_env(caminho=os.path.join(RAIZ, '.env.local')):
    """segredos locais (senha do e-mail, chave da API): linhas NOME=valor; não sobrescreve o ambiente"""
    if not os.path.exists(caminho): return
    for linha in open(caminho, encoding='utf-8'):
        linha = linha.strip()
        if not linha or linha.startswith('#') or '=' not in linha: continue
        nome, valor = linha.split('=', 1)
        os.environ.setdefault(nome.strip(), valor.strip().strip('"').strip("'"))


carregar_env()
from . import estado as E, gerador, render, autor, envio, ferramentas


def _mostrar(arquivos, esconder):
    for a in arquivos: print(a)
    if esconder: print('  esconder o texto ao ouvir:', ', '.join(esconder))


def main(argv):
    ap = argparse.ArgumentParser(prog='degrau')
    sub = ap.add_subparsers(dest='comando', required=True)
    p = sub.add_parser('exemplos'); p.add_argument('pacotes'); p.add_argument('saida', nargs='?')
    p = sub.add_parser('proximo'); p.add_argument('estado'); p.add_argument('--dias', type=int, default=1)
    p.add_argument('--data'); p.add_argument('--saida', default=os.path.join(RAIZ, 'pacotes'))
    p = sub.add_parser('registrar'); p.add_argument('estado'); p.add_argument('codigo')
    p.add_argument('--nota', type=float, required=True); p.add_argument('--tempo', type=float)
    p = sub.add_parser('estado'); p.add_argument('estado')
    p = sub.add_parser('automatico'); p.add_argument('estado'); p.add_argument('--dias', type=int, default=1)
    p.add_argument('--saida', default=os.path.join(RAIZ, 'pacotes')); p.add_argument('--pedido', action='store_true')
    p = sub.add_parser('enviar'); p.add_argument('estado'); p.add_argument('--pacote', type=int)
    p.add_argument('--pasta', default=os.path.join(RAIZ, 'pacotes'))
    p = sub.add_parser('validar'); p.add_argument('cursos', nargs='*')
    p = sub.add_parser('ver'); p.add_argument('codigo', nargs='+'); p.add_argument('--versao', type=int, default=1)
    p = sub.add_parser('gabarito'); p.add_argument('curso'); p.add_argument('arquivo', nargs='?')
    p = sub.add_parser('atualizar-gabarito'); p.add_argument('curso', nargs='?'); p.add_argument('--sem-enviar', action='store_true')
    p = sub.add_parser('configurar')
    p = sub.add_parser('semana'); p.add_argument('planilha', nargs='?'); p.add_argument('--config')
    p.add_argument('--sim', action='store_true'); p.add_argument('--sem-enviar', action='store_true')
    a = ap.parse_args(argv)
    if a.comando == 'configurar':
        from . import assistente
        return assistente.configurar()
    if a.comando in ('validar', 'ver', 'gabarito', 'atualizar-gabarito'):
        return ferramentas.executar(a)
    if a.comando == 'semana':
        from . import turma
        config = turma.carregar_config(a.config)
        if not a.planilha:   # sem caminho: janela para escolher a planilha baixada
            from .assistente import escolher_planilha
            a.planilha = escolher_planilha()
            if not a.planilha: print('Nenhuma planilha escolhida.'); return
        resumo = turma.preparar(a.planilha, config)
        print(turma.texto_resumo(resumo))
        enviaveis = [r for r in resumo if r['pacote'] or r['pendentes']]
        if a.sem_enviar:
            print('\nSem envio: os PDFs estão em', os.path.join(config['pasta_dados'], 'pacotes'))
            turma.enviar_e_gravar(resumo, config, enviar=False); return
        if not envio.configurado():
            sys.exit('\nerro: e-mail não configurado (DEGRAU_EMAIL_DE e DEGRAU_EMAIL_SENHA em .env.local); '
                     'nada foi gravado. Use --sem-enviar para só gerar os PDFs.')
        if not a.sim and input(f'\nEnviar {len(enviaveis)} e-mail(s)? [s/N] ').strip().lower() not in ('s', 'sim'):
            print('Nada enviado nem gravado.'); return
        turma.enviar_e_gravar(resumo, config)
        return

    if a.comando == 'exemplos':
        for arquivos, esconder in render.gerar(a.pacotes, a.saida): _mostrar(arquivos, esconder)
        return
    est = E.carregar(a.estado)
    if a.comando == 'automatico':
        from datetime import datetime
        print(datetime.now().isoformat(timespec='minutes'), est['aluno'], est['curso'])
        pend = gerador.pendentes(est)
        if pend:   # o pendente vem primeiro: nada a gerar até registrar a correção
            print('  pacote pendente, nada a gerar:', ', '.join(u['codigo'] for u in pend)); return
        plano = gerador.planejar(est, a.dias)
        if a.pedido:
            os.makedirs(os.path.join(RAIZ, 'saida'), exist_ok=True)
            caminho = os.path.join(RAIZ, 'saida', 'pedido.txt')
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(autor.pedido_fixo(plano['curso']) + '\n\n=== PEDIDO DO DIA ===\n\n' + autor.pedido_do_dia(est, plano))
            print('  pedido gravado em', caminho, '(nada foi enviado)'); return
        custo = autor.escrever_folhas(est, plano, registro=lambda s: print('  ' + s))
        E.salvar(a.estado, est)          # vocabulário novo fica salvo mesmo se o PDF falhar
        _mostrar(*gerador.proximo(est, a.dias, saida=a.saida))
        E.salvar(a.estado, est)
        print(f'  custo estimado da API: US$ {custo:.2f}')
        if envio.configurado():
            n = est['unidades'][-1]['pacote']
            envio.enviar(envio.montar(est, n, a.saida))
            print(f'  pacote {n} enviado por e-mail')
        else:
            print('  e-mail não configurado: pacote só em', a.saida)
    elif a.comando == 'enviar':
        n = a.pacote or max(u['pacote'] for u in est['unidades'])
        msg = envio.montar(est, n, a.pasta)
        envio.enviar(msg)
        print(f'pacote {n} enviado para {msg["To"]}')
    elif a.comando == 'proximo':
        _mostrar(*gerador.proximo(est, a.dias, a.data, a.saida))
        E.salvar(a.estado, est)
    elif a.comando == 'registrar':
        u = gerador.registrar(est, a.codigo, a.nota, a.tempo)
        E.salvar(a.estado, est)
        print(f'{u["codigo"]}: nota {u["nota"]:g}, tempo {format(u["tempo_min"], "g") if u["tempo_min"] is not None else "?"} '
              f'(limite {u["limite_min"]:g} min) -> {"Domínio" if u["status"] == "dominio" else "Repetir"}')
    if a.comando in ('registrar', 'estado'):
        curso = carregar_curso(est['curso'])
        print(f'{est["aluno"]} ({est["curso"]}): próxima folha {gerador.proxima_folha(est, curso) or "nenhuma"}')
        pend = [u['codigo'] for u in est['unidades'] if u['status'] == 'pendente']
        if pend: print('  pendente:', ', '.join(pend))
        for u in est['unidades'][-5:]:
            if u['status'] != 'pendente':
                print(f'  {u["data"]}  {u["codigo"]:<10} nota {u["nota"]:g}  {u["status"]}')


# sem nada: menu (dois cliques no atalho); a janela espera um Enter antes de fechar, mesmo com erro
argv, pelo_menu = sys.argv[1:], len(sys.argv) == 1
if pelo_menu:
    from .assistente import menu
    argv = menu() or []
codigo = 0
try:
    if argv: main(argv)
except ErroEspecificacao as e:
    print(f'erro: {e}', file=sys.stderr); codigo = 1
except SystemExit as e:
    codigo = e.code if isinstance(e.code, int) else (print(e.code, file=sys.stderr) or 1)
except KeyboardInterrupt:
    print('\ninterrompido'); codigo = 1
if pelo_menu and argv: input('\nPressione Enter para fechar.')
sys.exit(codigo)
