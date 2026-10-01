# uso: python -m motor exemplos/pacotes.yaml [pasta_de_saida]
import sys
from .especificacao import ErroEspecificacao
from .render import gerar

if len(sys.argv) not in (2, 3):
    sys.exit('uso: python -m motor <pacotes.yaml> [pasta_de_saida]')
try:
    for caminho in gerar(*sys.argv[1:]):
        print(caminho)
except ErroEspecificacao as e:
    sys.exit(f'erro: {e}')
