---
name: engenharia-segura
description: Pedido com etiqueta `seg` (login/permissão, entrada externa, SQL dinâmico, pagamento, credencial, infraestrutura) — desenhar ou revisar com foco em segurança e em sistema que aguenta crescer, não só "funciona agora".
---

# Engenharia segura e escalável

Carregada só quando o pedido tem a etiqueta `seg`. Objetivo: pensar como quem vai manter o sistema
daqui a um ano com 100x mais uso, não só fazer passar no teste de hoje.

## 1. Desenho (antes do código)
- Que dado sensível isso toca (senha, pagamento, documento, localização)? Onde ele fica guardado e por quanto tempo?
- Quem pode chamar isso — todo mundo, usuário logado, só o dono do recurso, só admin? Onde essa checagem mora?
- Qual é a fronteira de confiança (o que vem de fora: formulário, upload, parâmetro de URL, webhook,
  resposta de outra API) — tudo isso é entrada não confiável até provar o contrário.
- Pior caso: o que um usuário mal-intencionado ganha se abusar disso?

## 2. Código seguro (checklist curto, não teórico)
- Entrada externa sempre validada/sanitizada no servidor, nunca confiar só no front.
- Consulta a banco sempre parametrizada — nunca concatenar string em SQL.
- Saída que vai pro HTML sempre escapada (evita XSS); upload sempre com tipo/tamanho checado e fora do webroot quando possível.
- Autenticação e autorização checadas no servidor em cada rota sensível, não só escondidas na UI.
- Segredo (senha, token, chave) nunca em log, commit ou resposta de erro; variável de ambiente ou cofre, não hardcode.
- Erro para o usuário é genérico; o detalhe técnico vai só pro log interno.

## 3. Escala (o que quebra primeiro quando o uso cresce)
- Serviço sem estado em memória do processo (estado vai pro banco/cache, não numa variável global).
- Consulta com índice nas colunas de filtro/join; evitar N+1 (carregar em lote, não em loop).
- Lista grande sempre paginada; nunca "trazer tudo".
- Trabalho pesado ou demorado vai pra fila, não trava a resposta.
- Toda chamada de rede tem timeout; toda operação repetível (retry) é idempotente.
- Cache tem dono e tem expiração — nunca "fica lá para sempre".

## 4. Operação
- Log registra o suficiente pra investigar (quem, quando, o quê) sem gravar dado sensível.
- Mudança que apaga/sobrescreve dado tem backup verificado antes, igual a qualquer migração.
- Menor privilégio: usuário de banco/serviço só com a permissão que a tarefa exige.

## Saída
Para cada achado: **achado · risco (o que pode dar errado) · correção**, em 1-2 linhas cada. Diff
pronto em git: oferecer rodar `/security-review` para uma segunda passada antes de fechar.
