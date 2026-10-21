# Módulo `raycast` — esqueleto

**Estado: a completar.** O conteúdo do kit/aula do Raycast ainda não existe nesta máquina. Quando o
usuário disser "aplique o kit com raycast" sem ter colado o resumo da aula antes, pedir o resumo a
ele em vez de inventar conteúdo.

## Como detectar se o Raycast está instalado
- macOS: existe `/Applications/Raycast.app`.
- Windows: procurar "Raycast" no menu Iniciar ou em `%AppData%` / `%LocalAppData%` (instalador do
  Raycast para Windows).
- Se não achar em nenhum dos dois: avisar que o Raycast não está nesta máquina e seguir sem o módulo.

## Regra de uso
Se o Raycast já estiver instalado e configurado na máquina, usar o que já está lá — não reinstalar
nem reconfigurar por conta própria. Se não estiver, só instalar quando o usuário pedir.

## Ideia já decidida (confirmar o resto com o usuário)
O Raycast guarda a lista de máquinas (nomes de uma rede Tailscale ou equivalente); o usuário diz só
o **nome** da máquina, nunca o IP. O IP real nunca fica num arquivo público deste kit — fica dentro
do Raycast (ou de uma pasta privada), e o módulo só aponta para lá.

## Pendência
Colar aqui o resumo da aula/kit do Raycast quando o usuário fornecer, e preencher o resto deste
módulo (comandos, scripts, atalhos) a partir dele.
