# Módulo `vps` — regras de uma VPS de dev + produção

Inativo por padrão. Só entra em vigor quando o usuário disser "estou na VPS" (ou equivalente), ou
quando o hostname da máquina bater com o configurado abaixo. Em qualquer outro lugar (notebook, outra
VPS, chat), este módulo fica fora — não aplicar essas regras lá.

Só Linux (servidor): os scripts usam bash, systemd e caminhos Linux. Em Windows/macOS, não instalar.

## Como detectar
- O usuário diz explicitamente "estou na VPS" (ou nome da VPS) numa conversa.
- OU o hostname da máquina (`hostname`) bate com `<HOSTNAME_A_CONFIGURAR>` — valor que o usuário
  define ao instalar o módulo; nunca o nome real fica neste arquivo público.

## Regras desta máquina (generalizadas, sem segredo)
- Produção não se edita direto: produção fica fora da pasta de trabalho do dia a dia (ex.:
  `/var/www/<dominio>/<PROJ>`), e o trabalho é sempre em `~/dev/<PROJ>`. Publicação só por um script
  de deploy (`deploy.sh <PROJ>`), e só quando o usuário pedir.
- Projeto citado fora da pasta aberta: avisar em uma linha onde vai trabalhar e seguir; projeto
  ambíguo, perguntar antes de editar.
- Nunca seeder, `migrate:fresh`/`refresh`, `db:wipe`, truncate ou qualquer comando que reinicialize
  dados, em nenhum projeto, sem pedido explícito e sem backup antes.
- Parar para perguntar só se for ambíguo ou arriscado (apagar dados, produção, dinheiro, segurança,
  irreversível). Mudança de segurança (firewall, SSH, DNS): fazer backup antes e ter caminho de volta
  testado.

## Onde ficam os detalhes sensíveis
IPs, nomes de serviço, cofre de senhas e chaves não entram neste kit público. Para saber onde fica
cada coisa na VPS, use `cerebro.py busca` (quando existir) ou `mapa.py busca` (script deste kit,
em `bin/mapa.py`) enquanto o cérebro não existir. Detalhes sensíveis (IPs reais, serviços, cofre,
chaves) ficam numa pasta privada do Google Drive do usuário — procure lá pelo conector do Drive
quando precisar de um valor real.

## Scripts deste módulo
- `sentinela-vps.py` — vigia de ociosidade/disponibilidade da sessão (hook).
- `ai-heartbeat.sh` — heartbeat usado pelo sentinela nos eventos de hook.
- `sessoes.py` — inventário de sessões do Claude nesta máquina.

Instalar este módulo só quando o usuário pedir ("aplique o kit com vps") ou quando a detecção acima
disparar — nunca por padrão. Se já existir versão desses scripts na máquina, usar a que já está lá
em vez de sobrescrever (regra geral de módulos do `LEIA-PRIMEIRO.md`).
