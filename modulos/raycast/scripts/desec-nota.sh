#!/usr/bin/env bash
set -euo pipefail
#
# desec-nota.sh
# Cria uma nova nota de relatório de pentest no Obsidian a partir do modelo em
# ../modelos/relatorio-pentest.md, com data/hora no nome, e abre a nota.
# Uso: ./desec-nota.sh

# Cofre do Obsidian onde a nota é criada — preencha com o caminho real na sua máquina.
VaultObsidian="$HOME/Documentos/ObsidianVault/Pentest"

# Caminho do modelo, relativo a este script.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
modelo="$script_dir/../modelos/relatorio-pentest.md"

if [ ! -f "$modelo" ]; then
  echo "Erro: modelo não encontrado em $modelo"
  exit 1
fi
if [ ! -d "$VaultObsidian" ]; then
  echo "Erro: cofre do Obsidian não encontrado em $VaultObsidian (ajuste VaultObsidian no script)."
  exit 1
fi

# Nome da nota com data/hora (evita sobrescrever relatórios anteriores).
timestamp="$(date +%Y%m%d-%H%M)"
nome_nota="relatorio-pentest-${timestamp}.md"
destino="$VaultObsidian/$nome_nota"

cp "$modelo" "$destino"

# Abre a nota no Obsidian via URI; se falhar, abre no editor padrão (xdg-open).
nome_sem_extensao="${nome_nota%.md}"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "obsidian://open?file=${nome_sem_extensao}" >/dev/null 2>&1 \
    || xdg-open "$destino" >/dev/null 2>&1 &
else
  echo "Aviso: xdg-open não encontrado. Abra manualmente: $destino"
fi

echo "Nota criada: $destino"
