# Degrau — guia de quem opera

Este guia é para quem cuida do Degrau no dia a dia. Não é preciso saber programar: cada passo diz exatamente o que
clicar ou digitar. A instalação e a configuração são feitas **uma vez**; depois, o trabalho é de alguns minutos
depois de cada aula.

## Como funciona, em uma frase

Depois de cada aula, você baixa a planilha com os resultados dos alunos, abre o Degrau e escolhe "Rotina da semana":
ele corrige o andamento de cada aluno, prepara as folhas seguintes de cada um e manda por e-mail.

Os alunos resolvem as folhas no caderno e enviam as respostas por um formulário do Google, que corrige sozinho e
anota o resultado na planilha.

## O que é preciso

- Um computador com Windows, macOS ou Linux, com internet.
- A **conta Gmail da instituição**, com a **verificação em duas etapas** ligada
  (myaccount.google.com > Segurança). É dela que saem os e-mails e é nela que ficam a planilha e o formulário.
  Os dados dos alunos nunca ficam em conta pessoal.
- Uns 30 minutos para instalar e configurar.

## 1. Instalar (uma vez)

1. **Python.** Baixe em [python.org/downloads](https://www.python.org/downloads/) e instale.
   No Windows, na primeira tela do instalador, **marque "Add python.exe to PATH"**.
2. **Node.js.** Baixe a versão "LTS" em [nodejs.org](https://nodejs.org/) e instale (pode aceitar tudo).
3. **Ferramenta do Google para o script da planilha.** Abra o Terminal (no Windows: menu Iniciar > "cmd") e digite:
   ```
   npm install -g @google/clasp
   ```
   Se aparecer erro de conexão, tente de novo; os avisos com a palavra "deprecated" podem ser ignorados.
4. **O Degrau.** Baixe a pasta do projeto (no GitHub: botão "Code" > "Download ZIP"), descompacte num lugar fixo,
   por exemplo `Documentos/Degrau`.
5. **Instalar o Degrau.** Na pasta do Degrau:
   - Windows: dois cliques em `instalar.py`.
   - macOS e Linux: no Terminal, dentro da pasta, digite `python3 instalar.py`.

   No fim deve aparecer "Pronto". Se aparecer outra mensagem, ela diz o que falta.

## 2. Configurar (uma vez)

Abra o Degrau e escolha **4. Configurar**:

- Windows: dois cliques em `degrau.cmd`.
- macOS: dois cliques em `Degrau.command`.
- Linux: no Terminal, dentro da pasta, `./degrau`.

O assistente tem quatro passos. Em cada um ele mostra o que já está feito e pergunta antes de mexer; dá para parar e
voltar depois.

1. **Turma.** O curso (já vem `geometria-plana-epcar`) e quantos dias de treino há entre uma aula e a seguinte
   (cada dia é um bloco de 3 folhas).
2. **E-mail.** O endereço do Gmail da instituição e uma **senha de app** — não é a senha da conta. Para criar:
   [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) > dê o nome "Degrau" > copie as
   16 letras. O assistente manda um e-mail de teste para você conferir.
3. **Google.** Antes, ligue a "API do Google Apps Script" em
   [script.google.com/home/usersettings](https://script.google.com/home/usersettings), com a conta da instituição.
   O assistente abre o navegador para você entrar **com a conta da instituição**, cria a planilha "Degrau" e o script
   que corrige os envios, e abre o editor do script. Lá:
   1. no alto, escolha a função **montar** e clique em **Executar**; o Google pede autorização: avance, escolha a
      conta da instituição e permita (se aparecer "app não verificado", clique em "Avançado" > "Acessar");
   2. abra a planilha "Degrau" (no Google Drive) e, na aba **Alunos**, coloque um aluno por linha:
      **nome** na coluna A e **e-mail** na coluna B;
   3. volte ao editor e execute **montar** mais uma vez: ele cria o formulário e liga a correção automática.
      **Não rode o montar uma terceira vez** (criaria outro formulário).
4. **Link do formulário.** No Google Drive, abra o formulário "Degrau — entrega do bloco diário" > botão **Enviar** >
   ícone de link > **Copiar**, e cole no assistente. Esse link vai em todos os e-mails para os alunos.

**Teste antes de usar com a turma:** coloque na aba Alunos um aluno de teste com o seu próprio e-mail, faça uma
rotina da semana (abaixo) e responda o formulário como se fosse ele. Na semana seguinte, o resultado aparece no
resumo.

## 3. Rotina da semana (depois de cada aula, uns 5 minutos)

1. **Baixe a planilha:** abra a planilha "Degrau" no Google Drive > Arquivo > Fazer download >
   **Microsoft Excel (.xlsx)**.
2. **Abra o Degrau** (dois cliques, como acima) e escolha **1. Rotina da semana**. Uma janela pede a planilha que
   você acabou de baixar (normalmente na pasta Downloads).
3. **Confira o resumo.** Para cada aluno aparece:
   - `resultado` — o que ele enviou desde a última vez (Domínio: avança; Repetir: refaz o trecho);
   - `pacote` — as folhas que ele vai receber agora;
   - `PENDENTE` — blocos que ele ainda não enviou: ele recebe só um lembrete, sem folhas novas;
   - `ERRO` — algo que precisa de atenção (veja "Problemas comuns").
4. Responda **s** para enviar os e-mails. Só depois do envio o andamento de cada aluno é gravado; se você responder
   "não", nada muda e dá para rodar de novo.

## 4. Outras tarefas

- **Entrou ou saiu um aluno:** ajuste a aba Alunos (nome e e-mail) e, na planilha, use o menu
  **Degrau > Atualizar lista de alunos no formulário**. Aluno novo começa na primeira folha.
- **O professor mudou ou acrescentou folhas:** abra o Degrau e escolha **2. Atualizar o gabarito no Google**.
- **Cópia de segurança:** copie, de vez em quando, a pasta `dados` e os arquivos `config.local.yaml`, `.env.local`
  e `correcao/.clasp.json` para um lugar seguro (são eles que guardam o andamento dos alunos e a configuração).
  Mesmo sem cópia, o andamento pode ser reconstruído a partir do Painel da planilha.
- **Trocar de computador:** instale de novo (parte 1) e copie para a pasta nova esses mesmos quatro itens.
- **Versão nova do Degrau:** baixe a pasta nova e copie para ela os quatro itens acima; depois rode `instalar.py`.

## Problemas comuns

| O que aparece | O que fazer |
|---|---|
| "o Gmail recusou o login" | A senha de app está errada ou foi apagada. Crie outra (parte 2, passo 2) e rode Configurar > E-mail. |
| "e-mail não configurado" | Rode Configurar > E-mail. |
| Aluno não aparece na lista do formulário | Menu da planilha: Degrau > Atualizar lista de alunos no formulário. |
| No Painel: `ERRO: código do bloco inválido` | O aluno digitou o código errado. O código certo está no alto de cada folha (ex.: `G1 4-6`). Peça para enviar de novo. |
| No Painel: `ERRO: sem gabarito` | Escolha 2. Atualizar o gabarito no Google. Se continuar, avise o professor. |
| No resumo: `ERRO faltam folhas na biblioteca` | O aluno precisa repetir um trecho e a versão nova dessas folhas ainda não foi escrita. Avise o professor, que escreve as folhas indicadas. |
| No resumo: `sem e-mail na aba Alunos` | Preencha o e-mail do aluno na coluna B da aba Alunos e rode a rotina de novo. |
| "não existe config.local.yaml" | Rode `instalar.py` de novo e depois Configurar. |

## Privacidade

Os alunos são menores de idade. Planilha, formulário e e-mails ficam só na conta da instituição; a pasta `dados`
fica só neste computador. Nada disso vai para o repositório público do Degrau.
