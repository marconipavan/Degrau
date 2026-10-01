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
| `1ª folha (a) · 1` … `3ª folha (b) · 12` | Resposta curta | uma seção por página (6 seções × 12 campos); o número do campo é o número do item na folha; em branco se a página tiver menos itens |
| Foto da resolução | Envio de arquivo (até 5 imagens) | exige login com conta Google |

## Planilha

Abas (modelos em `modelos/`): `Alunos`, `Gabarito`, `Painel` (+ a aba de respostas criada pelo Forms).
No gabarito, várias respostas aceitas vão separadas por `|`. O tempo-padrão do bloco é a soma
dos tempos-padrão das folhas.

O gabarito não é escrito à mão: `python -m motor <pacotes.yaml>` gera, ao lado de cada PDF de geometria,
o arquivo `.planilha.csv` com as linhas da aba Gabarito (colunas: Bloco, Campo, Respostas aceitas, Pontos,
Tempo-padrão do bloco). O bloco diário tem as folhas indicadas em `bloco_diario` no currículo (3).
Se uma página passar de 12 itens, a geração falha. `modelos/gabarito.csv` é o bloco G1 1-3 gerado assim.

**Pendente (fase 3):** itens cuja resposta é um conjunto em qualquer ordem (G1 2b, item 1: os 6 ângulos)
não são corrigidos certo pela comparação exata; decidir entre aceitar em qualquer ordem no script ou pedir
só a contagem.

## Privacidade

Formulário e planilha na conta institucional, nunca na pessoal. Nada de dados de alunos neste repositório
(`.gitignore` já bloqueia `dados/`, `respostas/`, `fotos/`, `*.xlsx`).
