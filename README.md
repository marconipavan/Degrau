# Degrau

Folhas de estudo diárias, curtas e em degraus mínimos, com domínio exigido antes de avançar.

Cada aluno recebe, depois de cada aula, as folhas do seu próprio nível: um bloco de 3 folhas por dia, resolvido no
caderno. As respostas vão por um formulário do Google, corrigido automaticamente. Quem domina avança; quem não
domina refaz o trecho com exercícios novos. A aula continua coletiva; o treino passa a ser individual.

- **Uma tarefa por página**, frente e verso, formato A5 (lido no celular ou impresso).
- **Exemplo, não explicação:** a regra aparece num exemplo resolvido.
- **Domínio:** pelo menos 90% de acerto e tempo dentro do padrão do nível.
- **Figuras geradas por código**, com o gabarito saindo do mesmo cálculo que desenha a figura.

O método é inspirado em sistemas tradicionais de folhas diárias individualizadas. Este projeto é independente e não
tem relação com nenhuma marca.

## O que vem pronto

- **Geometria plana, nível G1 (ângulos):** 100 folhas, da noção de ângulo às questões de prova (preparação EPCAR e
  Colégio Naval).
- **Correção automática:** formulário e planilha do Google com um script que corrige cada envio e anota nota, tempo
  e domínio.
- **Rotina da turma:** a partir da planilha, prepara as folhas seguintes de cada aluno e envia por e-mail.

## Como usar

| Quem | Guia |
|---|---|
| Quem instala e opera no dia a dia | [docs/ADMINISTRACAO.md](docs/ADMINISTRACAO.md) |
| Professor (escrever e revisar folhas) | [docs/PROFESSOR.md](docs/PROFESSOR.md) |
| Aluno | [docs/ALUNO.md](docs/ALUNO.md) |
| Quem vai mexer no código | [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md) |

Resumo da instalação: Python 3.10 ou mais novo, Node.js e `npm install -g @google/clasp`; depois `python instalar.py`
e, para configurar, abrir o Degrau (`degrau.cmd` no Windows, `Degrau.command` no macOS, `./degrau` no Linux) e
escolher "Configurar".

## Estrutura

```
folhas/       folhas descritas em YAML, uma por arquivo
curriculos/   níveis e unidades de cada curso
motor/        leitura das folhas, desenho dos PDFs, gabarito, gerador de pacotes, rotina da turma
correcao/     Apps Script da correção automática (Google Forms + Planilha)
ferramentas/  conversor de esqueletos de folha, comparação de PDFs
testes/       testes (pytest) e simulador do Apps Script (correcao/teste)
docs/         guias por papel
```

## Licenças

Código: MIT. Conteúdo pedagógico (folhas e currículos): CC BY-SA 4.0. Fonte Andika: SIL Open Font License.
Detalhes em `LICENSE` e `LICENSE-CONTEUDO.md`.
