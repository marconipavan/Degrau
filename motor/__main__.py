# Linha de comando. Use ./degrau <comando> (ou python -m motor <comando>):
#   exemplos  <pacotes.yaml> [saída]            gera pacotes fixos (PDF + gabarito + áudio)
#   proximo   <estado.json> [--dias N]          gera o próximo pacote do aluno e o marca como pendente
#   registrar <estado.json> <código> --nota N [--tempo MIN]   registra a correção: domínio ou repetir
#   estado    <estado.json>                     resumo: próxima folha, pendentes, últimas notas
#   automatico <estado.json> [--pedido]         o Claude escreve as folhas que faltam (API) e gera o pacote;
#                                               --pedido só grava o pedido em saida/pedido.txt, sem chamar a API
import argparse, os, sys
from .especificacao import ErroEspecificacao, RAIZ, carregar_curso
from . import estado as E, gerador, render, autor


def _mostrar(arquivos, esconder):
    for a in arquivos: print(a)
    if esconder: print('  esconder o texto ao ouvir:', ', '.join(esconder))


def main():
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
    a = ap.parse_args()

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


try:
    main()
except ErroEspecificacao as e:
    sys.exit(f'erro: {e}')
