---
name: brainstorm
description: Desenho de funcionalidade nova ou mudança de fluxo (nível 3 da triagem) antes de qualquer código — perguntas curtas, caminhos com recomendação, um único PLANO e um ok.
---
# Brainstorm enxuto

Objetivo: o usuário reconhecer e aprovar O QUE será feito antes de qualquer código, com o mínimo de idas e voltas.

1. **Contexto primeiro, barato.** Leia só o necessário (ESTADO do projeto, arquivos do fluxo afetado via grep). Pedido que junta vários subsistemas independentes: diga isso e proponha a ordem; desenhe só o primeiro.
2. **Entendimento em 3–5 linhas.** Objetivo, restrições, critério de sucesso. Separe "você disse" de "estou supondo".
3. **Perguntas: só as que mudam o desenho, uma por vez**, de preferência múltipla escolha (AskUserQuestion) com a recomendada primeiro. Não pergunte o que dá para descobrir no código ou decidir por padrão sensato — decida e diga.
4. **2–3 caminhos só quando houver escolha real**, com trade-off em uma linha cada e a recomendação à frente. YAGNI: corte o que não serve ao objetivo.
5. **Desenho em chat, curto:** componentes/arquivos, fluxo de dados, erros, como testar. Cada parte do tamanho da sua complexidade. Pedido com etiqueta `seg`: 2–3 linhas de risco (dado sensível, quem acessa, pior caso) dentro do próprio desenho, sem virar seção separada.
6. **Um documento:** `docs/PLANO_<assunto>.md` com o desenho aprovado + tarefas pequenas (arquivos de cada uma, critério de aceite, teste, modelo do agente: mecanico/implementador/eu). Sem spec separada.
7. **Um ok.** Com o contexto coletado, entre no modo plano (EnterPlanMode: no `opusplan` o Opus assume) para desenhar; saia com ExitPlanMode mostrando o plano em poucas linhas — a aprovação é o ok. Depois grave o PLANO e siga com a skill `executar`, sem perguntar de novo.

Sinais de erro: escrever código antes do ok; perguntar várias coisas numa mensagem; fazer levantamento de opções sem recomendar; plano com "TBD".
