# Correção automática (Google Forms + Planilha + Apps Script)

Usado no piloto da turma. Fluxo: o aluno resolve as folhas do dia no caderno e envia pelo formulário;
o script compara com o gabarito e escreve nota, tempo e status (Domínio ou Repetir) no Painel.

## Formulário (um só, fixo)

| Campo | Tipo | Observação |
|---|---|---|
| Aluno | Lista suspensa | nomes da aba Alunos |
| Código do bloco | Resposta curta | formato `G1 10-12`; validar com expressão regular `^G\d+ \d+-\d+$` |
| Início | Hora | início da primeira folha do bloco |
| Fim | Hora | fim da última folha |
| Resposta 1 … Resposta 15 | Resposta curta | só a resposta final; em branco se o bloco tiver menos itens |
| Foto da resolução | Envio de arquivo (até 5 imagens) | exige login com conta Google |

## Planilha

Abas (modelos em `modelos/`): `Alunos`, `Gabarito`, `Painel` (+ a aba de respostas criada pelo Forms).
No gabarito, várias respostas aceitas vão separadas por `|`. O tempo-padrão do bloco é a soma
dos tempos-padrão das folhas.

**Limitação conhecida do modelo de gabarito:** hoje o gabarito é por *item do formulário*, e o
bloco G1 1-3 tem mais itens do que 15 campos. Antes do piloto, decidir: (a) gabarito só dos
itens objetivos mais importantes, ou (b) aumentar o número de campos, ou (c) um envio por folha.
O `gabarito.csv` traz só um trecho, como exemplo de formato.

## Privacidade

Formulário e planilha na conta institucional, nunca na pessoal. Nada de dados de alunos neste repositório
(`.gitignore` já bloqueia `dados/`, `respostas/`, `fotos/`, `*.xlsx`).
