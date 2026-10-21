#!/usr/bin/env pwsh
# @raycast.schemaVersion 1
# @raycast.title Desec: nova nota de relatório
# @raycast.mode compact
# @raycast.packageName Desec
# @raycast.icon 🛡️

# Cofre do Obsidian onde a nota é criada — preencha com o caminho real na sua máquina.
$VaultObsidian = "$HOME\Documents\ObsidianVault\Pentest"

# Caminho do modelo, relativo a este script.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$modelo = Join-Path $scriptDir "..\modelos\relatorio-pentest.md"

if (-not (Test-Path $modelo)) {
    Write-Output "Erro: modelo não encontrado em $modelo"
    exit 1
}
if (-not (Test-Path $VaultObsidian)) {
    Write-Output "Erro: cofre do Obsidian não encontrado em $VaultObsidian (ajuste `$VaultObsidian no script)."
    exit 1
}

# Nome da nota com data/hora (evita sobrescrever relatórios anteriores).
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$nomeNota = "relatorio-pentest-$timestamp.md"
$destino = Join-Path $VaultObsidian $nomeNota

Copy-Item -Path $modelo -Destination $destino

# Abre a nota no Obsidian via URI; se falhar, abre no editor padrão.
$nomeSemExtensao = [System.IO.Path]::GetFileNameWithoutExtension($nomeNota)
try {
    Start-Process "obsidian://open?file=$([Uri]::EscapeDataString($nomeSemExtensao))"
} catch {
    Start-Process $destino
}

Write-Output "Nota criada: $destino"
