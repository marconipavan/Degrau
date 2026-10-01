#!/bin/bash
# Compara os PDFs gerados a partir do YAML com os de referência (guardados numa etiqueta do git).
# uso: ferramentas/comparar.sh [etiqueta]        (padrão: referencia-fase0)
# Para cada página: pixels diferentes, palavras iguais ou não, e uma imagem
# "referência | novo | diferenças" em saida/comparacao/.
set -e
cd "$(dirname "$0")/.."
REF=${1:-referencia-fase0}; OUT=saida/comparacao
rm -rf saida/ref saida/novo $OUT; mkdir -p saida/ref $OUT
.venv/bin/python -m motor exemplos exemplos/pacotes.yaml saida/novo > /dev/null
for novo in saida/novo/*.pdf; do
  n=$(basename "$novo" .pdf)
  git show "$REF:exemplos/pdf/$n.pdf" > "saida/ref/$n.pdf"
  pdftoppm -png -r 100 "saida/ref/$n.pdf" "$OUT/ref_$n"; pdftoppm -png -r 100 "$novo" "$OUT/novo_$n"
  np=$(pdfinfo "$novo" | awk '/^Pages/{print $2}')
  [ "$np" = "$(pdfinfo "saida/ref/$n.pdf" | awk '/^Pages/{print $2}')" ] || echo "$n: NÚMERO DE PÁGINAS DIFERENTE"
  for ((p=1; p<=np; p++)); do
    a=$(ls $OUT/ref_$n-*.png | sed -n "${p}p"); b=${a/ref_/novo_}
    px=$(compare -metric AE "$a" "$b" null: 2>&1 || true)
    pal() { pdftotext -f $p -l $p "$1" - | tr -s '[:space:]' '\n' | sort; }
    if diff <(pal "saida/ref/$n.pdf") <(pal "$novo") > /dev/null; then txt=iguais; else txt=DIFERENTES; fi
    printf '%-28s pág %2d  pixels diferentes: %6s  palavras: %s\n' "$n" $p "$px" $txt
    convert "$a" "$b" \( "$a" "$b" -compose difference -composite -threshold 5% -fill red -opaque white \) +append "$OUT/$n-$p.png"
  done
  rm -f $OUT/ref_$n-*.png $OUT/novo_$n-*.png
done
