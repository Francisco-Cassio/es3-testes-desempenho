# Plano e Relatório de Teste de Desempenho

**Equipe:** Francisco de Cássio da Silva Mourão Júnior e Álvaro Miguel Rodrigues Aquino Costa  
**Pacote/Projeto:** Pacote A (Sabor Express + Matrícula), Pacote B (Biblioteca + Minicursos) e Projeto Anterior (Clínica Agenda)  
**Data:** 17/11/2026 a 20/11/2026

---

## 1. Plano (Preenchido ANTES da execução)

### 1.1 Desafio A – Abertura da Matrícula (Pacote A - `http://127.0.0.1:5000`)

| Item | Preenchimento |
|---|---|
| **Pergunta / hipótese** | Com 100 alunos simultâneos durante 2 minutos na abertura de matrícula, o portal mantém p95 geral ≤ 800 ms, p95 do comprovante ≤ 1500 ms e erros técnicos < 1%, sem jamais gerar vagas negativas? |
| **Operações testadas e proporção** | `GET /api/disciplinas` (50% - peso 5), `POST /api/matriculas` (30% - peso 3), `GET /api/matriculas/<id>/comprovante` (20% - peso 2). Justificativa: alunos consultam a oferta repetidamente antes e após confirmar a matrícula e baixam o comprovante em seguida. |
| **Verificações de conteúdo** | `GET /api/disciplinas`: HTTP 200, JSON com lista não vazia e nenhuma disciplina com `vagas < 0`. `POST /api/matriculas`: HTTP 201 (com `comprovante` iniciando em `COMP-`) ou HTTP 409/422 (regras de negócio contabilizadas à parte via `resp.success()`). `GET /api/matriculas/<id>/comprovante`: HTTP 200 e `comprovante` válido. |
| **Think time (pausa entre ações)** | 1 a 3 segundos (`between(1, 3)`). |
| **Massa de dados** | Um aluno distinto por usuário virtual (`20260001` a `20260200`) e grades válidas sem choque de horário (`["ES3", "BD2", "PW2"]`, `["RED", "IHC", "EMP"]`, etc.). |
| **Perfis (usuários, ritmo, duração)** | **Carga:** 100 alunos por 120 s (r=20/s). **Pico:** 10 alunos -> salto para 200 alunos em < 10 s (r=40/s) -> retorno a 20 alunos (90 s). **Estresse:** degraus de +50 alunos a cada 25 s até 400 alunos (200 s). |
| **Repetições** | 1 bateria completa por perfil (`carga`, `pico`, `estresse`), precedida por `POST /api/admin/reset`. |
| **Metas (SLA)** | p95 geral ≤ 800 ms; p95 do comprovante ≤ 1500 ms; falhas técnicas (5xx/timeout) < 1%; 0 disciplinas com vagas negativas. |
| **Critério de parada** | Término do perfil planejado ou instabilidade severa do sistema operacional. |

### 1.2 Desafio B – Consulta de Minicursos (Pacote B - `http://127.0.0.1:8000`)

| Item | Preenchimento |
|---|---|
| **Pergunta / hipótese** | Com 20 usuários simultâneos consultando minicursos, o portal mantém p95 ≤ 500 ms e falhas ≤ 1%, identifica o ponto de saturação nos patamares de estresse (50 e 100 usuários) e se recupera em até 30 s ao retornar para 20 usuários? |
| **Operações testadas e proporção** | `GET /api/cursos` (70% - peso 7) e `GET /api/cursos/1` (30% - peso 3). |
| **Verificações de conteúdo** | `GET /api/cursos`: HTTP 200, `total == 3` e presença do curso `"Python"`. `GET /api/cursos/1`: HTTP 200, `id == 1`, `nome == "Python"` e `vagas == 2`. |
| **Think time (pausa entre ações)** | 0,2 a 0,6 s (`between(0.2, 0.6)`). |
| **Massa de dados** | Catálogo em memória de 3 minicursos com 2 vagas cada. |
| **Perfis (usuários, ritmo, duração)** | **Verificação:** 1 u (r=1). **Referência:** 5 u (r=1). **Carga nominal:** 20 u (r=2). **Estresse 1:** 50 u (r=5). **Estresse 2:** 100 u (r=10). **Recuperação:** 20 u (r=2). |
| **Repetições** | 3 repetições por patamar (`r1`, `r2`, `r3`), totalizando 18 execuções independentes. |
| **Metas (SLA)** | Na carga nominal (20 u) e recuperação (20 u): p95 ≤ 500 ms e falhas ≤ 1%. |
| **Critério de parada** | Falhas > 20% por 10 s ou p95 > 2000 ms por 10 s (concluindo o patamar até 100 usuários para registrar a evidência de HTTP 503). |

### 1.3 Projeto Anterior – Clínica Agenda (API Django REST - `http://127.0.0.1:8001`)

| Item | Preenchimento |
|---|---|
| **Pergunta / hipótese** | A API Django REST da Clínica Agenda suporta 20 usuários simultâneos (autenticação JWT + listagem de especialidades, especialistas, horários disponíveis e consultas) com p95 ≤ 600 ms e falhas ≤ 1%, e se recupera imediatamente após estresse de 60 usuários? |
| **Operações testadas e proporção** | `GET /api/agendamentos/especialidades/` (35% - peso 7), `GET /api/agendamentos/horarios/?status=DISPONIVEL` (35% - peso 7), `GET /api/usuarios/especialistas/` (15% - peso 3) e `GET /api/agendamentos/consultas/` (15% - peso 3, autenticado com Bearer Token obtido no `on_start` via `POST /api/token/`). |
| **Verificações de conteúdo** | HTTP 200, estrutura paginada do DRF (`count` e `results`), `count >= 3` em especialidades (incluindo `"Cardiologia"`), `count >= 1` em horários disponíveis e especialistas, e presença de token JWT `"access"` no login. |
| **Think time (pausa entre ações)** | 0,5 a 1,5 s (`between(0.5, 1.5)`). |
| **Massa de dados** | Banco populado via `seed_clinica.py`: 3 especialidades, 3 especialistas com agendas ativas (234 horários disponíveis) e 30 pacientes (`paciente01` a `paciente30`). |
| **Perfis (usuários, ritmo, duração)** | **Carga nominal:** 20 u (r=4). **Estresse:** 60 u (r=10). **Recuperação:** 20 u (r=4). |
| **Repetições** | 3 repetições por patamar (`r1`, `r2`, `r3`), totalizando 9 execuções. |
| **Metas (SLA)** | Na carga nominal (20 u) e recuperação (20 u): p95 ≤ 600 ms e falhas técnicas ≤ 1%. |
| **Critério de parada** | Falhas > 20% por 10 s ou p95 > 3500 ms. |

---

## 2. Ambiente

| Item | Valor |
|---|---|
| **Processador / memória** | Intel Core (Family 6 Model 140 Stepping 1) – 4 núcleos físicos / 8 threads, 8 GB RAM (7,79 GB utilizáveis) |
| **Sistema operacional** | Windows 11 (10.0.26200) 64-bit |
| **Python (versão)** | Python 3.12.10 |
| **Ferramenta e versão** | Locust 2.47.0 |
| **Servidor e gerador de carga na mesma máquina?** | Sim (`127.0.0.1`), compartilhando CPU e pilha TCP/IP local. |

---

## 3. Resultados Medidos

Todos os dados brutos estão em `resultados/Registro_Resultados_Desempenho.csv` e nas subpastas de cada pacote. Abaixo estão as tabelas-resumo com os valores **medidos** pelo Locust.

### 3.1 Pacote A – Exemplo Resolvido e Desafio A (Matrícula Acadêmica)

| Cenário | Perfil | Usuários | Reqs | p50 (ms) | p95 Geral (ms) | p95 Gargalo (ms) | Vazão (req/s) | Falhas Técnicas (%) | Decisão SLA |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Exemplo A (Lanchonete)** | Carga | 50 | 1.401 | 2.100 | 2.100 | 2.700 (`/relatorio/vendas`) | 11,61 | 0,00% | **Não atende** |
| **Exemplo A (Lanchonete)** | Estresse | 250 | 9.639 | 2.100 | 2.200 | 6.800 (`/relatorio/vendas`) | 32,06 | 0,00% | **Não atende** |
| **Desafio A (Matrícula)** | Carga (2 min) | 100 | 3.154 | 45 | 10.000 | 10.000 (`/comprovante`) | 26,15 | 15,28% | **Não atende** |
| **Desafio A (Matrícula)** | Pico (0->200) | 200 | 4.273 | 27 | 67 | 5.900 (`/comprovante`) | 47,76 | 1,61% | **Não atende** |
| **Desafio A (Matrícula)** | Estresse (400) | 400 | 21.216 | 28 | 69 | 3.300 (`/comprovante`) | 106,11 | 4,66% | **Não atende** |

**Detalhamento por Endpoint no Desafio A (Matrícula Acadêmica):**
- `GET /api/disciplinas`: p50 = `26–29 ms`, p95 = `33–38 ms` (muito abaixo da meta de 800 ms).
- `POST /api/matriculas`: p50 = `57–58 ms`, p95 = `63–68 ms`. Contabilizou exatamente as 53–55 matrículas possíveis até esgotar as vagas das disciplinas (`HTTP 201`), e classificou corretamente milhares de respostas `HTTP 409` (vagas esgotadas / aluno já matriculado) como regra de negócio válida. **Nenhuma disciplina ficou com vagas negativas (`vagas_negativas_detectadas = 0`).**
- `GET /api/matriculas/[id]/comprovante`: p95 atingiu `3.300 ms` a `10.000 ms` (estourando o timeout de 10 s no perfil de carga contínua), violando a meta de `1.500 ms`.

### 3.2 Pacote B – Exemplo Resolvido e Desafio B (Consulta de Minicursos)

| Patamar / Fase | Usuários (-u) | Ritmo (-r) | Reqs (média 3 reps) | p50 (ms) (r1 / r2 / r3) | p95 (ms) (r1 / r2 / r3) | Vazão req/s (média) | Falhas % (r1 / r2 / r3) | Decisão SLA |
|---|---:|---:|---:|---|---|---:|---|---|
| **Exemplo B (Catálogo)** | 20 | 2 | 3.851 | 36 | 42 | 43,12 | 0,00% | **Atende** |
| **1. Verificação inicial** | 1 | 1 | 33 | 36 / 36 / 36 | 36 / 36 / 37 | 2,36 | 0,00% / 0,00% / 0,00% | **Atende** |
| **2. Referência** | 5 | 1 | 363 | 35 / 36 / 36 | 37 / 38 / 38 | 10,63 | 0,00% / 0,00% / 0,00% | **Atende** |
| **3. Carga nominal** | 20 | 2 | 1.351 | 36 / 36 / 36 | 40 / 41 / 40 | 39,56 | 0,00% / 0,00% / 0,00% | **Atende** |
| **4. Estresse 1** | 50 | 5 | 3.301 | 41 / 42 / 41 | 80 / 79 / 71 | 96,61 | 0,03% / 0,03% / 0,00% | **Atende** |
| **5. Estresse 2** | 100 | 10 | 5.711 | 120 / 120 / 120 | 140 / 140 / 140 | 167,36 | 28,25% / 28,37% / 28,01% | **Não atende** |
| **6. Recuperação** | 20 | 2 | 1.348 | 35 / 34 / 34 | 43 / 39 / 42 | 39,48 | 0,00% / 0,00% / 0,00% | **Atende** |

### 3.3 Projeto Anterior – Clínica Agenda (API Django REST)

| Patamar / Fase | Usuários (-u) | Ritmo (-r) | Reqs (média 3 reps) | p50 (ms) (r1 / r2 / r3) | p95 Geral (ms) (r1 / r2 / r3) | p95 Horários (ms) | Vazão req/s (média) | Falhas % (r1 / r2 / r3) | Decisão SLA |
|---|---:|---:|---:|---|---|---:|---:|---|---|
| **1. Carga nominal** | 20 | 4 | 432 | 9 / 9 / 9 | 48 / 40 / 43 | 22–28 | 17,94 | 0,00% / 0,00% / 0,00% | **Atende** |
| **2. Estresse** | 60 | 10 | 981 | 13 / 14 / 12 | 3.300 / 3.000 / 3.400 | 64–78 | 40,48 | 13,11% / 12,74% / 15,12% | **Não atende** |
| **3. Recuperação** | 20 | 4 | 439 | 9 / 10 / 9 | 36 / 27 / 67 | 23–25 | 18,22 | 0,00% / 0,00% / 0,00% | **Atende** |

---

## 4. Análise e Interpretação

### 4.1 Pacote A – Exemplo e Desafio de Matrícula
1. **Gargalo do Exemplo Resolvido A (`Sabor Express`):** O endpoint `GET /api/relatorio/vendas` é o gargalo claro do sistema. Enquanto `GET /api/cardapio` e `POST /api/pedidos` mantêm latência estável, o relatório de vendas possui um `threading.Lock()` global (`_lock_relatorio`) combinado com um `time.sleep(0.05 + 0.0002 * len(PEDIDOS))` que cresce linearmente conforme novos pedidos são criados. No estresse (250 usuários), o p95 do relatório saltou para **6.800 ms** (máximo de 8.428 ms).
2. **Atendimento ao SLA no Desafio A (`Matrícula Acadêmica`):** O SLA da coordenação **não foi atendido** em nenhum dos três perfis devido exclusivamente ao endpoint `GET /api/matriculas/<id>/comprovante`.
3. **Qual endpoint piora primeiro e por quê:** Os endpoints `GET /api/disciplinas` (p95 ~35 ms) e `POST /api/matriculas` (p95 ~65 ms) são extremamente rápidos e suportam 100 a 400 alunos com folga. Porém, `GET /api/matriculas/<id>/comprovante` serializa todas as requisições em uma trava global (`with _lock_pdf: time.sleep(0.25)`), simulando um gerador de PDF de instância única que só consegue produzir **4 comprovantes por segundo** ($1 / 0,25\text{s} = 4\text{ req/s}$). Quando 100 alunos pedem comprovante a uma taxa superior a 4 req/s, a fila cresce indefinidamente até atingir o timeout de 10.000 ms.
4. **Integridade das vagas e separação 409/422:** O uso de `_lock_vagas` no backend funcionou perfeitamente para proteger a seção crítica de decremento de vagas: em mais de 28.000 requisições somadas entre Carga, Pico e Estresse, **zero disciplinas ficaram com vagas negativas**. A separação entre `HTTP 409/422` e falhas técnicas no Locust evitou falsos positivos de erro quando as 230 vagas totais se esgotaram nos primeiros segundos do teste.

### 4.2 Pacote B – Consulta de Minicursos
1. **Consistência entre as 3 repetições:** As três repetições (`r1`, `r2`, `r3`) de cada patamar apresentaram variação inferior a 3% em vazão e p95 (ex.: na Carga Nominal de 20 usuários, p95 foi `40 ms`, `41 ms` e `40 ms`, com `0,00%` de falhas), comprovando alta reprodutibilidade experimental.
2. **Primeiro patamar que viola a meta:** Até **50 usuários** (`estresse50`), o sistema manteve p95 entre `71 ms` e `80 ms` e falhas em `0,03%` (1 falha em 3.310 requisições), ainda atendendo à meta (p95 ≤ 500 ms e falhas ≤ 1%). A violação ocorre de forma abrupta no patamar de **100 usuários (`estresse100`)**, onde a taxa de falhas salta para **28,01% a 28,37%**.
3. **Causa da saturação:** O servidor utiliza um semáforo limitado a 4 operações concorrentes (`CAP = threading.BoundedSemaphore(4)`) com timeout de aquisição de 100 ms (`CAP.acquire(timeout=0.10)`) e latência interna de 30 ms (`time.sleep(0.03)`). A capacidade máxima teórica do semáforo é de $\approx 4 / 0,03\text{s} = 133,3\text{ req/s}$. Com 50 usuários (~96,6 req/s), a fila aguarda menos de 100 ms; com 100 usuários (~167,4 req/s), a chegada supera a vazão máxima do semáforo e ~28% das requisições expiram os 100 ms de espera e recebem `HTTP 503 (Capacidade didática ocupada)`.
4. **Avaliação da Recuperação:** Ao reduzir a carga de 100 para 20 usuários (`recuperacao20`), o sistema voltou **imediatamente** (nos primeiros 5 segundos, muito abaixo do limite de 30 s) para `p95 = 39–43 ms` e `0,00%` de falhas, pois o estado em memória não sofre degradação residual após o esvaziamento das threads.

### 4.3 Projeto Anterior – Clínica Agenda (Django REST)
1. **Desempenho na Carga Nominal (20 usuários):** A API atendeu com folga à meta estipulada (p95 ≤ 600 ms e falhas ≤ 1%), registrando **p95 geral entre 40 ms e 48 ms**, mediana (`p50`) de **9 ms** e **0,00% de falhas** nas três repetições.
2. **Comportamento sob Estresse (60 usuários) e Identificação do Gargalo:** No patamar de 60 usuários com rampa agressiva (`r=10/s`), os endpoints de leitura (`GET /api/agendamentos/especialidades/`, `GET /api/agendamentos/horarios/?status=DISPONIVEL` e `GET /api/agendamentos/consultas/`) continuaram rápidos (`p95` entre `35 ms` e `78 ms`). O gargalo ocorreu no `POST /api/token/` durante o `on_start` simultâneo dos 60 usuários: como o Django utiliza por padrão o algoritmo criptográfico **PBKDF2-SHA256** (centenas de milhares de iterações de CPU por login para evitar ataques de força bruta), autenticar 60 usuários em 6 segundos saturou os 4 núcleos da CPU local, elevando o p95 agregado para `3.000–3.400 ms` e gerando timeouts de conexão (`~13%`).
3. **Recuperação:** Na fase de recuperação (`clinica_recuperacao20`), a API restabeleceu imediatamente `p95 = 27–67 ms` e `0,00%` de falhas.

---

## 5. Limitações e Recomendações

### Limitações do Estudo
1. **Gerador de carga e servidor na mesma máquina (`localhost`):** O Locust e os servidores Python/Django disputaram os mesmos 4 núcleos físicos de CPU e a mesma pilha de loopback do Windows 11.
2. **Servidores de desenvolvimento:** Os Pacotes A e B e o `runserver` do Django rodam em modo de desenvolvimento; em produção com Gunicorn/Uvicorn + PostgreSQL dedicado, o throughput de conexões concorrentes é significativamente superior.
3. **Massa de dados em memória / SQLite local:** Não reflete a latência de rede (RTT) de um ambiente distribuído em nuvem.

### Recomendações Técnicas de Melhoria
1. **Para o Desafio A (Matrícula Acadêmica):**
   - **Substituir o lock global `_lock_pdf` por geração assíncrona ou pool de workers:** A geração do comprovante PDF (`GET /api/matriculas/<id>/comprovante`) não deve usar um `threading.Lock()` global síncrono de 250 ms. Recomenda-se gerar o comprovante sob demanda em um pool de processos (ou fila Celery/RQ) e **fazer cache do comprovante gerado** (já que os dados da matrícula são imutáveis após a confirmação), reduzindo o tempo das consultas subsequentes de 250 ms para < 2 ms.
   - **Substituir o cálculo linear do relatório (`GET /api/relatorio/vendas`):** Manter um acumulador incremental de faturamento a cada `POST /api/pedidos` ou usar cache com TTL de 5 segundos em vez de recalcular toda a coleção sob lock global.
2. **Para o Desafio B (Portal de Minicursos):**
   - **Cache em memória para leitura de catálogo (`GET /api/cursos`):** Como a lista de cursos muda raramente, aplicar cache de leitura sem disputar o mesmo semáforo restrito (`BoundedSemaphore(4)`), reservando o controle de concorrência apenas para operações de escrita (`POST /api/inscricoes`).
3. **Para o Projeto Anterior (Clínica Agenda):**
   - **Reuso de sessão JWT e ajuste de workers ASGI/WSGI:** Evitar reautenticações repetidas no cliente mantendo o `access_token` em cache até próximo da expiração, e em produção executar o Django sob Gunicorn com múltiplos workers e cache Redis para as listagens públicas de especialidades e horários disponíveis.
