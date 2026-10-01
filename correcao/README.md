# Correção automática (Google Forms + Planilha + Apps Script)

Usado no piloto da turma. Fluxo: o aluno resolve as folhas do dia no caderno e envia pelo formulário;
o script compara com o gabarito e escreve nota, tempo e status (Domínio ou Repetir) no Painel.

## Formulário (um só, fixo)

| Campo | Tipo | Observação |
|---|---|---|
| Aluno | Lista suspensa | nomes da aba Alunos |
| Código do bloco | Resposta curta | formato `G1 10-12` (validado por expressão regular) |
| Início | Hora | início da primeira folha do bloco |
| Fim | Hora | fim da última folha |
| `1ª folha (a) · 1` … `3ª folha (b) · 12` | Resposta curta | uma seção por página (6 seções × 12 campos); o número do campo é o número do item na folha; em branco se a página tiver menos itens |
| Foto da resolução | Envio de arquivo (até 5 imagens) | exige login com conta Google |

## Planilha

Abas: `Alunos`, `Gabarito`, `Painel` (+ a aba de respostas criada pelo Forms); cabeçalhos em `modelos/`.

O gabarito não é escrito à mão: `./degrau proximo <estado>` (ou `./degrau exemplos <pacotes.yaml>`) gera, ao lado de cada PDF de geometria,
o arquivo `.planilha.csv` com as linhas da aba Gabarito (colunas: Bloco, Campo, Respostas aceitas, Pontos,
Tempo-padrão do bloco). O bloco diário tem as folhas indicadas em `bloco_diario` no currículo (3).
Se uma página passar de 12 itens, a geração falha. `modelos/gabarito.csv` é o bloco G1 1-3 gerado assim.

Como a resposta do aluno é comparada (`aoEnviar.gs`):

- sem diferença entre maiúsculas e minúsculas, acentos, `°` e espaços (`PÔQ` = `poq`, `Ra` = ` ra `);
- várias respostas aceitas separadas por `|` (ex.: `PQR|RQP`);
- `conjunto:A,B,C`: itens em qualquer ordem, separados por vírgula, ponto e vírgula ou espaço; nome de
  ângulo de 3 letras vale nos dois sentidos (`QÔP` = `PÔQ`). No YAML: `resposta: {conjunto: [...]}`;
- nota = pontos dos itens certos ÷ pontos do bloco; **Domínio** se nota ≥ 90 e tempo ≤ tempo-padrão do bloco
  (com `TEMPO_CONTA = false`, o tempo só é registrado);
- horário aceito como `19:02`, `19:02:00` ou `7:02:00 PM`; passar da meia-noite é tratado;
- bloco sem gabarito gera uma linha `ERRO: bloco sem gabarito` no Painel;
- envio repetido do mesmo bloco gera outra linha no Painel; vale a mais recente.

## Teste sem Google

```bash
node correcao/teste/simular.js     # também roda dentro do pytest
```

Roda o `aoEnviar.gs` de verdade, com planilha e formulário simulados e envios falsos (tudo certo,
variações de escrita, conjuntos, erros, limite de 90%, tempo estourado, horário AM/PM, bloco desconhecido),
e confere que o `montar.gs` cria um campo para cada linha do gabarito, com o mesmo título.

## Montagem, passo a passo (conta institucional do CASD)

1. **Planilha.** No Google Drive da conta institucional, crie uma planilha em branco (ex.: "Degrau — CASD").
2. **Script.** Extensões > Apps Script. Apague o conteúdo de `Código.gs` e cole `aoEnviar.gs`. Crie um
   segundo arquivo (+ > Script), chame de `montar` e cole `montar.gs`. Salve.
3. **Alunos.** Rode `montar` uma primeira vez (selecione a função `montar` > Executar; autorize o acesso).
   Ele cria as abas e para pedindo os alunos. Preencha a coluna A da aba `Alunos` (um nome por linha).
4. **Formulário.** Rode `montar` de novo. Ele cria o formulário "Degrau — entrega do bloco diário" ligado à
   planilha e o gatilho que chama `aoEnviar` a cada envio. Rode só uma vez: cada execução cria outro
   formulário e outro gatilho (confira em Acionadores, ícone de relógio, que há um só).
5. **Foto.** Abra o formulário e acrescente, no fim, a pergunta "Foto da resolução", tipo Envio de arquivo,
   até 5 imagens. (O Apps Script não cria esse tipo de pergunta.) Em Configurações, deixe a coleta de
   e-mail desligada; o envio de arquivo já exige login com conta Google.
6. **Gabarito.** Para cada pacote: gere com `./degrau proximo <estado do aluno>` e, na aba `Gabarito`,
   Arquivo > Importar > Upload > o `.planilha.csv` > "Anexar à página atual".
7. **Teste com envios falsos.** Abra o formulário (ícone de olho), envie como "Aluno Teste": uma vez com
   tudo certo, uma com dois erros, uma com bloco inexistente. Confira as três linhas no Painel: nota 100
   e Domínio; nota menor e os campos errados; `ERRO: bloco sem gabarito`. Apague as linhas de teste.
8. **Tempo.** Nas duas primeiras semanas do piloto, mude `TEMPO_CONTA` para `false` em `aoEnviar.gs`.
9. **Envio aos alunos.** Copie o link do formulário (Enviar > link) e mande junto com o PDF do pacote.

Se algo der errado no envio real, veja Apps Script > Execuções: cada envio aparece com o erro, se houver.

## Privacidade

Formulário e planilha na conta institucional, nunca na pessoal. Nada de dados de alunos neste repositório
(`.gitignore` já bloqueia `dados/`, `respostas/`, `fotos/`, `*.xlsx`).
