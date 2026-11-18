# Plano e Relatório de Teste de Desempenho

Equipe: Francisco Cássio e Álvaro Miguel   Pacote/Projeto: Pacotes A, B e Clínica Agenda   Data: 17/11/2026

## 1. Plano (preenchido ANTES de executar)

### 1.1 Desafio A – Abertura da Matrícula (Pacote A - `http://localhost:5000`)

| Item | Preenchimento |
|---|---|
| Pergunta / hipótese | Com 100 alunos simultâneos durante 2 minutos na abertura de matrícula, o portal mantém p95 geral ≤ 800 ms, p95 do comprovante ≤ 1500 ms e erros técnicos < 1%, sem gerar vagas negativas? |
| Operações testadas e proporção | `GET /api/disciplinas` (50% - peso 5), `POST /api/matriculas` (30% - peso 3), `GET /api/matriculas/<id>/comprovante` (20% - peso 2). Justificativa: os alunos consultam a grade várias vezes antes e depois de confirmar a matrícula, e em seguida baixam o comprovante. |
| Verificações de conteúdo | `GET /api/disciplinas`: HTTP 200, lista não vazia e nenhuma disciplina com `vagas < 0`. `POST /api/matriculas`: HTTP 201 (sucesso com `comprovante` iniciando em `COMP-`) ou regras de negócio HTTP 409/422 (contabilizadas separadamente sem contar como falha técnica). `GET /api/matriculas/<id>/comprovante`: HTTP 200 e `id` correspondente. |
| Think time (pausa entre ações) | 1 a 3 segundos (`between(1, 3)`) simulando o tempo de leitura e seleção na tela. |
| Massa de dados | Um aluno único por usuário virtual (`20260001` a `20260200`, e reciclagem controlada acima de 200 no estresse) e combinações válidas de disciplinas sem choque de horário (ex.: `["ES3", "BD2", "PW2"]`, `["RED", "IHC", "EMP"]`, `["BD2", "IHC", "MOB"]`). |
| Perfis (usuários, ritmo, duração) | **Carga:** 100 alunos constantes por 120 s (rampa de 20/s). **Pico:** 10 alunos base -> salto para 200 alunos em até 10 s (por 40 s) -> retorno a 20 alunos (total 90 s). **Estresse:** degraus de +50 alunos a cada 25 s até 400 alunos. |
| Repetições | Execução completa para cada perfil (`carga`, `pico`, `estresse`), com reset prévio via `POST /api/admin/reset`. |
| Metas (SLA) | p95 geral ≤ 800 ms; p95 do comprovante ≤ 1500 ms; falhas técnicas (5xx/timeout) < 1%; zero disciplinas com vagas negativas. |
| Critério de parada | Falhas técnicas > 20% por 10 s consecutivos, p95 geral > 3000 ms sustentado ou término do tempo planejado do perfil. |

### 1.2 Desafio B – Consulta de Minicursos (Pacote B - `http://127.0.0.1:8000`)

| Item | Preenchimento |
|---|---|
| Pergunta / hipótese | Com 20 usuários simultâneos consultando minicursos, o sistema atende p95 ≤ 500 ms e falhas ≤ 1%, e consegue retornar a esse patamar em até 30 s após sofrer estresse de 50 e 100 usuários? |
| Operações testadas e proporção | `GET /api/cursos` (70% - peso 7) e `GET /api/cursos/1` (30% - peso 3). |
| Verificações de conteúdo | `GET /api/cursos`: HTTP 200, JSON com `total == 3` e presença do curso `"Python"` na lista `itens`. `GET /api/cursos/1`: HTTP 200, JSON com `id == 1`, `nome == "Python"` e `vagas == 2`. |
| Think time (pausa entre ações) | 0,2 a 0,6 s (`between(0.2, 0.6)`). |
| Massa de dados | Consultas públicas de leitura aos 3 minicursos em memória (`Python`, `Java`, `Testes de Software`). |
| Perfis (usuários, ritmo, duração) | **Verificação inicial:** 1 u (r=1, 15 s). **Referência:** 5 u (r=1, 90 s). **Carga nominal:** 20 u (r=2, 90 s). **Estresse 1:** 50 u (r=5, 90 s). **Estresse 2:** 100 u (r=10, 90 s). **Recuperação:** 20 u (r=2, 90 s). |
| Repetições | 3 repetições por patamar (`r1`, `r2`, `r3`). |
| Metas (SLA) | Na carga nominal (20 usuários): p95 ≤ 500 ms e falhas ≤ 1%; recuperação para p95 ≤ 500 ms e falhas ≤ 1% em até 30 s com 20 usuários. |
| Critério de parada | Instabilidade da máquina, falhas > 20% por 10 s ou p95 > 2000 ms por 10 s (observando que HTTP 503 sob estresse faz parte do limite didático de 4 consultas simultâneas do servidor). |

### 1.3 Projeto Anterior – Clínica Agenda (Django REST - `http://127.0.0.1:8001`)

| Item | Preenchimento |
|---|---|
| Pergunta / hipótese | A API da Clínica Agenda suporta 20 usuários simultâneos consultando especialidades, especialistas, horários disponíveis e autenticando/listando consultas com p95 ≤ 600 ms e falhas ≤ 1%, e se recupera após estresse de 60 usuários? |
| Operações testadas e proporção | `GET /api/agendamentos/especialidades/` (35% - peso 7), `GET /api/agendamentos/horarios/?status=DISPONIVEL` (35% - peso 7), `GET /api/usuarios/especialistas/` (15% - peso 3) e `GET /api/agendamentos/consultas/` autenticado via JWT (15% - peso 3). |
| Verificações de conteúdo | HTTP 200 em todas as listagens paginadas, presença das chaves `"count"` e `"results"` no JSON do Django REST Framework, `count >= 1` nas especialidades/especialistas e validação de token JWT no `on_start`. |
| Think time (pausa entre ações) | 0,5 a 1,5 s (`between(0.5, 1.5)`). |
| Massa de dados | Banco populado via script de seed com especialidades médicas (`Cardiologia`, `Dermatologia`, `Ortopedia`), especialistas credenciados, agendas com horários gerados para 30 dias e pacientes autenticados com JWT. |
| Perfis (usuários, ritmo, duração) | **Carga nominal:** 20 usuários (r=4, 45 s). **Estresse:** 60 usuários (r=10, 45 s). **Recuperação:** 20 usuários (r=4, 45 s). |
| Repetições | 3 repetições por patamar (`r1`, `r2`, `r3`). |
| Metas (SLA) | Na carga nominal (20 usuários): p95 ≤ 600 ms e falhas técnicas ≤ 1%. |
| Critério de parada | Falhas > 20% por 10 s ou p95 > 2500 ms por 10 s. |

## 2. Ambiente

| Item | Valor |
|---|---|
| Processador / memória | Intel Core (Family 6 Model 140 Stepping 1) - 4 núcleos físicos / 8 threads, 8 GB RAM (7,79 GB utilizáveis) |
| Sistema operacional | Windows 11 (10.0.26200) 64 bits |
| Python ou JDK (versão) | Python 3.12.10 |
| Ferramenta e versão (Locust/Gatling) | Locust 2.47.0 |
| Servidor e gerador de carga na mesma máquina? | Sim (`localhost` / `127.0.0.1`), compartilhando CPU e memória entre o servidor web e os workers do Locust. |

## 3. Resultados

*(Será preenchido após a execução das baterias com os dados de `resultados/Registro_Resultados_Desempenho.csv`)*

## 4. Análise

*(Será preenchido após a coleta das métricas)*

## 5. Limitações e recomendações

*(Será preenchido após a análise dos gargalos)*
