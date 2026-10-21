# Módulo `raycast` — atalhos de pentest (Desec) para Raycast/Ulauncher

Lançador de atalhos para o estudo de pentest: abrir a academia, gerar o 2FA, ligar a VPN do
laboratório e abrir uma nota de relatório. **Educacional e só para alvos próprios/autorizados**
(laboratório da Desec ou aplicação sua) — a aula (`AULA.md`) e o modelo de nota deixam o escopo explícito.

Inativo por padrão. Só instalar quando o usuário disser "aplique o kit com raycast". Se os atalhos já
existirem e estiverem configurados na máquina, usar o que está lá — não reconfigurar por conta própria.

## Como detectar o lançador
- **Windows — Raycast:** procurar "Raycast" no menu Iniciar ou em `%LocalAppData%`/`%AppData%`. Os
  atalhos são os arquivos `.ps1` de `scripts/` (adicionar a pasta em Raycast → Extensions → Script Commands).
- **Linux — Ulauncher:** Raycast não tem Linux; usar os `.sh` de `scripts/` como entradas de shell
  no Ulauncher (ou aliases). Mesmo comportamento dos `.ps1`.
- Se não achar nenhum dos dois: avisar que o lançador não está nesta máquina e seguir sem o módulo.

## Os quatro atalhos (`scripts/`)
| Atalho | Faz |
|---|---|
| `desec-abrir` | Abre `https://academy.desecsecurity.com/` no navegador padrão. |
| `desec-2fa` | Gera o código TOTP do Google, **mostra e copia**. A semente vem do cofre do sistema — nunca do kit. |
| `desec-vpn` | Liga a VPN do lab. Modo `wsl` (padrão) ou `kali`, e flag de instalar o pacote. |
| `desec-nota` | Cria uma nota de relatório no Obsidian a partir de `modelos/relatorio-pentest.md`. |

## Onde ficam os segredos (NUNCA no kit)
- **Semente do 2FA:** no cofre do sistema. Windows: `Microsoft.PowerShell.SecretManagement`
  (`Set-Secret -Name desec-totp`). Linux: `secret-tool store --label=desec-totp service desec-totp`.
  O script só **lê** de lá (`Get-Secret` / `secret-tool lookup`). A semente nunca é gravada em arquivo.
- **`.ovpn` e senha da VPN:** numa pasta privada da máquina, `~/desec/` (ex.: `~/desec/desec.ovpn`).
  O kit não traz esse arquivo — você baixa da Desec e salva lá.
- Confirme antes de publicar: nenhum valor real pode aparecer em `scripts/` (grep anti-segredo).

## O que o usuário preenche na máquina (variáveis no topo de cada script)
- `desec-vpn`: `DistroWSL` (nome da distro no WSL, ex.: `kali-linux`), `HostKali` (host SSH da VM Kali),
  `OvpnPath`/`OvpnPathWSL` (caminho do `.ovpn`).
- `desec-2fa`: `SecretName` (nome do item no cofre, padrão `desec-totp`).
- `desec-nota`: `VaultObsidian` (pasta do cofre do Obsidian onde a nota é criada).

## Como testar (na máquina, depois de configurar)
1. `desec-2fa` → o código de 6 dígitos tem que bater com o Google Authenticator no mesmo instante.
2. `desec-vpn -Modo wsl` → o script mostra o comando e pede confirmação antes do `sudo`; depois de
   subir, rodar `meus-ips`/`status-vpn` e ver o IP de saída mudar (dentro do WSL, `curl ifconfig.me`).
3. `desec-nota` → abre uma nota nova no Obsidian já com o cabeçalho do modelo.
4. `desec-abrir` → abre a academia no navegador padrão.

## Dependências por plataforma
- Windows: Raycast; módulo `Microsoft.PowerShell.SecretManagement` para o 2FA; WSL (modo `wsl` da VPN).
- Linux: Ulauncher; `oathtool` (2FA), `secret-tool` (cofre), `xclip`/`wl-copy` (copiar), `openvpn` (VPN).
  Cada script avisa de forma clara se faltar uma dependência, sem travar.
