#!/usr/bin/env bash
set -euo pipefail
#
# desec-abrir.sh
# Abre a plataforma da Desec Security no navegador padrão (Linux/Ulauncher).
# Uso: ./desec-abrir.sh

UrlDesec="https://academy.desecsecurity.com/"

# xdg-open delega para o navegador padrão do ambiente gráfico.
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$UrlDesec" >/dev/null 2>&1 &
  echo "Abrindo $UrlDesec"
else
  echo "Erro: xdg-open não encontrado. Instale (ex.: apt install xdg-utils) ou abra manualmente: $UrlDesec"
  exit 1
fi
