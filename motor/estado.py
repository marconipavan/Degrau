# Degrau — adaptador de estado do aluno: arquivo JSON local (fora do git: estado/*.local.json).
# Outro adaptador (planilha, banco de dados) só precisa oferecer carregar e salvar com o mesmo formato.
#
# Formato:
#   curso, aluno, inicio (primeira folha do aluno, definida pelo nivelamento)
#   unidades: unidade diária (pacote do dia no francês, bloco no CASD), em ordem de entrega:
#     {pacote, codigo, folhas, versoes, data, limite_min, status (pendente|dominio|repetir),
#      nota, tempo_min, arquivo}
#   vocabulario, estruturas, erros_recorrentes: anotações livres para escrever as próximas folhas
import json, os


def carregar(caminho):
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def salvar(caminho, estado):
    """grava num arquivo temporário e troca: um erro no meio não corrompe o estado"""
    tmp = caminho + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, caminho)
