# Degrau — autor automático: o Claude escreve o YAML das folhas que faltam para o próximo pacote.
#
# Fluxo: o gerador planeja as folhas (gerador.planejar) -> monta-se um pedido com as regras do método,
# o formato YAML, o currículo e as folhas existentes como exemplo (parte fixa, em cache) + o estado do
# aluno e a lista do que escrever (parte variável) -> a resposta (JSON com o YAML de cada folha) passa
# pelas mesmas verificações do motor (estrutura, desenho, gabarito) -> se houver erro, os erros voltam
# para o Claude, até TENTATIVAS vezes -> grava as folhas na biblioteca e anota o vocabulário no estado.
import json, os
import yaml
from .especificacao import ErroEspecificacao, RAIZ, validar_folha, carregar_folha, caminho_folha, carregar_pacotes
from .gabarito import respostas_folha
from .verificar import verificar_folha

MODELO = 'claude-opus-5-5'
TENTATIVAS = 3
# US$ por milhão de tokens (Claude Opus 5.5): entrada, saída, escrita e leitura de cache
PRECO = {'entrada': 4.00, 'saida': 20.00, 'cache_escrita': 5.00, 'cache_leitura': 0.20}

ESQUEMA = {
    'type': 'object',
    'properties': {
        'folhas': {'type': 'array', 'items': {
            'type': 'object',
            'properties': {'codigo': {'type': 'string'}, 'versao': {'type': 'integer'}, 'yaml': {'type': 'string'}},
            'required': ['codigo', 'versao', 'yaml'], 'additionalProperties': False}},
        'vocabulario_novo': {'type': 'array', 'items': {'type': 'string'}},
        'estruturas_novas': {'type': 'array', 'items': {'type': 'string'}},
        'observacoes': {'type': 'string'},
    },
    'required': ['folhas', 'vocabulario_novo', 'estruturas_novas', 'observacoes'],
    'additionalProperties': False,
}


def _secao(texto, inicio, fim):
    i = texto.index(inicio); j = texto.index(fim, i + len(inicio))
    return texto[i:j].strip()


def pedido_fixo(curso):
    """Parte do pedido que não muda de um dia para o outro (vai em cache)."""
    claude_md = open(os.path.join(RAIZ, 'CLAUDE.md'), encoding='utf-8').read()
    regras = '\n\n'.join([
        _secao(claude_md, '## 3. O método', '\n---'),
        _secao(claude_md, '### 4.5 Progressão de formato', '\n---'),
        _secao(claude_md, '## 5. Especificação das folhas', '### Débitos do motor'),
    ])
    curriculo = open(os.path.join(RAIZ, 'curriculos', f'{curso["curso"]}.yaml'), encoding='utf-8').read()
    # exemplos fixos: as folhas de referência do curso em exemplos/pacotes.yaml (não a biblioteca inteira)
    codigos = [c for p in carregar_pacotes(os.path.join(RAIZ, 'exemplos', 'pacotes.yaml'))
               if p['curso'] == curso['curso'] for c in p['folhas']]
    exemplos = [_bloco_yaml(caminho_folha(curso['curso'], c)) for c in codigos]
    return f'''Você escreve as folhas de estudo diárias do sistema Degrau, curso "{curso['curso']}".
Cada folha é um arquivo YAML que o motor do Degrau lê e desenha num PDF A5 (frente "a" e verso "b").
O aluno fala português; o conteúdo das folhas fica no idioma do curso.

Escreva folhas do mesmo nível de qualidade e no mesmo formato dos exemplos. Respeite as regras do método
(degraus mínimos: nunca dois conceitos novos na mesma folha; exemplo, não explicação; esqueleto visual fixo),
reaproveite o vocabulário já visto e introduza pouco vocabulário novo por folha. Toda resposta de item
(campo resposta) precisa estar certa: ela vira o gabarito. Prefira frases curtas: o texto não pode passar
da margem da página (a verificação do motor recusa).

Para leitura com diálogo, escreva as falas como "Nome : « fala »" (o áudio vira "[Nome] fala").

# Regras do método e formato das folhas

{regras}

# Currículo do curso

```yaml
{curriculo.strip()}
```

# Folhas existentes (exemplos de formato e de nível)

{chr(10).join(exemplos)}

# Resposta

Responda só com o JSON pedido: em "folhas", um item por folha pedida (codigo e versao exatamente como
pedidos, yaml com o arquivo completo); em "vocabulario_novo" e "estruturas_novas", o que as folhas novas
introduzem; em "observacoes", uma ou duas frases para o professor (pode ser vazio).'''


def _bloco_yaml(caminho):
    return (f'### {os.path.relpath(caminho, RAIZ)}\n```yaml\n'
            + open(caminho, encoding='utf-8').read().strip() + '\n```')


def _ultima_versao(curso, codigo):
    v = 1
    while os.path.exists(caminho_folha(curso, codigo, v + 1)): v += 1
    return caminho_folha(curso, codigo, v)


def _unidade_do_curriculo(curso, codigo):
    nivel, num = codigo.split(); num = int(num)
    n = next((n for n in curso['niveis'] if n['codigo'] == nivel), {})
    for u in n.get('unidades', []):
        a, b = u['folhas']
        if a <= num <= b: return f'{u["nome"]} (folhas {a}-{b} do nível {nivel})'
    return f'nível {nivel}: {n.get("nome", "")} — {n.get("conteudo", "")}'


def pedido_do_dia(estado, plano):
    """Parte variável: estado do aluno e o que escrever."""
    curso = plano['curso']
    ultimas = [f'- {u["codigo"]} (v{max(u["versoes"])}): nota {u["nota"]}, {u["status"]}'
               for u in estado['unidades'][-6:] if u['status'] != 'pendente']
    pedidos = []
    for codigo, versao, _ in plano['faltam']:
        linha = f'- {codigo}, versão {versao}. Unidade no currículo: {_unidade_do_curriculo(curso, codigo)}.'
        if versao > 1:   # repetição: mesmos objetivos, itens novos
            anterior = open(caminho_folha(curso['curso'], codigo, versao - 1), encoding='utf-8').read()
            linha += (f'\n  É uma repetição: o aluno não dominou a versão {versao - 1}. Mesmo objetivo e mesmo nível, '
                      f'mas exercícios novos (não repita os itens). Versão anterior:\n```yaml\n{anterior.strip()}\n```')
        pedidos.append(linha)
    # continuidade: as 5 folhas anteriores ao pacote que já existem na biblioteca (última versão)
    from .gerador import sequencia
    primeira = plano['todas'][0]; anteriores = []
    for c in sequencia(curso, estado['inicio']):
        if c == primeira: break
        if os.path.exists(caminho_folha(curso['curso'], c)): anteriores.append(c)
    recentes = '\n\n'.join(_bloco_yaml(_ultima_versao(curso['curso'], c)) for c in anteriores[-5:])
    return f'''Aluno: {estado['aluno']}. Próximo pacote: {', '.join(f'{fs[0]} a {fs[-1]}' for fs in plano['unidades'])}.

Vocabulário já introduzido: {json.dumps(estado.get('vocabulario', {}), ensure_ascii=False)}
Estruturas já vistas: {json.dumps(estado.get('estruturas', {}), ensure_ascii=False)}
Erros recorrentes: {json.dumps(estado.get('erros_recorrentes', []), ensure_ascii=False)}
Últimos resultados:
{chr(10).join(ultimas) or '- nenhum'}

Folhas imediatamente anteriores (continue a partir delas, um degrau acima):
{recentes or '(nenhuma)'}

Escreva estas folhas:
{chr(10).join(pedidos)}'''


def validar_resposta(dados, plano):
    """Erros da resposta do Claude (lista vazia = tudo certo) e as folhas carregadas."""
    curso = plano['curso']
    pedidas = {(c, v): caminho for c, v, caminho in plano['faltam']}
    recebidas = {(f['codigo'], f['versao']): f['yaml'] for f in dados['folhas']}
    erros = [f'faltou a folha {c} versão {v}' for c, v in pedidas if (c, v) not in recebidas]
    erros += [f'folha não pedida: {c} versão {v}' for c, v in recebidas if (c, v) not in pedidas]
    folhas = {}
    for (c, v), texto in recebidas.items():
        if (c, v) not in pedidas: continue
        onde = f'{c} versão {v}'
        try:
            d = yaml.safe_load(texto)
            folha = validar_folha(d, onde, c)
            problemas = verificar_folha(folha, curso)   # desenha: valida blocos, layout e margens
            respostas_folha(folha)                      # gabarito: respostas e expressões conferidas
        except yaml.YAMLError as e:
            erros.append(f'{onde}: YAML inválido: {e}'); continue
        except (ErroEspecificacao, KeyError, TypeError, ValueError) as e:
            erros.append(f'{onde}: {e}'); continue
        erros += [f'{onde}: {p}' for p in problemas]
        if not problemas: folhas[(c, v)] = texto
    return erros, folhas


def _custo(usage):
    u = lambda k: getattr(usage, k, 0) or 0
    return (u('input_tokens') * PRECO['entrada'] + u('output_tokens') * PRECO['saida']
            + u('cache_creation_input_tokens') * PRECO['cache_escrita']
            + u('cache_read_input_tokens') * PRECO['cache_leitura']) / 1e6


def escrever_folhas(estado, plano, cliente=None, registro=print):
    """Pede ao Claude as folhas que faltam no plano, valida e grava na biblioteca.
    Devolve o custo estimado em US$."""
    if not plano['faltam']: return 0.0
    if cliente is None:
        import anthropic
        cliente = anthropic.Anthropic()
    curso = plano['curso']
    sistema = [{'type': 'text', 'text': pedido_fixo(curso), 'cache_control': {'type': 'ephemeral'}}]
    mensagens = [{'role': 'user', 'content': pedido_do_dia(estado, plano)}]
    custo = 0.0
    for tentativa in range(1, TENTATIVAS + 1):
        with cliente.beta.messages.stream(
            model=MODELO, max_tokens=64000, system=sistema, messages=mensagens,
            thinking={'type': 'adaptive'},
            output_config={'effort': 'high', 'format': {'type': 'json_schema', 'schema': ESQUEMA}},
            betas=['server-side-fallback-2026-07-01'], fallbacks='default',   # recusa -> modelo reserva
        ) as stream:
            resposta = stream.get_final_message()
        custo += _custo(resposta.usage)
        if resposta.stop_reason in ('refusal', 'max_tokens'):
            raise ErroEspecificacao(f'a API parou ({resposta.stop_reason}) na tentativa {tentativa}')
        dados = json.loads(next(b.text for b in resposta.content if b.type == 'text'))
        erros, folhas = validar_resposta(dados, plano)
        registro(f'tentativa {tentativa}: {len(folhas)}/{len(plano["faltam"])} folhas válidas, '
                 f'{len(erros)} erro(s), custo acumulado US$ {custo:.2f}')
        if not erros: break
        mensagens.append({'role': 'assistant', 'content': resposta.content})
        mensagens.append({'role': 'user', 'content': 'O motor do Degrau recusou a resposta:\n- ' + '\n- '.join(erros)
                          + '\nCorrija e devolva de novo todas as folhas pedidas.'})
    else:
        raise ErroEspecificacao(f'sem folhas válidas depois de {TENTATIVAS} tentativas:\n  ' + '\n  '.join(erros))

    for (c, v), texto in folhas.items():
        caminho = next(p for cc, vv, p in plano['faltam'] if (cc, vv) == (c, v))
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(texto.rstrip() + '\n')
        carregar_folha(curso['curso'], c, v)   # confere a leitura do arquivo gravado
    chave = ', '.join(f'{fs[0]}-{fs[-1].split()[1]}' if len(fs) > 1 else fs[0] for fs in plano['unidades'])
    if dados['vocabulario_novo']: estado.setdefault('vocabulario', {})[chave] = dados['vocabulario_novo']
    if dados['estruturas_novas']: estado.setdefault('estruturas', {})[chave] = dados['estruturas_novas']
    if dados['observacoes']: registro('observações: ' + dados['observacoes'])
    return custo
