#!/bin/sh
# Marca "agente de IA agiu agora" para o vigia de ociosidade (/usr/local/sbin/rdp-idle-reaper.py).
# Chamado pelos hooks do Claude Code. Nunca falha e nunca imprime nada.
u=$(id -un 2>/dev/null || echo desconhecido)
for d in /run/ai-agent-activity /var/tmp/ai-agent-activity; do
  [ -d "$d" ] || mkdir -p "$d" 2>/dev/null || continue
  touch "$d/claude-$u" 2>/dev/null && break
done
exit 0
