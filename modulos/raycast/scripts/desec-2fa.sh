#!/usr/bin/env bash
set -euo pipefail
#
# desec-2fa.sh
# Gera o código TOTP (2FA) da Desec a partir da semente guardada no cofre do sistema
# (nunca gravada neste script). Mostra o código e copia para a área de transferência.
# Uso: ./desec-2fa.sh

# Nome do item no cofre (secret-tool). Cadastre na própria máquina com:
#   secret-tool store --label="Desec TOTP" service desec-totp username desec
SecretService="desec-totp"

# 1) Checa dependências essenciais.
if ! command -v secret-tool >/dev/null 2>&1; then
  echo "Erro: secret-tool não encontrado. Instale (ex.: apt install libsecret-tools)."
  exit 1
fi
if ! command -v oathtool >/dev/null 2>&1; then
  echo "Erro: oathtool não encontrado. Instale (ex.: apt install oathtool)."
  exit 1
fi

# 2) Busca a semente no cofre (GNOME Keyring / secret-tool).
seed="$(secret-tool lookup service "$SecretService" 2>/dev/null || true)"
if [ -z "$seed" ]; then
  echo "Erro: não achei a semente no cofre (service=$SecretService)."
  echo "Cadastre com: secret-tool store --label=\"Desec TOTP\" service $SecretService"
  exit 1
fi

# 3) Gera o código TOTP de 6 dígitos.
codigo="$(oathtool --totp -b "$seed")"
echo "Código 2FA Desec: $codigo"

# 4) Copia para a área de transferência (Wayland ou X11, com fallback).
if command -v wl-copy >/dev/null 2>&1; then
  printf '%s' "$codigo" | wl-copy
  echo "(copiado para a área de transferência)"
elif command -v xclip >/dev/null 2>&1; then
  printf '%s' "$codigo" | xclip -selection clipboard
  echo "(copiado para a área de transferência)"
else
  echo "Aviso: wl-copy/xclip não encontrados. Copie o código acima manualmente."
fi
