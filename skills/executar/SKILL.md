---
name: executar
description: Executar um docs/PLANO_*.md já aprovado — despacha as tarefas para agentes baratos, faz a revisão única no fim e fecha a etapa.
---
# Executar plano aprovado

Pré-requisito: plano aprovado ("ok" ou ExitPlanMode aceito). Sem perguntar de novo.

1. **Ler o PLANO uma vez** e montar a fila de tarefas com dono: eu (≤2 arquivos ou decisão fina),
   `mecanico` (Haiku, repetitivo com instrução exata) ou `implementador` (Sonnet, código).
2. **Despachar.** Prompt do agente: caminho do PLANO, número da tarefa, arquivos que são dele, teste dele.
   Paralelo só com arquivos disjuntos. Agente que trava ou pede decisão fora do plano volta para mim.
3. **Revisão única no fim:** `git diff --stat` + leitura do diff, suíte completa (`| tail -5`),
   verificação por script do critério de sucesso. Plano com etiqueta `seg`: a revisão passa pela
   skill `engenharia-segura` antes de fechar. Corrigir eu mesmo o que for pequeno.
4. **Fechar:** marcar tarefas feitas no PLANO, ESTADO/HISTORICO e a linha do /clear.
   Publicar em produção (script de deploy do projeto, qualquer que seja) só se o usuário pedir.

Sinais de erro: agente em Opus; dois agentes no mesmo arquivo; revisor por tarefa; dizer "pronto" sem suíte.
