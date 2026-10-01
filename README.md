# Degrau

Folhas de estudo diárias, curtas e em degraus mínimos, com domínio exigido antes de avançar.

- Cada folha tem frente e verso, formato A5, **uma única tarefa por página** e quase nenhum texto.
- A regra aparece num exemplo resolvido; não há explicação teórica na folha.
- Avança-se só com **domínio**: pelo menos 90% de acerto e tempo dentro do padrão do nível.
- O compromisso é diário: pacote de manhã, entrega até o fim do dia.

O método é inspirado em sistemas tradicionais de folhas diárias individualizadas. Este projeto é
independente e não tem relação com nenhuma marca.

## Exemplos

| Francês, nível inicial (6A) | Francês, nível B1 (DI) | Geometria (paralelas e "bicos") |
|---|---|---|
| `exemplos/pdf/Pacote_001_6A_1-5.pdf` | `exemplos/pdf/Amostra_niveis_AII_e_DI.pdf` | `exemplos/pdf/G1_amostra_folhas81-89.pdf` |

## Como gerar os exemplos

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python exemplos/frances_pacote001.py
python exemplos/geometria_G1_amostra_81-89.py
```

Os PDFs saem em `exemplos/pdf/`.

## Estrutura

```
motor/        motor de desenho das folhas (Python + reportlab) e fonte Andika
exemplos/     scripts que geram pacotes de exemplo
curriculos/   tabelas de níveis (YAML)
leitor/       leitor de áudio em HTML (texto para fala com vozes por personagem)
correcao/     correção automática com Google Forms + Planilha + Apps Script
docs/         plano completo do sistema
```

## Licenças

Código: MIT. Conteúdo pedagógico: CC BY-SA 4.0. Fonte Andika: SIL Open Font License.
Detalhes em `LICENSE` e `LICENSE-CONTEUDO.md`.
