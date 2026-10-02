#!/usr/bin/env python3
"""Monta a cópia pública do Degrau (código aberto), sem a parte pessoal e com histórico novo.

    .venv/bin/python ferramentas/exportar_publico.py [pasta_destino]     (padrão: ../Degrau-publico)

Copia os arquivos versionados deste repositório, menos o que é pessoal (instância de francês, plano com contexto
pessoal, CLAUDE.md, estados), filtra os exemplos, cria um repositório git novo com um commit e procura termos que
não podem sair. Não publica nada: criar o repositório no GitHub e enviar é uma decisão à parte.
"""
import os, re, shutil, subprocess, sys
import yaml

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FORA = [  # prefixos (pastas terminam em /) ou nomes exatos
    'CLAUDE.md', 'docs/plano-completo.md', 'docs/prompts/esqueletos-G1.zip',
    'folhas/frances-delf-b1/', 'curriculos/frances-delf-b1.yaml', 'leitor/',
    'exemplos/pdf/Pacote_001_6A_1-5.', 'exemplos/pdf/Amostra_niveis_AII_e_DI.',
    'ferramentas/exportar_publico.py',
]
# o que não pode aparecer em nenhum arquivo de texto da cópia pública
PROIBIDO = re.compile(r'Supaero|Notion|Kumon|angelo\.marconi|Brésilien à Toulouse|frances\.local|'
                      r'claude\.ai/artifact|duplo diploma|média geral', re.I)


def fora(caminho):
    return any(caminho == f or (caminho.startswith(f)) for f in FORA)


def main():
    destino = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, '..', 'Degrau-publico'))
    if os.path.exists(destino):
        sys.exit(f'{destino} já existe: apague ou escolha outra pasta')
    arquivos = subprocess.run(['git', 'ls-files'], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.split('\n')
    copiados = 0
    for a in filter(None, arquivos):
        if fora(a) or not os.path.exists(os.path.join(RAIZ, a)): continue
        os.makedirs(os.path.dirname(os.path.join(destino, a)) or destino, exist_ok=True)
        shutil.copy2(os.path.join(RAIZ, a), os.path.join(destino, a)); copiados += 1

    # exemplos: só os cursos que vão junto
    caminho = os.path.join(destino, 'exemplos', 'pacotes.yaml')
    pacotes = [p for p in yaml.safe_load(open(caminho, encoding='utf-8'))
               if os.path.exists(os.path.join(destino, 'curriculos', p['curso'] + '.yaml'))]
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write('# Pacotes de exemplo. Gerar com: degrau exemplos exemplos/pacotes.yaml  (saída em exemplos/pdf/)\n')
        yaml.safe_dump(pacotes, f, allow_unicode=True, sort_keys=False)

    achados = []
    for pasta, _, nomes in os.walk(destino):
        for n in nomes:
            p = os.path.join(pasta, n)
            try: texto = open(p, encoding='utf-8').read()
            except (UnicodeDecodeError, OSError): continue
            for m in PROIBIDO.finditer(texto):
                achados.append(f'{os.path.relpath(p, destino)}: {m.group(0)!r}')
    if achados:
        print('ATENÇÃO, termos que não deveriam sair:\n  ' + '\n  '.join(achados))
        sys.exit(1)

    subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=destino, check=True)
    subprocess.run(['git', 'add', '-A'], cwd=destino, check=True)
    subprocess.run(['git', 'commit', '-q', '-m', 'Degrau: primeira versão pública'], cwd=destino, check=True)
    print(f'{copiados} arquivos em {destino} (repositório novo, um commit). Nada foi publicado.')


if __name__ == '__main__':
    main()
