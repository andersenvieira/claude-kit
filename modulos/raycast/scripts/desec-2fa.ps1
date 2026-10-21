#!/usr/bin/env pwsh
# @raycast.schemaVersion 1
# @raycast.title Desec: código 2FA
# @raycast.mode compact
# @raycast.packageName Desec
# @raycast.icon 🛡️

# Nome do item no cofre do sistema (Credential Manager via SecretManagement).
# Cadastre a semente na própria máquina com:
#   Set-Secret -Name $SecretName -Secret "<semente-base32>"
$SecretName = "desec-totp"

# Função TOTP pura (RFC 6238), usada se o oathtool não estiver disponível no WSL.
# Recebe a semente em Base32 e devolve o código de 6 dígitos da janela atual (30s).
function Get-TotpCodigo {
    param([string]$SeedBase32)

    # Decodifica Base32 para bytes.
    $alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    $seedLimpa = $SeedBase32.ToUpper().Replace(" ", "").Replace("-", "")
    $bits = ""
    foreach ($c in $seedLimpa.ToCharArray()) {
        $idx = $alfabeto.IndexOf($c)
        if ($idx -lt 0) { continue }
        $bits += [Convert]::ToString($idx, 2).PadLeft(5, '0')
    }
    $byteCount = [Math]::Floor($bits.Length / 8)
    $bytes = New-Object byte[] $byteCount
    for ($i = 0; $i -lt $byteCount; $i++) {
        $bytes[$i] = [Convert]::ToByte($bits.Substring($i * 8, 8), 2)
    }

    # Contador de passo de tempo (30s) em big-endian, 8 bytes.
    $passo = [Math]::Floor([double]([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) / 30)
    $contadorBytes = New-Object byte[] 8
    for ($i = 7; $i -ge 0; $i--) {
        $contadorBytes[$i] = [byte]($passo -band 0xFF)
        $passo = $passo -shr 8
    }

    # HMAC-SHA1 e extração dinâmica (dynamic truncation) do RFC.
    $hmac = New-Object System.Security.Cryptography.HMACSHA1(, $bytes)
    $hash = $hmac.ComputeHash($contadorBytes)
    $offset = $hash[$hash.Length - 1] -band 0xF
    $codigoInt = (($hash[$offset] -band 0x7F) -shl 24) -bor `
                 (($hash[$offset + 1] -band 0xFF) -shl 16) -bor `
                 (($hash[$offset + 2] -band 0xFF) -shl 8) -bor `
                 ($hash[$offset + 3] -band 0xFF)
    $codigo = $codigoInt % 1000000
    return $codigo.ToString("D6")
}

# 1) Busca a semente no cofre via SecretManagement (Windows Credential Manager).
$seed = $null
if (Get-Module -ListAvailable -Name Microsoft.PowerShell.SecretManagement) {
    try {
        $seed = Get-Secret -Name $SecretName -AsPlainText -ErrorAction Stop
    } catch {
        Write-Output "Erro: não achei o segredo '$SecretName' no cofre."
        Write-Output "Cadastre com: Set-Secret -Name $SecretName -Secret '<semente-base32>'"
        exit 1
    }
} else {
    Write-Output "Módulo Microsoft.PowerShell.SecretManagement não instalado."
    Write-Output "Instale com: Install-Module Microsoft.PowerShell.SecretManagement, Microsoft.PowerShell.SecretStore -Scope CurrentUser"
    Write-Output "Depois cadastre a semente com: Set-Secret -Name $SecretName -Secret '<semente-base32>'"
    exit 1
}

# 2) Gera o código: prefere oathtool dentro do WSL, se existir; senão usa a função pura.
$codigo = $null
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    $temOathtool = (wsl -- bash -lc "command -v oathtool" 2>$null)
    if ($temOathtool) {
        $codigo = (wsl -- bash -lc "oathtool --totp -b '$seed'" 2>$null).Trim()
    }
}
if (-not $codigo) {
    $codigo = Get-TotpCodigo -SeedBase32 $seed
}

# 3) Mostra e copia para a área de transferência.
Write-Output "Código 2FA Desec: $codigo"
try {
    Set-Clipboard -Value $codigo
    Write-Output "(copiado para a área de transferência)"
} catch {
    Write-Output "Aviso: não consegui copiar automaticamente. Copie o código acima manualmente."
}
