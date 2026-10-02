#!/bin/sh
# Agenda o Degrau automático todo dia às 06:30 (hora local) no crontab do usuário.
# uso: ferramentas/agendar.sh [estado.json]      (padrão: estado/frances.local.json)
#      ferramentas/agendar.sh --remover
# Antes: coloque a chave em .env.local (ANTHROPIC_API_KEY=...). O registro vai para saida/automatico.log.
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
MARCA='# degrau-automatico'
if [ "$1" = "--remover" ]; then
  crontab -l 2>/dev/null | grep -v "$MARCA" | crontab -
  echo "agendamento removido"; exit 0
fi
ESTADO=${1:-estado/frances.local.json}
case "$ESTADO" in /*) ;; *) ESTADO="$RAIZ/$ESTADO" ;; esac
[ -f "$ESTADO" ] || { echo "estado não encontrado: $ESTADO"; exit 1; }
[ -f "$RAIZ/.env.local" ] || echo "aviso: $RAIZ/.env.local não existe; a chamada à API vai falhar sem a chave"
mkdir -p "$RAIZ/saida"
LINHA="30 6 * * * \"$RAIZ/degrau\" automatico \"$ESTADO\" >> \"$RAIZ/saida/automatico.log\" 2>&1 $MARCA"
( crontab -l 2>/dev/null | grep -v "$MARCA"; echo "$LINHA" ) | crontab -
echo "agendado: $LINHA"
