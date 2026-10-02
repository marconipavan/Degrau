# Degrau — guia de desenvolvimento

Para quem vai mexer no código. Quem só usa: `ADMINISTRACAO.md` (operação) e `PROFESSOR.md` (conteúdo).

## Princípios

1. **Núcleo genérico, instâncias em dados.** O motor não sabe nada de geometria nem de idiomas: conhece
   curso → níveis → unidades → folhas → itens. Cada curso é currículo + folhas em YAML.
2. **Figura e gabarito do mesmo cálculo.** Figuras são geradas da construção; ângulos são calculados e todo rótulo
   (`80°`, `3x + 5°`) é conferido contra o desenho. Se não fechar, a folha é recusada.
3. **Falhar alto.** Qualquer erro de especificação diz o arquivo, o lado, o bloco e o item.
4. **Sempre olhar as páginas.** Depois de mexer em layout: `degrau ver` e abrir o PDF. Vários defeitos só aparecem
   na imagem.
5. **Dados de alunos nunca no repositório** (`.gitignore`: `dados/`, `estado/*.local.json`, `.env.local`,
   `config.local.yaml`, `correcao/.clasp.json`).

## Mapa do código

| Arquivo | Papel |
|---|---|
| `motor/especificacao.py` | Lê e valida currículos, folhas (`N.yaml`, `N.vK.yaml`) e pacotes; `biblioteca()` lista as folhas escritas |
| `motor/render.py` | Tabela de tipos de bloco; layout por caixas (blocos fixos medidos num canvas descartável, elásticos dividem a sobra) |
| `motor/folha.py`, `motor/geo.py`, `motor/bicos.py`, `motor/figuras.py` | Desenho (reportlab): folha de papel, folha de caderno, figuras |
| `motor/medidas.py` | Ângulos de cada figura em minutos e conferência dos rótulos (incógnitas x e y) |
| `motor/verificar.py` | Texto fora da página, sobre texto ou sobre linha (testes e `validar`) |
| `motor/gabarito.py` | Gabarito por item; exporta CSV e `correcao/gabarito.gs` |
| `motor/audio.py` | Bloco de áudio para o leitor (cursos de idioma) |
| `motor/gerador.py`, `motor/estado.py` | Próximo pacote pelo estado do aluno: domínio, repetição com a versão seguinte, pendente bloqueia |
| `motor/turma.py`, `motor/envio.py` | Rotina semanal da turma: planilha baixada → resultados → pacotes → e-mails |
| `motor/assistente.py`, `motor/__main__.py` | Assistente de configuração, menu e linha de comando |
| `motor/autor.py` | Opcional: o Claude (API da Anthropic) escreve folhas que faltam |
| `correcao/*.gs` | Apps Script: `aoEnviar` corrige cada envio do formulário; `montar` cria abas, formulário e gatilho |
| `ferramentas/` | `esqueletos.py` (converte esqueletos para YAML), `comparar.sh` (PDFs contra uma referência) |

## Folhas

Cada folha: `folha`, `unidade`, `a`, `b`. Cada lado: `instrucao`, `icone` (`ouvir`, `escrever`, `ligar`, `circular`,
`ler`), `blocos` e, opcionais, `traducao` (só folhas de papel), `pontos` (total, "[100]") ou `pontos_cada`. Cada bloco
é um mapa de uma chave, o tipo; `resposta` alimenta o gabarito e nunca é desenhada.

Blocos de geometria: `exemplo` (`texto` e `figura`), `grade` (itens numerados; cada item com `texto`, uma figura,
`resposta`, e opcionalmente `alternativas`, `incognita: y`, `pontos`), `figura` (uma figura sem número),
`alternativas`, `texto`. Blocos de idioma: `palavras`, `ligar`, `circular`, `copiar`, `frases`, `banco`, `lacunas`,
`leitura`, `verdadeiro-falso`, `ditado`, `exemplo` (`frase` e `decomposicao`), `perguntas`, `ordenar`, `decompor`,
`subinstrucao`.

Figuras (medidas em mm; direções em graus, a partir da semirreta para a direita, sentido anti-horário):

```yaml
angulo:      {direcoes: [0, 50], nomes: [O, A, B], marca: arco, rotulo: "50°"}
semirretas:  {direcoes: [0, 40, 80], nomes: [A, M, B], vertice: O,
              marcas: [[A, M, ~, "2x + 10°"], [A, B, reto, ~]], tracejadas: [M]}
cruzadas:    {direcoes: [0, 70], ponto: O, marcas: [[0, 70, "3x + 10°"], [180, 250, "5x − 30°"]]}
transversal: {direcao: 75, marcas: [[r, acima-direita, "2x + 10°"], [s, abaixo-esquerda, y]]}
bico:        {altura: 30, segmentos: [[-35, 18], [-140, 0]], marcas: [[0, dir, ~], [1, ~, x], [2, dir, ~]]}
```

Rótulos: com `°` ou `'` é medida conferida com o desenho; com `x` ou `y` é expressão (todas as do mesmo x têm que
dar o mesmo valor); `~` escreve o valor calculado; sem nada disso (`3`, `a`) é só nome. No bico, o último segmento
vai até a reta s e item sem `resposta` usa o vértice marcado com `x`.

## Testes

```
.venv/bin/pytest            # se o ambiente tiver plugins estranhos no PYTHONPATH: env -u PYTHONPATH .venv/bin/pytest
node correcao/teste/simular.js
```

Os testes geram tudo, conferem margens e sobreposições em todas as páginas, o gabarito contra respostas conhecidas,
as expressões das figuras, o gerador (vários dias e repetições), a rotina da turma com planilha fictícia e e-mail
simulado, e o Apps Script real com planilha e formulário simulados. `degrau validar` confere a biblioteca inteira.

## Curso novo

1. `curriculos/<curso>.yaml` com a chave `folha` (marca, campos `papel` ou `caderno`, padrão do nome do arquivo),
   níveis com `folhas` e `tempo_padrao_min`, unidades com faixas.
2. Folhas em `folhas/<curso>/<nível>/`.
3. Se faltar um tipo de exercício ou de figura: acrescente em `motor/render.py` (tabela `TIPOS` ou `FIGURAS`), com
   desenho, conferência em `motor/medidas.py` quando houver cálculo, e teste.
