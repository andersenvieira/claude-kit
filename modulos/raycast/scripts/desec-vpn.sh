#!/usr/bin/env bash
set -euo pipefail
#
# desec-vpn.sh
# Liga a VPN da Desec. Modo wsl (padrão, roda openvpn local no Linux) ou kali (via SSH).
# Mostra o comando antes de rodar (usa sudo) e pede confirmação.
# Uso: ./desec-vpn.sh [--modo wsl|kali] [--instalar]

# Variáveis específicas da máquina — preencha com os valores reais na sua máquina.
HostKali="kali"                 # host/alias SSH da VM Kali (ex.: em ~/.ssh/config)
OvpnPath="$HOME/desec/desec.ovpn"  # caminho do .ovpn local (nunca gravado no kit)

Modo="wsl"
Instalar=0

# Parser simples de argumentos.
while [ $# -gt 0 ]; do
  case "$1" in
    --modo)
      Modo="$2"
      shift 2
      ;;
    --instalar)
      Instalar=1
      shift
      ;;
    *)
      echo "Argumento desconhecido: $1"
      exit 1
      ;;
  esac
done

if [ "$Modo" != "wsl" ] && [ "$Modo" != "kali" ]; then
  echo "Erro: --modo deve ser 'wsl' ou 'kali'."
  exit 1
fi

# Monta o comando conforme o modo. No modo wsl aqui roda-se o openvpn direto (já em Linux).
if [ "$Modo" = "wsl" ]; then
  comando="sudo openvpn --config $OvpnPath --daemon"
else
  comando="ssh $HostKali 'sudo systemctl start openvpn@desec'"
fi

# Se pedido, instala o pacote openvpn no alvo antes de ligar a VPN (nunca sem a flag).
if [ "$Instalar" -eq 1 ]; then
  if [ "$Modo" = "wsl" ]; then
    comando_instalar="sudo apt-get install -y openvpn"
    comando_checar="test -f \"$OvpnPath\" && echo OK || echo FALTA"
  else
    comando_instalar="ssh $HostKali 'sudo apt-get install -y openvpn'"
    comando_checar="ssh $HostKali 'test -f ~/desec/desec.ovpn && echo OK || echo FALTA'"
  fi
  echo "Vou rodar (instalação): $comando_instalar"
  read -r -p "Confirmar? (s/n) " ok
  if [ "$ok" = "s" ]; then
    eval "$comando_instalar"
    echo "Checando .ovpn em ~/desec/ ..."
    eval "$comando_checar"
  else
    echo "Instalação cancelada pelo usuário."
    exit 0
  fi
fi

# Transparência: mostra o comando (usa sudo) antes de pedir confirmação.
echo "Vou rodar: $comando"
read -r -p "Confirmar? (s/n) " ok
if [ "$ok" != "s" ]; then
  echo "Operação cancelada pelo usuário."
  exit 0
fi

eval "$comando"
echo "Comando enviado (modo: $Modo)."
