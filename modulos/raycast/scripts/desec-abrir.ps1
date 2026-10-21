#!/usr/bin/env pwsh
# @raycast.schemaVersion 1
# @raycast.title Desec: abrir Academy
# @raycast.mode compact
# @raycast.packageName Desec
# @raycast.icon 🛡️

# Abre a plataforma da Desec Security no navegador padrão do Windows.
$UrlDesec = "https://academy.desecsecurity.com/"

Start-Process $UrlDesec
Write-Output "Abrindo $UrlDesec"
