# uso: python -m motor exemplos/pacotes.yaml [pasta_de_saida]
import sys
from .especificacao import ErroEspecificacao
from .render import gerar

if len(sys.argv) not in (2, 3):
    sys.exit('uso: python -m motor <pacotes.yaml> [pasta_de_saida]')
try:
    for arquivos, esconder in gerar(*sys.argv[1:]):
        for a in arquivos: print(a)
        if esconder: print('  esconder o texto ao ouvir:', ', '.join(esconder))
except ErroEspecificacao as e:
    sys.exit(f'erro: {e}')
