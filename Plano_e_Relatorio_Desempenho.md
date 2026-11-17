# Plano e Relatório de Teste de Desempenho

Equipe: Francisco Cássio e Álvaro Miguel   Pacote/Projeto: Pacote A, Pacote B e Clínica Agenda   Data: 17/11/2026

## 1. Plano (preencher ANTES de executar)

| Item | Preenchimento |
|---|---|
| Pergunta / hipótese | |
| Operações testadas e proporção | |
| Verificações de conteúdo | |
| Think time (pausa entre ações) | |
| Massa de dados | |
| Perfis (usuários, ritmo, duração) | Carga: ___  Estresse: ___  Pico: ___  Recuperação: ___ |
| Repetições | |
| Metas (SLA) | p95 ≤ ___ ms; falhas ≤ ___ %; outras: ___ |
| Critério de parada | |

## 2. Ambiente

| Item | Valor |
|---|---|
| Processador / memória | |
| Sistema operacional | |
| Python ou JDK (versão) | |
| Ferramenta e versão (Locust/Gatling) | |
| Servidor e gerador de carga na mesma máquina? | |

## 3. Resultados

Preencha `resultados/Registro_Resultados_Desempenho.csv` com uma linha por execução e
cole aqui a tabela-resumo e os gráficos (p95, req/s e falhas por patamar).

## 4. Análise

- A meta foi atendida em cada teste? Em qual patamar deixou de ser?
- Qual endpoint piora primeiro? A vazão parou de crescer em algum ponto?
- O sistema se recuperou após o estresse? Em quanto tempo?
- As repetições deram resultados parecidos? O que explica as diferenças?

## 5. Limitações e recomendações

- 
