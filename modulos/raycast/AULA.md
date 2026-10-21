# Aula — Raycast/Ulauncher a serviço do pentest

Esta aula ensina a usar os atalhos que **você já tem** no Raycast (Windows) / Ulauncher (Linux)
dentro de um fluxo de teste de segurança. Não cria atalho novo aqui — os quatro atalhos novos da
Desec (`desec-abrir`, `desec-2fa`, `desec-vpn`, `desec-nota`) estão descritos no `LEIA.md` deste módulo.

## Antes de tudo: escopo
Teste ativo (varredura, porta, ping dirigido) só em **alvo autorizado**: o laboratório da Desec, uma
cópia local de `~/dev/<projeto>` seu, ou um sistema para o qual você tem autorização por escrito.
Sistema de terceiro fica fora, mesmo que pareça inofensivo. Cada teste ativo começa com uma linha
dizendo o alvo e o que vai ser feito. (É a mesma regra da skill `pentest-professor`.)

## O método em 3 fases (versão curta)
1. **Reconhecimento** — descobrir o que existe: faixa de rede, máquinas vivas, portas abertas.
2. **Enumeração** — detalhar cada porta/serviço achado: versão, banner, o que responde.
3. **Exploração e relatório** — testar a falha (só no lab/autorizado) e registrar no modelo de nota.

Os atalhos ajudam nas fases 1 e 2 (recon e enumeração), que é onde mais se perde tempo manualmente.

## Os atalhos que você já tem, mapeados às fases

### Fase 1 — Reconhecimento
- **Meus IPs** (`meus-ips`) — mostra seu IP local e o público. Serve para saber **de onde** você está
  testando e se já está dentro da VPN do lab (o IP de saída muda quando a VPN sobe). Primeiro atalho
  a rodar depois de ligar a `desec-vpn`.
- **Status VPN** (`status-vpn`) — confirma que o túnel está de pé antes de mirar o alvo. Sem VPN, o
  tráfego nem chega no lab (ou pior, vai pra internet aberta).
- **Calculadora de Sub-rede** (`calculadora-subrede`) — você digita `10.10.10.0/24` e ela diz faixa,
  primeiro/último host e quantos endereços. Use para saber **o tamanho do alvo** antes de varrer:
  `/24` são 254 hosts, `/16` são 65 mil (varredura muito mais longa). *CIDR = a notação `/24` que diz
  quantos bits do endereço são fixos.*
- **Dispositivos na Rede** (`dispositivos-rede`) — lista as máquinas vivas na sua faixa (descoberta
  por ARP/ping). É o "quem está em casa" antes de bater porta por porta. No lab, revela os alvos.

### Fase 2 — Enumeração
- **Ping** (`ping`) — confirma se um host específico responde e a latência. Útil para separar "host
  caído" de "host vivo com firewall" (host vivo mas sem resposta de ping ainda pode ter portas
  abertas — não descarte só pelo ping).
- **Testar Porta** (`testar-porta`) — você dá host + porta e ela diz se está aberta. Para checar um
  serviço pontual (ex.: 22 SSH, 80/443 web, 3389 RDP) sem subir uma varredura inteira.
- **Porta Quem Usa** (`porta-quem-usa`) — na **sua** máquina, mostra qual processo ocupa uma porta.
  Serve para o outro lado do teste: entender o que *você* está expondo, e liberar/conferir uma porta
  antes de subir um listener (ex.: receber um shell reverso no lab).

## Boas práticas (as 5 que mais evitam dor de cabeça)
1. **Devagar e com escopo** — varra a menor faixa que resolve. `/24` antes de `/16`; um host antes da
   faixa toda. Varredura ampla é barulhenta e lenta.
2. **Anote enquanto acha** — cada porta/serviço interessante vira uma linha na nota (`desec-nota`)
   na hora, não no fim. Memória não é evidência.
3. **Evidência mínima** — guarde o comando e o trecho que prova o achado, nunca um dado real completo
   de alguém. Se topar com dado real de cliente, pare e registre só o tipo.
4. **Um alvo por vez** — foque, enumere a fundo, só então o próximo. Pular de host em host perde o fio.
5. **VPN antes, sempre** — rode `status-vpn`/`meus-ips` antes de qualquer teste. Testar fora do túnel
   pode mirar a internet aberta por engano — isso é teste não autorizado.

## Fluxo típico de uma sessão de lab (juntando tudo)
1. `desec-vpn` liga o túnel → `status-vpn` + `meus-ips` confirmam que você está dentro.
2. `calculadora-subrede` na faixa do lab → sei o tamanho.
3. `dispositivos-rede` → lista os hosts vivos.
4. Escolho um host: `ping` → `testar-porta` nas portas comuns (ou uma varredura com nmap no Kali).
5. Cada achado vira linha em `desec-nota` (modelo de relatório).
6. No fim, a nota já está quase pronta: severidade, evidência, correção, como verificar.

## Próxima ação (até 2 min)
Ligue a VPN do lab (`desec-vpn`) e rode `meus-ips` — confirme que o IP de saída mudou. É o "oi, estou
dentro" antes de qualquer teste.
