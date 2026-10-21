#!/usr/bin/env pwsh
# @raycast.schemaVersion 1
# @raycast.title Desec: ligar VPN
# @raycast.mode compact
# @raycast.packageName Desec
# @raycast.icon 🛡️
# @raycast.argument1 { "type": "dropdown", "placeholder": "Modo", "optional": true, "data": [{"title": "wsl", "value": "wsl"}, {"title": "kali", "value": "kali"}] }

param(
    [ValidateSet("wsl", "kali")]
    [string]$Modo = "wsl",
    [switch]$Instalar
)

# Variáveis específicas da máquina — preencha com os valores reais na sua máquina.
$DistroWSL   = "kali-linux"            # nome da distro WSL que roda o OpenVPN
$HostKali    = "kali"                  # host/alias SSH da VM Kali (ex.: em ~/.ssh/config)
$OvpnPathWSL = "~/desec/desec.ovpn"    # caminho do .ovpn dentro do WSL (nunca no kit)

# Monta o comando conforme o modo escolhido.
if ($Modo -eq "wsl") {
    $comando = "wsl -d $DistroWSL -- sudo openvpn --config $OvpnPathWSL --daemon"
} else {
    $comando = "ssh $HostKali 'sudo systemctl start openvpn@desec'"
}

# Se pedido, instala o pacote openvpn no alvo antes de ligar a VPN (nunca sem a flag).
if ($Instalar) {
    if ($Modo -eq "wsl") {
        $comandoInstalar = "wsl -d $DistroWSL -- sudo apt-get install -y openvpn"
        $comandoChecar   = "wsl -d $DistroWSL -- bash -lc 'test -f $OvpnPathWSL && echo OK || echo FALTA'"
    } else {
        $comandoInstalar = "ssh $HostKali 'sudo apt-get install -y openvpn'"
        $comandoChecar   = "ssh $HostKali 'test -f ~/desec/desec.ovpn && echo OK || echo FALTA'"
    }
    Write-Output "Vou rodar (instalação): $comandoInstalar"
    $ok = Read-Host "Confirmar? (s/n)"
    if ($ok -eq "s") {
        Invoke-Expression $comandoInstalar
        Write-Output "Checando .ovpn em ~/desec/ ..."
        Invoke-Expression $comandoChecar
    } else {
        Write-Output "Instalação cancelada pelo usuário."
        exit 0
    }
}

# Transparência: mostra o comando (usa sudo) antes de pedir confirmação.
Write-Output "Vou rodar: $comando"
$ok = Read-Host "Confirmar? (s/n)"
if ($ok -ne "s") {
    Write-Output "Operação cancelada pelo usuário."
    exit 0
}

Invoke-Expression $comando
Write-Output "Comando enviado (modo: $Modo)."
