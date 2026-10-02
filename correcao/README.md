# Correção automática (Google Forms + Planilha + Apps Script)

Usado no piloto da turma. Fluxo: o aluno resolve as folhas do dia no caderno e envia pelo formulário;
o script compara com o gabarito e escreve nota, tempo e status (Domínio ou Repetir) no Painel.

## Formulário (um só, fixo)

| Campo | Tipo | Observação |
|---|---|---|
| Aluno | Lista suspensa | nomes da aba Alunos |
| Código do bloco | Resposta curta | copiado da folha: `G1 10-12`, `G1 100` ou, numa repetição, `G1 10-12 v2` |
| Início | Hora | início da primeira folha do bloco |
| Fim | Hora | fim da última folha |
| `1ª folha (a) · 1` … `3ª folha (b) · 12` | Resposta curta | uma seção por página (6 seções × 12 campos); o número do campo é o número do item na folha; em branco se a página tiver menos itens |
| Foto da resolução | Envio de arquivo (até 5 imagens) | **opcional, fica para depois** (decisão de 02/10/2026); exige login com conta Google |

## Planilha

Abas: `Alunos`, `Gabarito`, `Painel` (+ a aba de respostas criada pelo Forms); cabeçalhos em `modelos/`.

- **Alunos:** Aluno, E-mail, Nível atual, Próximo bloco, Entrada (nivelamento). Os e-mails são preenchidos pela
  administração do curso e ficam só na planilha da conta institucional.
- **Gabarito:** uma linha por item, **por folha e versão**: Folha, Versão, Página, Item, Respostas aceitas, Pontos,
  Tempo-padrão da folha (min). Carrega-se **uma vez** com a biblioteca inteira, gerada por
  `./degrau gabarito geometria-plana-epcar`, e de novo quando entrarem folhas novas.
  `modelos/gabarito.csv` é esse arquivo para as folhas escritas hoje.
- **Painel:** escrito pelo script, uma linha por envio.

Como o envio é corrigido (`aoEnviar.gs`):

- o código do bloco diz quais folhas e qual versão (`G1 10-12 v2` → G1 10, 11 e 12 na versão 2); a 1ª folha do
  bloco corresponde à seção "1ª folha" do formulário, e assim por diante;
- sem diferença entre maiúsculas e minúsculas, acentos, `°` e espaços (`PÔQ` = `poq`, `Ra` = ` ra `); aspas do
  celular (’ ′ ” e duas aspas simples) valem como `'` e `"`, para minutos e segundos;
- várias respostas aceitas separadas por `|` (ex.: `PQR|RQP`);
- `conjunto:A,B,C`: itens em qualquer ordem, separados por vírgula, ponto e vírgula ou espaço; nome de
  ângulo de 3 letras vale nos dois sentidos (`QÔP` = `PÔQ`). No YAML: `resposta: {conjunto: [...]}`;
- nota = pontos dos itens certos ÷ pontos do bloco; **Domínio** se nota ≥ 90 e tempo ≤ soma dos tempos-padrão
  das folhas (com `TEMPO_CONTA = false`, o tempo só é registrado);
- horário aceito como `19:02`, `19:02:00` ou `7:02:00 PM`; passar da meia-noite é tratado;
- erros viram uma linha `ERRO: …` no Painel: código do bloco inválido, ou folha sem gabarito (por exemplo, uma
  versão 2 que ainda não foi carregada);
- envio repetido do mesmo bloco gera outra linha no Painel; vale a mais recente.

## Teste sem Google

```bash
node correcao/teste/simular.js     # também roda dentro do pytest
```

Roda o `aoEnviar.gs` de verdade, com planilha e formulário simulados e envios falsos, e confere que o
`montar.gs` cria um campo para cada item do gabarito, com o mesmo título.

## Montagem, passo a passo (conta institucional do CASD)

Leva uns 20 minutos. Use sempre a **conta institucional**, nunca a pessoal.

### Parte 1 — Criar a planilha e colocar os scripts

Escolha **um** dos dois caminhos.

**Caminho A, pela `clasp` (recomendado: depois disso o Claude Code atualiza os scripts pelo VS Code).**
A `clasp` é a ferramenta oficial do Google para editar Apps Script no computador.

1. Ative a API do Apps Script na conta institucional: abra https://script.google.com/home/usersettings e ligue
   "API do Google Apps Script".
2. No terminal: `npm install -g @google/clasp`.
3. `clasp login`: abre o navegador; entre com a conta institucional e autorize. A credencial fica em
   `~/.clasprc.json`, fora do repositório.
4. Na pasta do projeto:
   ```bash
   cd correcao
   clasp create-script --type sheets --title "Degrau — CASD" --rootDir .
   clasp push
   ```
   O primeiro comando cria a planilha e o projeto de script ligado a ela; o segundo envia `aoEnviar.gs`,
   `montar.gs` e `appsscript.json` (o arquivo `.clasp.json` criado aqui fica fora do git). Comandos conferidos
   na `clasp` 3.4.1; `clasp status` mostra o que seria enviado (só esses três arquivos).
5. `clasp open-script` abre o editor do script no navegador. A planilha aparece no seu Drive com o nome
   "Degrau — CASD".

**Caminho B, à mão.**

1. No Drive da conta institucional, crie uma planilha em branco chamada "Degrau — CASD".
2. Extensões > Apps Script. Apague o conteúdo de `Código.gs` e cole `aoEnviar.gs`. Crie um segundo arquivo
   (+ > Script), chame de `montar` e cole `montar.gs`. Salve.

### Parte 2 — Montar abas, formulário e gatilho

1. No editor do script, escolha a função `montar` no menu de cima e clique em **Executar**. Na primeira vez o
   Google pede autorização: avance, escolha a conta institucional e permita (planilha, formulário, gatilhos).
   O `montar` cria as abas `Alunos`, `Gabarito` e `Painel` e para com a mensagem "Preencha a aba Alunos".
2. Na aba `Alunos`, coloque um aluno por linha: **nome** na coluna A e **e-mail** na coluna B. Os e-mails podem
   ser preenchidos pela administração. Inclua uma linha "Aluno Teste" para os testes.
3. Rode `montar` de novo. Ele cria o formulário "Degrau — entrega do bloco diário", liga o formulário à planilha
   (aparece uma aba de respostas) e cria o gatilho que chama `aoEnviar` a cada envio.
   **Rode só esta vez:** cada execução cria outro formulário e outro gatilho. Confira em Acionadores (ícone de
   relógio, à esquerda no editor) que existe um só, `aoEnviar`, "Ao enviar o formulário".
4. (Opcional, fica para depois.) Para receber fotos da resolução: abra o formulário e acrescente **no fim** a
   pergunta "Foto da resolução", tipo **Envio de arquivo**, até 5 arquivos, só imagens. O Apps Script não consegue
   criar esse tipo de pergunta. Sem ela, a correção funciona igual (a coluna Fotos do Painel fica vazia).
5. Ainda no formulário, em Configurações > Respostas: deixe "Coletar endereços de e-mail" desligado e
   "Limitar a uma resposta" desligado (o aluno envia todo dia).

### Parte 3 — Carregar o gabarito

1. No computador do projeto: `./degrau gabarito geometria-plana-epcar` (gera
   `saida/gabarito-geometria-plana-epcar.csv` com a biblioteca inteira).
2. Na planilha, abra a aba `Gabarito` e use Arquivo > Importar > Upload > esse arquivo, com
   **"Substituir a página atual"** e **"Converter texto em números, datas e fórmulas: Não"** (sem isso, uma
   resposta como `1/2` vira data).
3. Repita sempre que entrarem folhas novas na biblioteca.

### Parte 4 — Testar com envios falsos

Use o bloco G1 1-3, que já existe: `./degrau ver G1 1-3` gera o PDF em `saida/ver/` e mostra o gabarito com
a mesma numeração dos campos (ex.: `G1 1b · 4: Ra` é o campo "1ª folha (b) · 4").

1. Abra o formulário em modo de visualização (ícone de olho) e envie como "Aluno Teste", código `G1 1-3`, início
   19:00, fim 19:10, todas as respostas certas. No Painel deve aparecer: nota 100, tempo 10, limite 12, Domínio.
2. Envie de novo com duas respostas erradas. Deve aparecer a nota menor e, em "Itens errados", os dois campos.
3. Envie com o código `G1 101-103` (folhas que não existem). Deve aparecer `ERRO: sem gabarito: G1 101, G1 102, G1 103`.
4. Se algo não aparecer: no editor do script, menu Execuções, cada envio mostra o erro, se houver.
5. Apague as linhas de teste do Painel e da aba de respostas.

### Parte 5 — Antes do piloto

1. Nas duas primeiras semanas, o tempo só é registrado: em `aoEnviar.gs`, `TEMPO_CONTA = false` (pelo caminho A,
   o Claude Code muda e roda `clasp push`; pelo caminho B, edite no editor e salve).
2. Copie o link do formulário (Enviar > ícone de link) para mandar aos alunos junto com o primeiro pacote.

O envio automático dos pacotes por e-mail para cada aluno (fase 6) ainda não está pronto; ele vai ler os e-mails
da aba `Alunos`.

## Privacidade

Formulário e planilha na conta institucional, nunca na pessoal. Nada de dados de alunos neste repositório
(`.gitignore` já bloqueia `dados/`, `respostas/`, `fotos/`, `*.xlsx`, `correcao/.clasp.json`).
