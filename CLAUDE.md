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
| Motor de folhas (texto) | `motor/folha.py` | Funciona. Classe `Folha` (alias `Feuille`) com cabeçalho, ícones e 14 tipos de exercício |
| Motor de geometria | `motor/geo.py` | Funciona. `FolhaGeo`: cabeçalho para celular, ângulos, semirretas, quadro de exemplo |
| Figuras de paralelas com "bicos" | `motor/bicos.py` | Funciona. `Bico`: poligonal entre paralelas, centralizada, com ângulos **calculados** |
| Pacote 1 de francês | `exemplos/frances_pacote001.py` | Gera `Pacote_001_6A_1-5.pdf` (10 páginas) |
| Amostra de francês avançado | `exemplos/frances_amostra_AII_DI.py` | Gera AII 64 e DI 112 |
| Pacote 1 de geometria | `exemplos/geometria_G1_pacote01.py` | Gera G1 1–3 |
| Amostra de geometria avançada | `exemplos/geometria_G1_amostra_81-89.py` | Gera G1 81, 85, 89 e imprime o gabarito calculado |
| Leitor de áudio | `leitor/leitor-frances.html` | Funciona em qualquer navegador; HTML único |
| Correção automática | `correcao/aoEnviar.gs` | **Esboço não testado** |
| Currículos | `curriculos/*.yaml` | Dados prontos, **ainda não lidos pelo motor** |

### Fora do repositório (instância francês)

| Peça | Onde | Observação |
|---|---|---|
| Caderno de progresso | Página privada no Notion | Estado atual, vocabulário, estruturas, erros recorrentes, registro de pacotes |
| Leitor publicado | Artefato no claude.ai | Mesma página do `leitor/` |
| Lembretes | Google Agenda: pedir a folha às 06:30; prazo de entrega até 23:59 (avisos às 21:00 e 23:30) | Fuso America/Sao_Paulo |
| Memória do Claude (claude.ai) | Arquivo de memória com ponteiros e regras | O Claude Code não enxerga essa memória |

### Progresso do francês

- Nível 6A. Pacote 1 (folhas 6A 1–5) enviado em 30/09/2026, **aguardando entrega e correção**.
- Vocabulário introduzido: bonjour, merci, un avion, une ville, la France, un étudiant, content, fatigué, brésilien, dans, mais, arriver, je m'appelle, je suis, bienvenue, une hôtesse, en France.
- Estrutura vista em frases (sem explicação): je suis / il est.

### Decisão em aberto: onde fica o estado

Hoje o estado do francês vive no Notion; o do CASD viverá numa planilha. Para o núcleo genérico, propor
um **adaptador de estado** (seção 7.3) e, para o francês, avaliar mover o estado para um JSON no repositório
(`estado/frances.json`, fora do controle de versão se tiver algo pessoal) ou configurar o Notion como servidor
de ferramentas no Claude Code. **Perguntar ao Ângelo antes de decidir.**

---

## 2. Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt           # só reportlab
python exemplos/frances_pacote001.py       # saída em exemplos/pdf/
python exemplos/geometria_G1_amostra_81-89.py   # imprime também o gabarito calculado
```

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
| `ecoute` | alto-falante | ouvir |
| `ecris` | lápis inclinado | escrever, completar, responder |
| `relie` | dois pontos ligados | ligar |
| `entoure` | oval | circular, verdadeiro ou falso |
| `lis` | livro aberto | ler |

### 4.3 Cabeçalho da instância francês (`Folha.page`)

- Linha minúscula no topo: "DEGRAU · français".
- Código em negrito 15 pt (ex.: **6A 1a**) + nome da unidade 9,5 pt (encolhe automaticamente até 6,5 pt se encostar nos campos).
- À direita: campos **Nom**, **Date**, **Début**, **Fin** (impressão em papel ou tablet).
- Linha horizontal a 12 mm do topo útil.

### 4.4 Cabeçalho da instância geometria (`FolhaGeo.page`)

- Linha minúscula: `FolhaGeo.MARCA` (padrão "DEGRAU · geometria"; o nome do cursinho só entra com autorização).
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

## 5. Tipos de exercício implementados (API atual)

`Folha` (em `folha.py`). Todos desenham a partir de `self.y` (cursor vertical) e o atualizam.

| Método | Parâmetros | O que desenha |
|---|---|---|
| `page(code, unite, instr, gloss, icone, points=None)` | — | Cabeçalho + instrução; define `self.y` |
| `fim(code)` | — | Rodapé + `showPage()` |
| `mots(itens, cols=2, size=19)` | `[(fr, pt), …]` | Palavras grandes com tradução cinza |
| `relie(pares, seed=1)` | `[(fr, pt), …]` | Duas colunas para ligar; direita embaralhada com semente fixa |
| `entoure(linhas)` | `[[op1, op2, op3], …]` | Linhas de opções para circular (o áudio diz qual) |
| `recopie(mots, size=20)` | `[str]` | Palavra em contorno claro + linha para copiar |
| `phrases(frases, size=15, gloss=None)` | `[str]`, `[str]` | Frases numeradas, tradução opcional |
| `banque(mots)` | `[str]` | Quadro de palavras |
| `trous(frases, size=14)` | `"Je ___ Rafael."` | Frases com caixa no lugar de `___` |
| `lecture(linhas, fois=3, size=14)` | `[str]` | Texto + quadradinhos para cada leitura em voz alta |
| `vraifaux(frases)` | `[str]` | Afirmações + "V F" |
| `dictee(n, num0=1, titre=None, gloss=None)` | — | Linhas de ditado (com subinstrução opcional) |
| `texte(paras, size=12, box=False)` | `[str]` | Parágrafos com quebra automática, quadro opcional |
| `exemple(titre, phrase, decomp)` | — | Quadro com frase e decomposição (a), (b)… |
| `questions(qs, size=11, lignes=2, num0=1)` | `[(pergunta, n_linhas)]` | Perguntas + linhas |
| `sousinstr(icone, txt, points=None)` | — | Segunda instrução na mesma página |
| `ordre(frases)` | `[str]` | Caixas para numerar a ordem |
| `decompose(num, phrase, parts)` | — | Frase + partes "(a) …" com linha até a margem |

`FolhaGeo` (em `geo.py`): `angulo(x, y, d1, d2, L, nomes=(V,P,Q), marca='arco'|'reto', rot)`, `raios(x, y, dirs, nomes, vert)`,
`num`, `texto`, `exemplo(h)`.

`Bico` (em `bicos.py`): `paralelas(yr, ys, x0, x1)` e `zig(xa, xb, yr, ys, segs, marks, r, size)`.

- `segs`: lista de `(direção em graus, comprimento)`; o **último** segmento é estendido até encostar na reta `s`.
- `marks`: lista de `(índice do vértice, lado, rótulo)`. Nas pontas (índice 0 e último), `lado` é `'dir'` ou `'esq'` (de que lado da paralela o ângulo é medido). Rótulo `None` → escreve o valor calculado; string → escreve a string (ex.: `'x'`, `'3x + 5°'`).
- **Retorna** `{índice: valor em graus}` calculado da geometria. O gabarito vem daqui.
- A poligonal é **centralizada** entre `xa` e `xb`. Direções rasas (menos de ~30° com a horizontal) fazem a figura sair do quadro; prefira direções íngremes.
- Regra matemática usada nas folhas: entre paralelas, a soma dos ângulos que **abrem** para a esquerda é igual à soma dos que abrem para a direita.

### Débitos do motor (corrigir na fase 1)

- Posições escritas à mão (milímetros mágicos) em cada exemplo; falta layout automático por "caixas".
- Nomes misturados em francês e português (`mots`, `relie`, `texte` × `angulo`, `raios`). Padronizar (sugestão: português no código, conteúdo no idioma do curso).
- `exemplo()` de `FolhaGeo` recebe altura fixa; deveria medir o conteúdo.
- Não há testes. Mínimo: gerar todos os exemplos sem erro + checar que nenhum texto sai da página (bounding boxes).
- Itens de verdadeiro ou falso, lacunas etc. não carregam gabarito: o gabarito está só no `docs/plano-completo.md`.

---

## 6. As duas instâncias

### 6.1 Francês (uso pessoal)

**Meta:** DELF B1 numa sessão do 2º semestre de 2027 (com margem para uma 2ª tentativa antes de abril de 2028). A prova tem 4 competências de 25 pontos; aprovação com 50/100 e mínimo 5 em cada. O maior risco é a produção oral.

**Fluxo diário atual (no claude.ai):**

1. 06:30 — lembrete. Ângelo manda "folha".
2. Claude lê o caderno de progresso, confere pendências, monta o pacote seguinte conforme a tabela e o domínio anterior.
3. Entrega: PDF `Pacote_NNN_nível_folhas.pdf` + **um bloco único de texto** com as faixas de áudio do dia.
4. Ângelo cola o bloco no leitor, faz as folhas anotando início e fim.
5. Entrega até 23:59: fotos das páginas (preferível) ou respostas digitadas por folha ("3a: 1 merci, …").
6. Claude corrige, dá nota por folha e do pacote, compara tempo, decide domínio/repetição e atualiza o caderno.

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

**Problema conhecido do modelo de gabarito:** um bloco de 3 folhas tem mais itens que os 15 campos do formulário. Decidir antes do piloto: gabarito só dos itens objetivos principais, mais campos, ou um envio por folha. Ver `correcao/README.md`.

**Piloto:** 6–8 voluntários (fortes e com dificuldade), 4 semanas, só G1. Critérios definidos antes: ≥70% ainda entregando na semana 4; nota média nas folhas subindo; desempenho no simulado melhor que o de não participantes com nível parecido. Semana 0: revisar tabela, montar planilha/formulário/script, testar com envios falsos, falar com a coordenação, convidar voluntários.

**Privacidade:** alunos são menores de idade. Formulário e planilha na conta institucional do CASD; autorização da coordenação para coletar fotos de cadernos; envio de arquivo no Forms exige conta Google (alternativa: fotos por WhatsApp). **Nunca** versionar dados de alunos (`.gitignore` já bloqueia).

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
| Estado do aluno | Notion | Planilha (aba Alunos/Painel) | JSON local, banco |
| Entrega do pacote | Chat no claude.ai | WhatsApp individual | E-mail, Telegram, página |
| Recebimento | Fotos/texto no chat | Google Forms | Aplicativo |
| Correção | Claude | Apps Script + gabarito | Correção local em Python a partir das respostas exportadas |
| Lembretes | Google Agenda | (a definir) | Agendador automático |
| Áudio | Leitor no navegador | — | Texto para fala gerado no servidor (arquivos de áudio) |

### 7.4 Especificação de folha em YAML (proposta)

Francês:

```yaml
curso: frances-delf-b1
folha: 6A 1
unidade: Mots familiers 1
a:
  tipo: mots
  icone: ecoute
  instrucao: Écoute et répète.
  traducao: Ouça e repita cada palavra em voz alta.
  itens:
    - [bonjour, "olá, bom dia"]
    - [merci, obrigado]
  faixa: "Feuille un a. Bonjour. Merci."
b:
  tipo: relie
  icone: relie
  instrucao: Relie.
  pontos: 10
  itens_de: a          # reaproveita os pares da frente
  semente: 3
```

Geometria (a figura é **especificação de construção**; o gabarito é calculado):

```yaml
curso: geometria-plana-epcar
folha: G1 81
unidade: O bizu dos bicos 1
a:
  tipo: figuras-bico
  instrucao: Veja o exemplo. Calcule x.  (r // s)
  pontos: 25
  exemplo:
    segmentos: [[-30, 22], [-140, 0]]
    marcas: [[0, dir, ~], [1, ~, x], [2, dir, ~]]
    texto: ["bico para a direita:", "x = 30° + 40° = 70°"]
  itens:
    - segmentos: [[-35, 18], [-140, 0]]
      marcas: [[0, dir, ~], [1, ~, x], [2, dir, ~]]
      resposta: calcular      # o motor preenche com o valor do vértice marcado com x
```

Para itens com expressões (ex.: `3x + 5°`), o motor deve verificar que **todas** as expressões dão o valor calculado com o mesmo x e falhar alto se não derem (foi assim que se pegou um rótulo errado na conversa: "100°" num ângulo de 80°).

### 7.5 Linha de comando (proposta)

```bash
degrau gerar --curso frances-delf-b1 --pacote 2          # PDF + bloco de áudio + gabarito
degrau gerar --curso geometria-plana-epcar --aluno joao --bloco "G1 10-12"
degrau gabarito --curso geometria-plana-epcar --nivel G1 --csv correcao/modelos/gabarito.csv
degrau corrigir --curso frances-delf-b1 --pacote 1 --respostas respostas.txt
```

### 7.6 Automação de verdade (opcional, fase 5)

No claude.ai o Claude não consegue iniciar a conversa; por isso o gatilho da manhã é do Ângelo. Para entrega
automática: agendador (cron local ou GitHub Actions às 09:30 UTC = 06:30 em Brasília, sem horário de verão) gera o
pacote a partir do estado + currículo e envia (e-mail ou Telegram). Se a geração do conteúdo novo usar a API da
Anthropic, a chave vai em segredo do repositório, nunca no código. Avaliar custo antes.

---

## 8. Roteiro de fases (com critérios de aceite)

| Fase | Entregas | Aceite |
|---|---|---|
| **0. Repositório de pé** | Revisar o que veio no zip; rodar os 4 exemplos; primeiro commit | 4 PDFs gerados sem erro; nada de dados pessoais versionados |
| **1. Conteúdo separado do desenho** | Esquema YAML de folha; renderizador que lê YAML; reescrever os 4 exemplos como YAML; layout por caixas em vez de milímetros fixos; testes básicos | Os PDFs gerados a partir do YAML ficam visualmente equivalentes aos atuais (comparar imagens) |
| **2. Gabarito e áudio a partir da mesma especificação** | Exportar gabarito (CSV para a planilha) e bloco de áudio direto do YAML; figuras com gabarito calculado e verificação das expressões | Gabarito de G1 1–3 e 81–89 batem com o `docs/plano-completo.md` |
| **3. Correção do CASD testada** | Resolver o limite de 15 campos; testar o Apps Script com envios falsos; documentar a montagem passo a passo | Envio falso → linha correta no Painel |
| **4. Gerador de pacotes** | Linha de comando `degrau`; estado do aluno via adaptador; regra de domínio e repetição com exercícios novos | Gerar 5 dias seguidos de francês e 2 pacotes de geometria sem editar código |
| **5. Automação** | Agendador + envio | Pacote chega sozinho às 06:30 |
| **6. Multi-aluno CASD** | Pacote individual por aluno a partir do painel | Piloto de 6–8 alunos rodando |

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

1. Revisão da tabela G1: (a) "Graus, minutos e segundos" merece uma unidade inteira na EPCAR? (b) as questões de prova entram cedo demais na Revisão 1? (c) "O bizu dos bicos" é o nome usado em sala? (marcados com `revisar: true` no YAML)
2. Coordenação do CASD: autorização para fotos de cadernos e dados de desempenho; uso do nome "CASD" no repositório público.
3. Onde fica o estado do francês (Notion × JSON local × outro).
4. Modelo de gabarito do formulário (limite de 15 campos).
5. Se haverá automação de envio (fase 5) e por qual canal.

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
