# Prompt: esqueletos das folhas do G1 (geometria, turma EPCAR do CASD)

Cole tudo o que está abaixo da linha numa conversa do Claude que já tenha o contexto das aulas da turma.

---

Preciso que você escreva o conteúdo das folhas de treino diário da minha turma de geometria plana (preparação
EPCAR, alunos de cerca de 14 anos, níveis muito diferentes). Depois eu converto cada folha para o formato do
sistema que gera os PDFs, então o que importa aqui é o conteúdo certo, num formato fixo e sem ambiguidade.

## Como o sistema funciona (para você escrever do jeito certo)

- Cada **folha** tem frente (a) e verso (b), formato A5, lida no **celular**. O aluno resolve **no caderno** e
  manda só as **respostas finais** por um formulário; um script corrige sozinho comparando com o gabarito.
- Cada página tem **uma única tarefa** (ex.: só nomear ângulos; só calcular o complemento).
- **Não há explicação teórica** na folha. A regra aparece num **exemplo resolvido**, num quadro no topo da página,
  quando a unidade começa ou quando entra uma ideia nova. A explicação fica para a aula.
- **Degraus mínimos:** cada folha é só um pouco mais difícil que a anterior; nunca duas ideias novas na mesma folha.
- O aluno faz **3 folhas por dia** (~10 minutos no total, 3 a 4 minutos por folha). Dimensione cada página para isso.
- Domínio = pelo menos 90% de acerto e tempo dentro do padrão; quem não domina repete o trecho com exercícios novos.

### Restrições de cada página (o formulário e a correção automática exigem)

1. **No máximo 12 itens com resposta por página** (o ideal é de 4 a 10).
2. **Resposta curta e objetiva**, que o aluno digita no celular: um número, um ângulo, uma letra, uma alternativa,
   um nome de ângulo (ex.: `AÔB`). Nada de resposta dissertativa.
3. Se houver mais de uma forma certa, liste todas (ex.: `PQR` e `RQP`). Se a resposta for uma lista em qualquer
   ordem, diga "conjunto, qualquer ordem".
4. Ângulos: escreva a resposta como número, com ou sem `°` (tanto faz, o corretor ignora o símbolo).
   Graus, minutos e segundos: sempre no formato `35°20'15"`.
5. **Pontos por item**, de modo que cada página some cerca de 100 (ex.: 4 itens de 25, 10 itens de 10).
6. Instrução de **uma linha**, no imperativo, até ~60 caracteres (ex.: "Calcule o complemento de cada ângulo.").

### Figuras

As figuras são **desenhadas por código a partir da construção**, e o gabarito sai do mesmo cálculo. Por isso,
**não desenhe nem descreva "de olho"**: dê os dados da construção, com os ângulos de verdade. Use este vocabulário
(direções em graus, medidas a partir da semirreta que aponta para a direita, no sentido anti-horário):

- **Ângulo:** vértice e as duas pontas, com as direções. Ex.: "ângulo de vértice O, ponta A na direção 0°,
  ponta B na direção 50°; marca de arco; escrever 50° na figura" (ou "marca de ângulo reto").
- **Semirretas de mesma origem:** origem e cada semirreta com nome e direção. Ex.: "origem O; A 0°, B 40°, C 85°".
  Se for preciso escrever valores ou expressões entre duas semirretas, diga entre quais e o quê.
- **Retas que se cruzam** (opostos pelo vértice): as duas direções e o que escrever em cada um dos 4 ângulos.
- **Paralelas cortadas por uma transversal:** retas r e s horizontais, a direção da transversal, e o que escrever
  em cada um dos 8 ângulos, identificando cada um pela reta (r ou s) e pela posição (acima/abaixo,
  esquerda/direita). Ex.: "em r, acima à direita: 3x + 10°".
- **Bico entre paralelas** (zigue-zague entre r e s): a sequência de segmentos com direção e comprimento
  aproximado, e o que escrever em cada ângulo (o valor, `x` ou uma expressão como `3x + 5°`).

Confira que tudo fecha: as expressões têm que dar o ângulo desenhado com o mesmo x, e a resposta tem que sair da
figura. O sistema recalcula e recusa a folha se não fechar.

## O que já existe (continue a partir disso, no mesmo estilo)

- **G1 1** — Reconhecer ângulos 1. a: exemplo "ângulo AÔB, vértice O, lados OA e OB"; nomear 4 ângulos da figura
  (aceita as duas ordens). b: classificar 10 valores em agudo (A), reto (R), obtuso (O) ou raso (Ra).
- **G1 2** — Reconhecer ângulos 2. a: classificar 6 ângulos pela figura (A, R, O). b: escrever todos os ângulos com
  vértice O formados por 4 semirretas (conjunto, qualquer ordem); e, com 5 semirretas, só dizer quantos são (10).
- **G1 3** — Reconhecer ângulos 3. a: tipo do ângulo a partir de uma conta ("o dobro de 45°", "180° − 1°"…).
  b: revisão de 1 a 3 (vértice de XŶZ; nome e tipo de um ângulo da figura; nome do ângulo de 90°; quantos ângulos
  5 semirretas formam; o dobro de um agudo pode ser obtuso? S/N).
- **G1 81** — O bizu dos bicos 1. a: exemplo (bico para a direita: x = 30° + 40° = 70°) + 4 figuras, x no bico.
  b: o x passa para a paralela (mesma ideia ao contrário), 4 figuras.
- **G1 85** — O bizu dos bicos 5. a: dois bicos; exemplo "a soma dos ângulos que abrem para a esquerda é igual à
  soma dos que abrem para a direita" + 4 figuras. b: 4 figuras sem exemplo.
- **G1 89** — O bizu dos bicos 9. a: os ângulos viram expressões (x + 5°, 3x + 5°…), montar a equação e achar x,
  2 figuras. b: questão no formato de prova, 4 alternativas.

## O que escrever: 94 folhas + a prova de nivelamento

O nome da unidade na folha é o nome da unidade seguido da posição da folha na faixa (ex.: G1 12 é
"Graus, minutos e segundos 2").

| Folhas | Unidade | Conteúdo |
|---|---|---|
| G1 4 a 10 | Reconhecer ângulos (4 a 10) | vértice, lados, notação; agudo, reto, obtuso, raso |
| G1 11 a 20 | Graus, minutos e segundos (1 a 10) | converter, somar, subtrair, multiplicar e dividir por inteiro (é uma unidade inteira mesmo) |
| G1 21 a 30 | Complemento e suplemento (1 a 10) | cálculo direto; complemento do suplemento |
| G1 31 a 40 | Equações com ângulos (1 a 10) | "o suplemento de x é o triplo do complemento de x" |
| G1 41 a 50 | Posições (1 a 10) | adjacentes, consecutivos, bissetriz, opostos pelo vértice |
| G1 51 a 60 | Revisão 1 (1 a 10) | 1 a 50 misturado; **sem questões de prova** (elas só entram a partir da 91) |
| G1 61 a 70 | Paralelas: identificar (1 a 10) | correspondentes, alternos, colaterais |
| G1 71 a 80 | Paralelas: calcular (1 a 10) | expressões do tipo 2x + 10° |
| G1 82, 83, 84, 86, 87, 88, 90 | O bizu dos bicos (2, 3, 4, 6, 7, 8, 10) | encaixe entre as que já existem: 82–84 consolidam um bico (x no bico e na paralela, ângulos menos "redondos"); 86–88 consolidam dois ou mais bicos; 90 fecha a unidade (misturado) |
| G1 91 a 100 | Questões de prova (1 a 10) | EPCAR e Colégio Naval, revisão final; até 3 questões por página, cada uma com alternativas e uma única certa |

**Prova de nivelamento:** 10 questões, uma por unidade (na ordem das unidades acima), da mais fácil para a mais
difícil, cada uma resolvível em 1 a 2 minutos, resposta curta. Ela define em que folha cada aluno entra (um pouco
abaixo de onde ele começa a errar).

## Formato de entrega

Um arquivo `.md` por folha, com nome `G1_004.md` … `G1_100.md` (número com 3 dígitos), mais `NIVELAMENTO_G1.md` e
um `INDICE.md` com uma linha por folha: número, unidade e o degrau novo daquela folha. Entregue tudo num
`.zip` chamado `esqueletos-G1.zip`. Se for longo demais para uma resposta, faça por unidade (10 folhas por vez) e
junte no fim; prefiro qualidade a pressa.

Modelo de cada arquivo (siga exatamente esta estrutura):

```
# G1 23 — Complemento e suplemento 3
Degrau novo: (uma frase: o que esta folha acrescenta em relação à anterior)

## Frente (G1 23a)
Tarefa: (o tipo da tarefa, ex.: calcular o suplemento)
Instrução: (uma linha)
Pontos: 10 cada
Exemplo resolvido: (opcional; o enunciado e a resolução em uma ou duas linhas, sem teoria)
Itens:
1. Enunciado: ... | Figura: (só se houver; construção no vocabulário acima) | Resposta: ... | Aceitar também: ...
2. ...

## Verso (G1 23b)
(mesma estrutura)
```

Para questão de prova (G1 91 a 100), cada item fica assim:

```
1. Enunciado: ... | Figura: ... | Alternativas: (A) ... (B) ... (C) ... (D) ... | Resposta: C | Fonte: EPCAR 2019 (se for adaptada de prova real)
```

Antes de entregar, confira em cada folha: uma única tarefa por página; no máximo 12 itens com resposta por página;
nenhuma explicação teórica; resposta certa e coerente com a figura; e só uma ideia nova em relação à folha anterior.
