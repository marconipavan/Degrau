# Linha de comando. Use ./degrau <comando> (ou python -m motor <comando>):
#   exemplos  <pacotes.yaml> [saída]            gera pacotes fixos (PDF + gabarito + áudio)
#   proximo   <estado.json> [--dias N]          gera o próximo pacote do aluno e o marca como pendente
#   registrar <estado.json> <código> --nota N [--tempo MIN]   registra a correção: domínio ou repetir
#   estado    <estado.json>                     resumo: próxima folha, pendentes, últimas notas
import argparse, os, sys
from .especificacao import ErroEspecificacao, RAIZ, carregar_curso
from . import estado as E, gerador, render


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
    a = ap.parse_args()

    if a.comando == 'exemplos':
        for arquivos, esconder in render.gerar(a.pacotes, a.saida): _mostrar(arquivos, esconder)
        return
    est = E.carregar(a.estado)
    if a.comando == 'proximo':
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
