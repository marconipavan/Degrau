# Degrau — guia do professor

Para quem escreve e revisa as folhas. A turma recebe as folhas pelo e-mail que a administração envia (veja
`ADMINISTRACAO.md`); aqui está o que fica com o professor: o conteúdo.

## O método, em poucas linhas

- **Degraus mínimos:** cada folha um pouco mais difícil que a anterior; nunca duas ideias novas na mesma folha.
- **Exemplo, não explicação:** a regra aparece num exemplo resolvido no topo da página, sem teoria.
- **Uma tarefa por página**, frente (a) e verso (b).
- **Domínio:** pelo menos 90% de acerto e tempo dentro do padrão. Sem domínio, o aluno refaz o mesmo trecho com
  exercícios **novos** (a versão 2 das folhas).
- **Todo dia um bloco** de 3 folhas (uns 10 minutos), resolvido no caderno; o aluno envia só as respostas finais.

## Onde estão as folhas

Uma folha por arquivo: `folhas/<curso>/<nível>/<número>.yaml` (ex.: `folhas/geometria-plana-epcar/G1/23.yaml`).
A versão 2 de uma folha, usada na repetição, é `23.v2.yaml`. O currículo (níveis e unidades) está em
`curriculos/<curso>.yaml`.

Cada folha diz o conteúdo e a resposta de cada item; o programa desenha o PDF, monta o gabarito e confere tudo.
O formato completo, com todos os tipos de exercício e de figura, está em `DESENVOLVIMENTO.md` (seção "Folhas");
o jeito mais fácil de começar é copiar uma folha parecida e mudar.

Regras que o formulário e a correção automática exigem:

- no máximo **12 itens com resposta por página**;
- **respostas curtas**: número, ângulo, letra, alternativa (várias formas aceitas: `PQR|RQP`; lista em qualquer
  ordem: `{conjunto: [...]}`);
- figuras são descritas pela **construção** (direções, rótulos), nunca desenhadas à mão: o programa calcula os
  ângulos e recusa a folha se um rótulo não fechar com o desenho.

## Comandos

Na pasta do Degrau (Linux e macOS: `./degrau ...`; Windows: `degrau ...`):

| Comando | Para quê |
|---|---|
| `degrau validar` | Confere todas as folhas (estrutura, margens, sobreposição, gabarito, limite do formulário) e lista as que faltam. Rode sempre depois de mexer. |
| `degrau ver G1 23` ou `degrau ver G1 21-30` | Gera o PDF dessas folhas em `saida/ver/` e mostra o gabarito com a numeração do formulário. |
| `degrau ver G1 23 --versao 2` | O mesmo para a versão 2. |
| `degrau gabarito geometria-plana-epcar` | O gabarito inteiro numa planilha (CSV), para conferência. |
| `degrau atualizar-gabarito` | Depois de mudar ou acrescentar folhas: leva o gabarito novo ao Google (ou peça à administração). |

## Escrever muitas folhas de uma vez

`docs/prompts/esqueletos-g1.md` é o pedido que gerou os esqueletos do G1 numa conversa com o Claude. Para outro
nível, adapte a tabela de unidades e o que já existe; o resultado (arquivos `G1_NNN.md`) é convertido para o formato
das folhas por:

```
.venv/bin/python ferramentas/esqueletos.py <pasta com os .md> geometria-plana-epcar
```

O conversor para em qualquer frase de figura que não conheça, em vez de adivinhar. Depois: `degrau validar`,
`degrau ver`, revisão de professor e `degrau atualizar-gabarito`.

## Quando um aluno precisa repetir

O resumo da rotina semanal avisa: `faltam folhas na biblioteca` com os arquivos exatos (ex.: `G1/7.v2.yaml`).
Escreva a versão 2 dessas folhas (mesmo objetivo, itens novos), rode `degrau validar` e
`degrau atualizar-gabarito`. Na rotina seguinte o aluno recebe as folhas novas.
