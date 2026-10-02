# CLAUDE.md — Degrau

Documento de passagem. Tudo o que foi decidido e construído numa conversa no claude.ai (30/09 a 01/10/2026),
para que o Claude Code continue o trabalho sem perder contexto. Leia inteiro antes de mexer no código.

O plano original, com mais narrativa e todos os gabaritos, está em `docs/plano-completo.md`.

---

## 0. Resumo em dez linhas

1. **O que é:** um sistema genérico de folhas de estudo diárias inspirado no método de folhas individualizadas (frente e verso, A5, uma tarefa por página, degraus mínimos, domínio antes de avançar, compromisso diário).
2. **Núcleo genérico + instâncias.** O francês e o CASD **não são projetos separados**: são duas instâncias do mesmo núcleo. Toda decisão de arquitetura deve servir a qualquer matéria.
3. **Instância 1 — Francês (uso pessoal do Ângelo):** meta DELF B1 no 2º semestre de 2027. Pacote diário de 5 folhas, áudio por texto para fala, caderno de progresso, lembretes 06:30 e 23:30. **Já em uso.**
4. **Instância 2 — CASD (turma de geometria plana, preparação EPCAR):** alunos recebem o PDF no celular, resolvem no caderno, mandam respostas curtas + foto por um Google Forms; um Apps Script corrige e preenche um painel. **Desenhado, não implantado.**
5. **Estado do código:** funciona, mas é *ad hoc*: cada folha é escrita em Python com posições fixas. Não há especificação em dados ainda.
6. **Próximo passo principal (fase 1):** separar conteúdo de desenho — folhas e currículos descritos em YAML, motor só lê e desenha.
7. **Regra de ouro das figuras:** figura e gabarito saem do **mesmo cálculo**. Nunca desenhar uma figura e escrever o gabarito à parte.
8. **Proibido:** nome, logo ou identidade visual de qualquer marca comercial de método de ensino; dados de alunos no repositório.
9. **Idioma:** documentação e comentários em português; conteúdo das folhas de francês em francês.
10. **O usuário:** Ângelo, professor de matemática no CASD. Quer a solução mais simples que funcione, explicações diretas e termos por extenso (siglas só em código, fórmulas e gráficos).

---

## 1. Estado atual (01/10/2026)

### O que existe e funciona

| Peça | Onde | Estado |
|---|---|---|
| Especificações em YAML | `folhas/<curso>/<nível>/<número>.yaml` | Uma folha (frente a + verso b) por arquivo; respostas em cada item, nunca desenhadas |
| **G1 completo** | `folhas/geometria-plana-epcar/G1/1..100.yaml` | 4–100 (exceto 81, 85, 89) convertidos dos esqueletos de `docs/prompts/esqueletos-G1.zip`; 100/100 passam no `validar`; **falta a revisão do Ângelo** (seção 6.2) |
| Conversor de esqueletos | `ferramentas/esqueletos.py` | Formato do prompt `docs/prompts/esqueletos-g1.md` → YAML; para em frase de figura desconhecida |
| Medidas das figuras | `motor/medidas.py`, `motor/figuras.py` | Ângulos em minutos (aceita 35°30'), incógnitas x e y; retas que se cruzam, transversal entre paralelas, rótulos que desviam de linhas e rótulos da página inteira |
| Leitura e validação | `motor/especificacao.py` | Falha alto com arquivo, lado, bloco e item do erro |
| Renderizador | `motor/render.py` | Tabela de tipos de bloco; layout por caixas; recolhe o gabarito |
| Motor de folhas (texto) | `motor/folha.py` | Classe `Folha`: cabeçalho, ícones e os tipos de exercício de idioma |
| Motor de geometria | `motor/geo.py` | `FolhaGeo`: cabeçalho para celular, figuras medidas, quadro de exemplo, grade |
| Figuras de paralelas com "bicos" | `motor/bicos.py` | `Bico`: poligonal centralizada, ângulos **calculados**, rótulos afastados das linhas |
| Exemplos | `exemplos/pacotes.yaml` | 4 PDFs: 6A 1–5, AII 64 + DI 112, G1 1–3, G1 81/85/89 |
| Testes | `testes/test_folhas.py` | Gera tudo; nada fora da página; texto sobre texto ou sobre linha; gabarito de 81–89 |
| Gabarito | `motor/gabarito.py` | Lido do YAML; bicos conferidos (todos os rótulos dão o mesmo x, que bate com resposta e alternativa) |
| Áudio | `motor/audio.py` | Bloco de faixas para o leitor, gerado dos blocos com som |
| Estado do aluno | `motor/estado.py`, `estado/` | Adaptador JSON; o do francês é `estado/frances.local.json` (fora do git) |
| Autor automático | `motor/autor.py`, `./degrau automatico` | O Claude (API) escreve as folhas que faltam; passam pelas verificações do motor antes de gravar |
| Verificação do desenho | `motor/verificar.py` | Texto fora da página, sobre texto ou sobre linha (testes e autor automático) |
| Gerador de pacotes | `motor/gerador.py`, `./degrau` | Próximas folhas pelo estado; domínio, repetição com a versão seguinte (`N.v2.yaml`), pendente bloqueia |
| Ferramentas de autoria | `motor/ferramentas.py` | `degrau validar` (biblioteca inteira + o que falta), `degrau ver` (PDF e gabarito de uma folha), `degrau gabarito` (aba Gabarito da planilha) |
| Comparação | `ferramentas/comparar.sh` | Pixels e palavras, página a página, contra uma etiqueta ou commit |
| Leitor de áudio | `leitor/leitor-frances.html` | Funciona em qualquer navegador; HTML único |
| Correção automática | `correcao/aoEnviar.gs`, `correcao/montar.gs` | Gabarito por folha e versão; testada com envios simulados (`correcao/teste/simular.js`); **falta montar e testar no Google** (passo a passo em `correcao/README.md`, com `clasp` para editar pelo VS Code) |
| Currículos | `curriculos/*.yaml` | O motor lê só a chave `folha` (marca e tipo de campos); o resto ainda não |

### Fora do repositório (instância francês)

| Peça | Onde | Observação |
|---|---|---|
| Caderno de progresso | Página privada no Notion | **Aposentado em 01/10/2026**: o estado está em `estado/frances.local.json` (conteúdo conferido, nada se perdeu) |
| Leitor publicado | Artefato no claude.ai | Mesma página do `leitor/` |
| Lembretes | Google Agenda: pedir a folha às 06:30; prazo de entrega até 23:59 (avisos às 21:00 e 23:30) | Fuso America/Sao_Paulo |
| Memória do Claude (claude.ai) | Arquivo de memória com ponteiros e regras | O Claude Code não enxerga essa memória |

### Progresso do francês

- Nível 6A. Pacote 1 (folhas 6A 1–5) enviado em 30/09/2026, **aguardando entrega e correção**.
- 6A 4 e 6A 5 foram uma prévia (Expressions e Petite histoire). Decidido em 01/10/2026: daqui em diante vale o currículo
  (6A 6–30 continuam Mots familiers; nome da unidade = unidade + posição na faixa, ex.: "Mots familiers 6").
- Vocabulário introduzido: bonjour, merci, un avion, une ville, la France, un étudiant, content, fatigué, brésilien, dans, mais, arriver, je m'appelle, je suis, bienvenue, une hôtesse, en France.
- Estrutura vista em frases (sem explicação): je suis / il est.

### Onde fica o estado (decidido em 01/10/2026)

O estado do francês fica em `estado/frances.local.json`, fora do git (`.gitignore`: `estado/*.local.json`).
Formato documentado em `motor/estado.py`; exemplo fictício em `estado/exemplo.json`. O caderno no Notion
deixa de ser a fonte do estado. O CASD continua na planilha (outro adaptador, na fase 6).

---

## 2. Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt           # reportlab, pyyaml, pytest
./degrau exemplos exemplos/pacotes.yaml    # saída em exemplos/pdf/: PDF + .gabarito.csv
                                           # + .planilha.csv (CASD) + .audio.txt (se houver som)
./degrau estado estado/frances.local.json  # próxima folha, pendentes, últimas notas
./degrau proximo estado/frances.local.json # gera o próximo pacote em pacotes/ (fora do git)
./degrau registrar estado/frances.local.json "6A 1-5" --nota 95 --tempo 9   # domínio ou repetir
./degrau automatico estado/frances.local.json --pedido   # grava em saida/pedido.txt o que iria para a API
./degrau automatico estado/frances.local.json            # API escreve as folhas que faltam + gera o pacote
./degrau enviar estado/frances.local.json  # manda o último pacote por e-mail (Gmail; --pacote N, --pasta DIR)
ferramentas/agendar.sh                     # agenda o automatico às 06:30 (crontab); --remover desfaz
./degrau validar                           # confere todas as folhas e lista as que faltam (sai com 1 se houver erro)
./degrau ver G1 4-6                        # PDF dessas folhas em saida/ver/ + gabarito na numeração do formulário
./degrau gabarito geometria-plana-epcar    # aba Gabarito da planilha (biblioteca inteira) em saida/
cd correcao && clasp push                  # envia aoEnviar.gs e montar.gs ao projeto do CASD (depois do clasp login)
pytest                                     # nesta máquina: env -u PYTHONPATH pytest (o ROS injeta plugins)
ferramentas/comparar.sh [etiqueta]         # compara com a referência (padrão: referencia-fase0)
```

A etiqueta `referencia-fase0` guarda os PDFs gerados pelos scripts originais (fase 0).

Para conferir visualmente: `pdftoppm -png -r 80 arquivo.pdf previa` (poppler) e abrir as imagens.
**Sempre** renderizar e olhar as páginas depois de mudar layout: vários bugs da conversa só apareceram na imagem
(rótulos encostando em linhas, figuras saindo da margem, título sobrepondo campos).

---

## 3. O método — regras invioláveis

1. **Degraus mínimos.** Cada folha um pouco mais difícil que a anterior; nunca dois conceitos novos na mesma folha.
2. **Entrada abaixo do nível real.** O nivelamento coloca o aluno onde ele acerta quase tudo.
3. **Domínio = nota ≥ 90% E tempo ≤ tempo-padrão.** Sem domínio, o pacote seguinte repete o mesmo trecho com exercícios **novos** (não os mesmos).
4. **Diário.** Pacote não entregue não avança; o pendente vem primeiro no dia seguinte.
5. **Exemplo, não explicação.** Nenhuma folha explica a regra em texto teórico. A regra aparece num exemplo resolvido.
6. **Esqueleto visual fixo, conteúdo crescente.** Cabeçalho, ícones e forma da instrução não mudam; cresce a quantidade de texto e a exigência (palavra → frase → parágrafo → justificativa).
7. **Unidades de 10 folhas,** cada uma com um único tipo de tarefa; histórias e revisões intercaladas.
8. **Tempo-padrão por nível** (1–2 min por folha no início, até 3–5 min no B1).

Análise de referência que originou o método: tabela de folhas de inglês de uma rede tradicional (níveis 7A a L).
Fases: repetir e recitar → aprender a ler e escrever → visualizar um texto → tema de cada parágrafo → resumir →
ler criticamente. **Não** incluir esse PDF nem o nome da marca no repositório.

---

## 4. Especificação visual das folhas

### 4.1 Comum

- **Página:** A5 retrato (148 × 210 mm), margem `M = 10 mm`.
- **Fontes:** Andika regular e negrito (`motor/fonts/`), registradas como `And`, `AndB`; `Sans` é alias da Andika regular (usado só na linha da marca).
- **Cores:** tinta `#1d1d1f`; cinza `#8a8f98` (traduções, números de item, rodapé); cinza claro `#c9ccd2` (contorno do quadro de exemplo); contorno de cópia `#cfd3da`; linhas de resposta `#b8bcc4`; acento `#1f4e9c` (reservado).
- **Linha de instrução:** ícone circular (raio 4,2 mm) à esquerda; instrução em negrito 11–11,5 pt; tradução em cinza 7,5 pt abaixo (só níveis iniciais de idioma); pontuação "[10 chacun]" / "[10 cada]" à direita — se a instrução for longa, a pontuação desce para a linha de baixo.
- **Rodapé:** código da folha, 7 pt, cinza, canto inferior direito.
- **Quadro de exemplo:** retângulo arredondado cinza claro, título "Exemplo"/"Exemple" em negrito 9,5 pt.

### 4.2 Ícones (desenhados em vetor, `icon()` em `folha.py`)

| Chave | Desenho | Uso |
|---|---|---|
| `ouvir` | alto-falante | ouvir |
| `escrever` | lápis inclinado | escrever, completar, responder |
| `ligar` | dois pontos ligados | ligar |
| `circular` | oval | circular, verdadeiro ou falso |
| `ler` | livro aberto | ler |

### 4.3 Cabeçalho da instância francês (`Folha.page`)

- Linha minúscula no topo: "DEGRAU · français".
- Código em negrito 15 pt (ex.: **6A 1a**) + nome da unidade 9,5 pt (encolhe automaticamente até 6,5 pt se encostar nos campos).
- À direita: campos **Nom**, **Date**, **Début**, **Fin** (impressão em papel ou tablet).
- Linha horizontal a 12 mm do topo útil.

### 4.4 Cabeçalho da instância geometria (`FolhaGeo.page`)

- Linha minúscula: `FolhaGeo.MARCA` (no currículo: "DEGRAU · geometria · CASD"; uso do nome autorizado pela coordenação).
- Código + unidade.
- No lugar dos campos: "No caderno, anote: G1 81a · início · fim" (o aluno lê no celular e escreve no caderno).
- Sem linhas de resposta: tudo no caderno; respostas finais curtas (número, ângulo, letra, alternativa).

### 4.5 Progressão de formato (francês)

| Faixa de níveis | Formato |
|---|---|
| 6A–3A | Tradução em cinza nas instruções; palavras 19 pt; frases 14–16 pt; muito espaço em branco |
| AI–AII | Instruções só em francês; textos de ~60 palavras; respostas em frase completa; escrita de memória |
| BI–CII | Textos maiores; perguntas de quem/o quê/onde/quando/por quê/como |
| DI–FI | Letra 10,5–11 pt; parágrafos de 100+ palavras; pontuação por questão ([20], [30]); decomposição de frases complexas; formato do DELF |

---

## 5. Especificação das folhas (YAML) e motor

Cada folha: `folha`, `unidade`, `a`, `b`. Cada lado: `instrucao`, `icone`, `blocos` e, opcionais, `traducao`
(só folhas de papel), `pontos` ("[100]") ou `pontos_cada` ("[10 chacun]"/"[10 cada]"). Cada bloco é um mapa
com uma chave, o tipo. Exemplos completos em `folhas/`. O campo `resposta` alimenta o gabarito e nunca é desenhado.

| Bloco | Conteúdo | Método do motor |
|---|---|---|
| `palavras` | `itens: [[fr, pt], …]`, `colunas` | `palavras` |
| `ligar` | `itens` ou `itens_de: a`, `semente` | `ligar` |
| `circular` | `itens: [{opcoes, resposta}]` | `circular` |
| `copiar` | `[str]` | `copiar` |
| `frases` | `itens: [str]` ou `[[fr, pt]]` | `frases` |
| `banco` | `[str]` | `banco` |
| `lacunas` | `itens: [{texto: "Je ___ Rafael.", resposta}]` | `lacunas` |
| `leitura` | `linhas`, `vezes` | `leitura` |
| `verdadeiro-falso` | `itens: [{texto, resposta: V/F}]` | `verdadeiro_falso` |
| `ditado` | `itens: [{resposta}]`, subinstrução opcional | `ditado` |
| `texto` | `paragrafos`, `quadro` | `texto` |
| `exemplo` | `frase` + `decomposicao` (idiomas) ou `texto` + `figura` (geometria) | `exemplo_frase` / `exemplo_figura` |
| `perguntas` | `itens: [{pergunta, linhas, pontos, resposta}]` | `perguntas` |
| `ordenar` | `itens: [{texto, resposta: posição}]` | `ordenar` |
| `decompor` | `itens: [{frase, partes, resposta}]` | `decompor` |
| `subinstrucao` | `instrucao`, `icone`, pontos | `subinstrucao` |
| `grade` | `itens` numerados (figura e/ou `texto`, `resposta`), `colunas` | `grade` |
| `figura` | uma figura sem número | `figura` |
| `alternativas` | `itens`, `resposta: A/B/C/D` | `alternativas` |

`tamanho` (pt) é opcional em quase todos. Figuras (medidas em mm; direções em graus, podem ter fração):
`angulo: {direcoes: [d1, d2], nomes: [V, P, Q], marca: arco|reto, rotulo}`,
`semirretas: {direcoes, nomes, vertice, marcas: [[P, Q, arco|reto|~, rótulo], …], tracejadas: [M, …]}`,
`cruzadas: {direcoes: [d1, d2], ponto: O, marcas: [[de, até, rótulo], …]}` (retas que se cruzam),
`transversal: {direcao, marcas: [[r|s, acima-direita|acima-esquerda|abaixo-esquerda|abaixo-direita, rótulo], …]}`,
`bico: {altura, segmentos: [[direção, comprimento], …], marcas: [[vértice, dir|esq|~, rótulo|~|x], …]}`.

Rótulos: com `°` ou `'` é medida (conferida com o desenho); com `x`/`y` é expressão (todas as do mesmo x têm
que fechar); sem nada disso (`3`, `a`) é só nome. Item da grade pode ter `alternativas` (questão de prova,
resposta = letra), `incognita: y` (quando a pergunta é y) e `pontos`. Sem `incognita`, a resposta só é conferida
com x quando o item é só a figura. Figuras são medidas desenhando num canvas que não desenha (`Medidor`), então
o espaço reservado inclui os rótulos.

**Layout por caixas:** a página empilha os blocos. Os fixos são medidos num canvas descartável; os elásticos
(palavras, ligar, circular, copiar, frases, lacunas, verdadeiro-falso, grade) dividem a sobra até `LIMITE`,
com passo máximo e mínimo por tipo. Se não couber, erro em vez de sobreposição.

**Bico** (`desenhar_bico` em `bicos.py`):

- O **último** segmento é estendido até encostar na reta `s`.
- Nas pontas (índice 0 e último), `lado` é `dir` ou `esq` (de que lado da paralela o ângulo é medido). Rótulo `~` → escreve o valor calculado; string → escreve a string (`x`, `3x + 5°`).
- Devolve `{índice: valor em graus}` calculado da geometria. Item sem `resposta` usa o vértice marcado com `x`.
- A poligonal é **centralizada**; se ficar mais larga que o espaço, erro (prefira direções íngremes).
- Cada rótulo se afasta pela bissetriz até não encostar em linha nem em outro rótulo.
- Regra matemática usada nas folhas: entre paralelas, a soma dos ângulos que **abrem** para a esquerda é igual à soma dos que abrem para a direita.

### Débitos do motor

- Parâmetros internos ainda em francês (`size`, `gloss`, `titre`…); os nomes de métodos e ícones já estão em português.
- Tamanhos de letra escritos por folha (`tamanho`); deveriam vir de um estilo por faixa de níveis (seção 4.5).
- O texto do exemplo de geometria ("x = 30° + 40° = 70°") é escrito à mão e não é conferido com a figura.
- O tempo-padrão do bloco usa o máximo da faixa do nível (`tempo_padrao_min`).

---

## 6. As duas instâncias

### 6.1 Francês (uso pessoal)

**Meta:** DELF B1 numa sessão do 2º semestre de 2027 (com margem para uma 2ª tentativa antes de abril de 2028). A prova tem 4 competências de 25 pontos; aprovação com 50/100 e mínimo 5 em cada. O maior risco é a produção oral.

**Fluxo diário (a partir da fase 4, no Claude Code):**

Com o agendamento ligado (seção 7.6), os passos 2 a 4 rodam sozinhos às 06:30 e o pacote fica em `pacotes/`.

1. 06:30 — lembrete. Ângelo pede a folha.
2. Claude roda `./degrau estado estado/frances.local.json`: se houver pacote pendente, ele vem primeiro.
3. Claude escreve em YAML as folhas que faltam (o `proximo` lista os arquivos; numa repetição, a versão nova
   `N.v2.yaml` com exercícios novos), usando vocabulário, estruturas e erros recorrentes do estado.
4. `./degrau proximo …` gera PDF `Pacote_NNN_nível_folhas.pdf`, gabarito e **um bloco único de texto** com as
   faixas de áudio, e marca o pacote como pendente.
5. Ângelo cola o bloco no leitor, faz as folhas anotando início e fim.
6. Entrega até 23:59: fotos das páginas (preferível) ou respostas digitadas por folha ("3a: 1 merci, …").
7. Claude corrige com o `.gabarito.csv`, dá nota por folha e do pacote, roda `./degrau registrar …` (domínio
   ou repetir) e atualiza vocabulário, estruturas e erros recorrentes no estado.

**Pacote:** 5 folhas por dia (10 páginas A5).

**Currículo:** `curriculos/frances-delf-b1.yaml` — 13 níveis (6A, 5A, 4A, 3A, AI, AII, BI, BII, CI, CII, DI, EI, FI), ~1.750 folhas, ~350 dias.

**História:** *Un Brésilien à Toulouse* — Rafael, estudante brasileiro de engenharia aeronáutica em Toulouse; Camille (de Lyon); a comissária de bordo; o professor. Arco: chegada → campus → projetos e viagens → estágio em empresa aeroespacial → textos densos sobre Toulouse e carreira. Fornece as frases das unidades de estruturas e as folhas "Histoire".

**Convenção do bloco de áudio:**

```
Feuille un a. Bonjour. Merci. Un avion. …
Feuille cinq a. Bonjour ! Je m'appelle Rafael. …
[L'hôtesse] Bienvenue à Toulouse !
[Rafael] Merci !
Feuille cinq b. Je suis dans un avion. …
```

- Linha falada "Feuille N x." abre cada folha.
- Falas de personagens: `[Nome]` no início da linha. Sem marca = narrador.
- Nas folhas em que o áudio contém a resposta (circular, ditado), avisar para esconder o texto.

**Leitor (`leitor/leitor-frances.html`):** colar texto → "Preparar texto" (divide em frases; linhas com `[Nome]` viram falas) → escolher voz do narrador e velocidade (padrão 0,85×) → "Ouvir tudo", "Pausar/Continuar", "Parar", "Esconder texto". Tocar numa frase repete só ela. Seção "Vozes da conversa": voz por personagem (padrão: vozes francesas diferentes do narrador + altura de voz distinta por personagem; se só houver uma voz no aparelho, diferencia pela altura). Guarda voz, velocidade, último texto e vozes por personagem no `localStorage` (com `try/catch`). Usa a API de síntese de voz do navegador; qualidade depende do aparelho.

### 6.2 CASD (geometria plana, turma EPCAR)

**Problema:** turma heterogênea (alunos de ~14 anos, níveis muito diferentes). Hoje contornado com duas listas por aula. Solução: aula coletiva + treino individual por nível.

**Restrições:** o CASD não imprime; PDF no celular; resolução no caderno; entrega por formulário; duas aulas por semana; ~10 minutos de treino por dia.

**Rotina:**

- Bloco diário = 3 folhas (3–4 min cada). Código do bloco: `G1 10-12`.
- Pacote = blocos entre uma aula e a seguinte.
- Na aula: professor olha o painel (quem sobe, quem repete). Depois da aula: PDF do próximo pacote por WhatsApp, individual, no nível de cada aluno. Em casa: bloco diário + envio pelo formulário. Prazo: véspera da aula.
- Nivelamento: prova de 10 questões (uma por unidade) define a entrada, um pouco abaixo do nível real.
- Casdindin (moeda fictícia do cursinho) premia constância e subida de nível.

**Currículo:** `curriculos/geometria-plana-epcar.yaml` — G1 Ângulos detalhado em 10 unidades; G2–G8 só esqueleto.

**Correção:** `correcao/` — formulário único, planilha (Alunos, Gabarito, Painel), Apps Script `aoEnviar` disparado ao enviar o formulário. Status "Domínio" se nota ≥ 90 e tempo ≤ limite; senão "Repetir". Constante `TEMPO_CONTA = false` nas duas primeiras semanas do piloto.

**Formulário:** uma seção por página do bloco, 12 campos cada, numerados como os itens da folha. O gabarito da planilha sai do YAML (`.planilha.csv`). Ver `correcao/README.md`.

**Decisões de 02/10/2026 para o piloto:**

- **Uma versão de cada folha.** Na repetição, o gerador lista a versão 2 que falta e o Ângelo escreve na hora;
  a geração automática de versões novas (variação das folhas de cálculo) fica para uma etapa posterior.
- **Gabarito indexado por folha e versão**, carregado uma vez só na aba Gabarito para a biblioteca inteira
  (resolve entradas em qualquer folha e repetições com versões diferentes). Código do bloco com a versão quando
  for repetição (`G1 10-12 v2`).
- **Código do bloco impresso na folha**, para o aluno copiar no formulário (cabeçalho: "Bloco G1 1-3 · no caderno, anote:").
- **Conteúdo do G1:** esqueletos das 94 folhas feitos noutra conversa do Claude (`docs/prompts/esqueletos-g1.md`,
  resultado em `docs/prompts/esqueletos-G1.zip`) e convertidos em 02/10/2026. Revisão de professor pendente:
  G1 42 (definição de adjacentes × consecutivos); G1 66 (siglas CO, AI, AE… como resposta); G1 88 (ponte para a 89);
  91–100 (questões inéditas "no estilo" EPCAR/Colégio Naval; trocar algumas por questões reais adaptadas);
  distratores das alternativas; enunciados que repetem a figura ("Figura 1: quanto mede AÔC?").
- **Nivelamento:** esqueleto em `NIVELAMENTO_G1.md` do zip (10 questões, regra de entrada); ainda não convertido
  (o código "G1 NIV" não passa no formulário: definir como entra no sistema).
- **Entrega por e-mail automático.** O sistema é entregue ao CASD; os e-mails dos alunos ficam com a
  administração do curso (na planilha da conta institucional), nunca no repositório.

**Piloto:** 6–8 voluntários (fortes e com dificuldade), 4 semanas, só G1. Critérios definidos antes: ≥70% ainda entregando na semana 4; nota média nas folhas subindo; desempenho no simulado melhor que o de não participantes com nível parecido. Semana 0: revisar tabela, montar planilha/formulário/script, testar com envios falsos, falar com a coordenação, convidar voluntários.

**Privacidade:** alunos são menores de idade. Formulário e planilha na conta institucional do CASD; coleta de fotos de cadernos autorizada pela coordenação (01/10/2026); envio de arquivo no Forms exige conta Google (alternativa: fotos por WhatsApp). **Nunca** versionar dados de alunos (`.gitignore` já bloqueia).

---

## 7. Arquitetura-alvo (o que construir)

### 7.1 Princípio

O núcleo não sabe nada de francês nem de geometria. Ele conhece: **curso → níveis → unidades → folhas → itens**,
sabe desenhar tipos de exercício, montar pacotes, gerar faixas de áudio, exportar gabaritos, corrigir respostas curtas
e decidir domínio. Cada instância é só **dados + configuração + adaptadores**.

### 7.2 Modelo de dados

- **Curso:** id, idioma do conteúdo, idioma de apoio, cabeçalho (marca, tipo de campos), tamanho do pacote, regra de domínio.
- **Nível:** código, nome, metas, número de folhas, tempo-padrão por folha, conteúdos/vocabulário novos.
- **Unidade:** intervalo de folhas, tipo de tarefa.
- **Folha:** código (nível + número), frente e verso, cada lado com: tipo de exercício, instrução, tradução opcional, ícone, pontos, itens, gabarito por item, faixa de áudio opcional.
- **Pacote:** lista de folhas, data, prazo.
- **Aluno:** nível atual, próximo pacote, histórico, sequência de dias.
- **Entrega:** pacote, respostas, fotos, início, fim.
- **Correção:** nota por folha e por pacote, tempo, status, itens errados, erros recorrentes.

### 7.3 Adaptadores (plugáveis por instância)

| Função | Francês hoje | CASD | Opções futuras |
|---|---|---|---|
| Estado do aluno | JSON local (`estado/`) | Planilha (aba Alunos/Painel) | Banco |
| Entrega do pacote | Chat no claude.ai | WhatsApp individual | E-mail, Telegram, página |
| Recebimento | Fotos/texto no chat | Google Forms | Aplicativo |
| Correção | Claude | Apps Script + gabarito | Correção local em Python a partir das respostas exportadas |
| Lembretes | Google Agenda | (a definir) | Agendador automático |
| Áudio | Leitor no navegador | — | Texto para fala gerado no servidor (arquivos de áudio) |

### 7.4 Especificação de folha em YAML

Implementada na fase 1 (seção 5; exemplos em `folhas/`). O áudio não precisa de campo próprio: sai dos blocos
`palavras`, `frases`, `circular` (lê a resposta), `leitura` ("Nome : « fala »" vira `[Nome] fala`) e `ditado`.

Para itens com expressões (ex.: `3x + 5°`), o motor verifica (fase 2, `resolver_x` em `bicos.py`) que **todas** as expressões dão o valor calculado com o mesmo x e falha alto se não derem (foi assim que se pegou um rótulo errado na conversa: "100°" num ângulo de 80°).

### 7.5 Linha de comando

Implementada na fase 4 (`./degrau`, seção 2). A correção automática do francês a partir de respostas digitadas
(`degrau corrigir --respostas`) ainda não existe: hoje a nota vem da correção feita pelo Claude.

### 7.6 Automação (fase 5)

Feitos em 01/10/2026 a **geração** e o **envio por e-mail** (Gmail, escolha do Ângelo).

- `./degrau automatico <estado>`: se houver pacote pendente, não faz nada. Senão planeja o próximo pacote,
  pede ao Claude (`claude-opus-5-5`, esforço `high`, saída em JSON com esquema) o YAML das folhas que faltam,
  passa cada folha pelas verificações do motor (estrutura, desenho, gabarito) e devolve os erros ao modelo
  até 3 vezes. Grava as folhas em `folhas/`, o vocabulário novo no estado, e gera o pacote em `pacotes/`.
- Pedido: parte fixa em cache (regras do método, seção 5, currículo, folhas de `exemplos/pacotes.yaml`) +
  parte do dia (vocabulário, estruturas, erros, últimos resultados, as 5 folhas anteriores; numa repetição,
  a versão anterior com a ordem de não repetir itens). Para revisar sem gastar: `--pedido`.
- Chave da API em `.env.local` (fora do git): `ANTHROPIC_API_KEY=...`. Fallback de recusa ligado (`fallbacks: "default"`).
- Custo estimado: ~7 mil tokens de entrada fixos + ~2 mil do dia; saída ~10–15 mil (folhas + raciocínio).
  Com os preços do Opus 5.5 (US$ 4 / 20 por milhão), ~US$ 0,30–0,40 por pacote, ~US$ 10–12 por mês.
  O cache dura 5 minutos: só barateia as novas tentativas do mesmo dia. O custo real sai no registro.
- Envio (`motor/envio.py`): Gmail por SMTP com **senha de app**. Em `.env.local`: `DEGRAU_EMAIL_DE`,
  `DEGRAU_EMAIL_SENHA`, `DEGRAU_EMAIL_PARA` (opcional). Vai o PDF e o bloco de áudio (no corpo, pronto para copiar,
  e em anexo) com o aviso de onde esconder o texto; **o gabarito nunca vai**. O `automatico` envia no fim se o
  e-mail estiver configurado; `./degrau enviar` manda um pacote à mão.
- Agendamento: `ferramentas/agendar.sh` põe no crontab `30 6 * * *` (fuso da máquina: America/Sao_Paulo);
  registro em `saida/automatico.log`.
- As folhas escritas pela API ficam em `folhas/` sem commit: revisar e versionar como as outras.

### 7.7 Expansão para outras áreas (fase 7, a planejar)

Pedido do Ângelo em 01/10/2026. Cada área nova é uma instância: currículo + tipos de bloco ou figura que faltarem
+ testes. A regra de ouro continua: tudo que é calculado (balanceamento, massas, correntes) sai do mesmo cálculo
que gera a folha, e o motor falha alto se não fechar.

| Área | Folhas típicas | O que falta no núcleo |
|---|---|---|
| Alemão | Igual ao francês (palavras, frases, leitura, ditado) | Currículo até o B1 (Goethe), textos fixos em alemão ("je", "Beispiel"), números por extenso no áudio, voz alemã no leitor. A Andika já tem ä, ö, ü, ß |
| Mandarim | Caracteres, pinyin com tons, ordem dos traços, tons no áudio | Fonte com caracteres chineses (a Andika não tem; ex.: Noto Sans SC, licença OFL), quadriculado para escrever, voz chinesa no leitor, currículo por HSK |
| Química: nomenclatura orgânica e inorgânica | Nome ↔ fórmula; nomear a cadeia | Fórmulas com índices (H₂SO₄); cadeia carbônica desenhada a partir da especificação, como os bicos |
| Química: balanceamento | Achar os coeficientes | Gabarito calculado (sistema linear) e conferência da contagem de átomos |
| Química: estequiometria | Massas, mols, rendimento | Gabarito calculado com tabela de massas atômicas e arredondamento padronizado |
| Física: circuitos simples | Resistência equivalente, corrente, tensão | Figura do circuito gerada da especificação (série e paralelo); gabarito pela lei de Ohm |

Perguntas a responder antes de construir:

1. Qual área entra primeiro (piloto da expansão)?
2. Quem valida o currículo de cada área (o ativo é a tabela de níveis, não o gerador)?
3. Para quem: uso pessoal, turma do CASD ou outros professores?

### 7.8 Métricas de desempenho (fase 8, a planejar)

Pedido do Ângelo em 01/10/2026. Ainda não desenhado em detalhe: depende dos dados de correção (fases 3 e 4).

| Métrica | Ideia inicial |
|---|---|
| Acertos | Nota de cada folha e de cada pacote (já sai da correção) |
| Constância | Dias entregues ÷ dias previstos; sequência atual e recorde; entregas fora do prazo |
| Posição em relação ao objetivo | O usuário escolhe um objetivo **só entre os cadastrados** num registro de objetivos (ex.: DELF A1/A2/B1, TOEFL, série escolar, prova da EPCAR). Cada objetivo aponta para um ponto do currículo (ex.: DELF B1 = fim do FI); posição = folhas dominadas ÷ folhas até esse ponto |
| Marcos por idade | Onde se espera que um aluno de certa idade esteja (ex.: série escolar ↔ nível), a partir de uma tabela de referência por curso |
| Tendência mensal | Por mês: nota média, tempo médio, folhas dominadas, repetições |
| Progresso de nível | Fração do nível atual concluída; níveis concluídos por mês |
| Projeção | Data estimada para chegar ao objetivo = folhas restantes ÷ ritmo recente (ex.: últimos 30 dias), com faixa otimista e pessimista; comparada com a data da prova |
| Teste de fim de nível | Uma prova ao fim de cada nível, sem exemplo resolvido. Aprovado avança; reprovado recomeça o nível (ou parte dele) |

Perguntas a responder antes de construir:

1. Onde as métricas aparecem: painel na planilha, página no navegador ou um resumo junto do pacote?
2. Marcos por idade: de onde vem a tabela de referência de cada curso?
3. Teste de fim de nível: número de questões, nota de corte, e se a reprovação recomeça o nível inteiro ou só as unidades com erro.
4. Quais objetivos entram primeiro no registro.
5. Dados de menores: idade e métricas do CASD só na conta institucional; no repositório, só a lógica e dados fictícios.

---

## 8. Roteiro de fases (com critérios de aceite)

| Fase | Entregas | Aceite |
|---|---|---|
| **0. Repositório de pé** (feita) | Revisar o que veio no zip; rodar os 4 exemplos; primeiro commit | 4 PDFs gerados sem erro; nada de dados pessoais versionados |
| **1. Conteúdo separado do desenho** (feita) | Esquema YAML de folha; renderizador que lê YAML; reescrever os 4 exemplos como YAML; layout por caixas em vez de milímetros fixos; testes básicos | Os PDFs gerados a partir do YAML ficam visualmente equivalentes aos atuais (comparar imagens) |
| **2. Gabarito e áudio a partir da mesma especificação** (feita) | Exportar gabarito (CSV para a planilha) e bloco de áudio direto do YAML; figuras com gabarito calculado e verificação das expressões | Gabarito de G1 1–3 e 81–89 batem com o `docs/plano-completo.md` |
| **3. Correção do CASD testada** (lógica testada; falta o teste no Google) | Conjuntos em qualquer ordem (G1 2b); testar o Apps Script com envios falsos; documentar a montagem passo a passo | Envio falso → linha correta no Painel |
| **4. Gerador de pacotes** (feita) | Linha de comando `degrau`; estado do aluno via adaptador; regra de domínio e repetição com exercícios novos | Gerar 5 dias seguidos de francês e 2 pacotes de geometria sem editar código |
| **5. Automação** (feita; falta ligar com as chaves) | Agendador + geração do conteúdo pela API + envio por e-mail | Pacote chega sozinho às 06:30 |
| **6. Multi-aluno CASD** | Gabarito por folha e versão; código do bloco na folha; `degrau validar` e `degrau ver`; um estado por aluno; importar o Painel; gerar e enviar por e-mail o pacote de cada aluno; nivelamento | Piloto de 6–8 alunos rodando |
| **7. Expansão para outras áreas** (a planejar) | Alemão, mandarim, química (nomenclatura, balanceamento, estequiometria), física (circuitos simples) etc. (seção 7.7) | Por área: currículo validado, um pacote de exemplo com gabarito calculado e testes |
| **8. Métricas de desempenho** (a planejar) | Acertos, constância, posição em relação ao objetivo, marcos por idade, tendência mensal, progresso de nível, projeção, teste de fim de nível (seção 7.8) | Definir com o Ângelo depois do piloto |

Fazer na ordem. Não pular para aplicativo: o produto só vale se o piloto mostrar retenção (≥70% entregando na semana 4).

---

## 9. Convenções

- **Código de folha:** nível + número + lado (`6A 1a`, `G1 81b`). Bloco do CASD: `G1 10-12`.
- **Arquivos:** francês `Pacote_NNN_nível_folhas.pdf`; geometria `G1_pacoteNN_folhasX-Y.pdf`.
- **Pontuação** escrita na folha, por exercício.
- **Figuras** sempre geradas por código a partir da construção; nunca imagem pronta.
- **Sem marca comercial** de método de ensino em nomes, textos, código ou arquivos.
- **Sem dados de alunos** no repositório.
- **Licenças:** código MIT; conteúdo CC BY-SA 4.0; fonte SIL OFL.
- **Antes de tornar público:** conferir `docs/plano-completo.md` (marca e links privados já retirados; ainda contém contexto pessoal do Ângelo e menções ao CASD) e decidir o que fica.

---

## 10. Decisões pendentes do Ângelo

1. ~~Revisão da tabela G1~~ — decidido em 01/10/2026: (a) graus, minutos e segundos fica como unidade inteira; (b) as questões de prova saíram da Revisão 1 (só a partir da folha 91); (c) "O bizu dos bicos" é o nome usado em sala.
2. ~~Coordenação do CASD~~ — autorizado em 01/10/2026: fotos de cadernos, dados de desempenho e uso do nome "CASD" (inclusive na marca da folha e no repositório público). Dados de alunos continuam fora do git.
3. ~~Onde fica o estado do francês~~ — decidido em 01/10/2026: JSON local (`estado/frances.local.json`).
4. ~~Modelo de gabarito do formulário~~ — decidido em 01/10/2026: mais campos, uma seção por página com 12 campos numerados como na folha (`correcao/README.md`).
5. ~~Envio automático~~ — decidido em 01/10/2026: e-mail pelo Gmail (senha de app).
6. Expansão para outras áreas (fase 7): as três perguntas da seção 7.7.
7. Métricas de desempenho (fase 8): as cinco perguntas da seção 7.8.

---

## 11. Como trabalhar com o Ângelo

- Direto, sem introduções; nível técnico alto.
- A solução mais simples que funciona; rejeita o que for super-engenhado.
- Edições mínimas e localizadas, não reescritas amplas.
- Em texto explicativo, termos por extenso; siglas só em código, fórmulas e gráficos.
- Vocabulário dele: **bizu** (a ideia forte, o atalho), **bizuleu** (o caminho a evitar), **safo** (quem domina o assunto).
- Documentos e comentários em português.
- Ao resolver matemática com ele: uma etapa de cada vez, tudo explícito.
- Ele faz passes para tirar frases com cara de texto de inteligência artificial: escrever natural.
