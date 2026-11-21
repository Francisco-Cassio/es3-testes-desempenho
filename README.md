# Trabalho 1 – Testes de Desempenho (Engenharia de Software III)

Repositório com os planos, scripts e resultados dos testes de desempenho (carga, estresse, pico e recuperação) utilizando **Locust** em **Python**.

## Equipe
- **Francisco de Cássio da Silva Mourão Júnior**
- **Álvaro Miguel Rodrigues Aquino Costa**

## Versões Utilizadas
- **Python:** `3.12.10`
- **Locust:** `2.47.0`
- **Flask:** `3.1.3` (Pacote A)
- **Django / DRF:** `Django 6.1`, `djangorestframework 3.18.0`, `djangorestframework_simplejwt 5.5.1` (Projeto Anterior)

## Estrutura do Repositório

```text
.
├── README.md
├── plano_relatorio_desempenho.md      # Plano de testes, tabelas e análise completa
├── relatorio.pdf                      # Relatório final em PDF (4 páginas)
├── slides.pdf                         # Slides da apresentação da equipe
├── pacote-A/
│   ├── app/app.py                     # Sistema A (Sabor Express + Matrícula Acadêmica)
│   ├── exemplo/locustfile.py          # Exemplo resolvido A: Semana do Cliente
│   └── desafio/locustfile_matricula.py# Desafio A: Abertura da Matrícula (Carga, Pico e Estresse)
├── pacote-B/
│   ├── app.py                         # Sistema B (Biblioteca Acadêmica + Minicursos)
│   ├── exemplo/locustfile.py          # Exemplo resolvido B: Catálogo da Biblioteca
│   └── desafio/desafio_locust.py      # Desafio B: Consulta de Minicursos (70% lista / 30% detalhe)
├── projeto-anterior/
│   ├── backend/                       # Código da API Django REST (Clínica Agenda)
│   ├── seed_clinica.py                # Popula o banco local da Clínica Agenda
│   ├── run_server_clinica.py          # Inicia a API da Clínica Agenda em 127.0.0.1:8001
│   └── locustfile_clinica.py          # Suíte Locust da Clínica Agenda
└── resultados/
    ├── registro_resultados_desempenho.csv
    ├── pacote-A/                      # CSVs e HTMLs do Exemplo A e Desafio A
    ├── pacote-B/                      # CSVs e HTMLs do Exemplo B e das 18 execuções do Desafio B
    └── projeto-anterior/              # CSVs e HTMLs das 9 execuções da Clínica Agenda
```

---

## 1. Preparação do Ambiente

Clone o repositório, crie o ambiente virtual e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS / Git Bash
# .venv\Scripts\Activate.ps1     # Windows PowerShell

python -m pip install flask locust requests -r projeto-anterior/backend/requirements.txt
```

---

## 2. Pacote A – Sabor Express e Matrícula Acadêmica

### Subir o sistema A (Terminal 1)
```bash
python pacote-A/app/app.py
# Servidor disponível em http://127.0.0.1:5000
```

### Rodar o Exemplo Resolvido A – Semana do Cliente (Terminal 2)
```bash
curl -X POST http://127.0.0.1:5000/api/admin/reset
TIPO_TESTE=carga locust -f pacote-A/exemplo/locustfile.py --host http://127.0.0.1:5000 --headless --csv resultados/pacote-A/exemplo/carga --html resultados/pacote-A/exemplo/carga.html

curl -X POST http://127.0.0.1:5000/api/admin/reset
TIPO_TESTE=estresse locust -f pacote-A/exemplo/locustfile.py --host http://127.0.0.1:5000 --headless --csv resultados/pacote-A/exemplo/estresse --html resultados/pacote-A/exemplo/estresse.html
```
*(No Windows PowerShell, defina a variável antes do comando: `$env:TIPO_TESTE="carga"; locust -f ...`)*

### Rodar o Desafio A – Abertura da Matrícula (`carga`, `pico` e `estresse`)
```bash
# 1. Teste de Carga (100 alunos por 2 min)
curl -X POST http://127.0.0.1:5000/api/admin/reset
TIPO_TESTE=carga locust -f pacote-A/desafio/locustfile_matricula.py --host http://127.0.0.1:5000 --headless --csv resultados/pacote-A/desafio/carga --html resultados/pacote-A/desafio/carga.html

# 2. Teste de Pico (0 -> 200 alunos em até 10 s)
curl -X POST http://127.0.0.1:5000/api/admin/reset
TIPO_TESTE=pico locust -f pacote-A/desafio/locustfile_matricula.py --host http://127.0.0.1:5000 --headless --csv resultados/pacote-A/desafio/pico --html resultados/pacote-A/desafio/pico.html

# 3. Teste de Estresse (degraus até 400 alunos)
curl -X POST http://127.0.0.1:5000/api/admin/reset
TIPO_TESTE=estresse locust -f pacote-A/desafio/locustfile_matricula.py --host http://127.0.0.1:5000 --headless --csv resultados/pacote-A/desafio/estresse --html resultados/pacote-A/desafio/estresse.html
```

---

## 3. Pacote B – Biblioteca e Minicursos

### Subir o sistema B (Terminal 1)
```bash
python pacote-B/app.py
# Servidor disponível em http://127.0.0.1:8000
```

### Rodar o Exemplo Resolvido B – Catálogo da Biblioteca (Terminal 2)
```bash
python -m locust -f pacote-B/exemplo/locustfile.py --host http://127.0.0.1:8000 --headless -u 20 -r 2 -t 90s --stop-timeout 5s --csv resultados/pacote-B/exemplo/carga20_r1 --html resultados/pacote-B/exemplo/carga20_r1.html
```

### Rodar o Desafio B – Consulta de Minicursos (6 fases x 3 repetições)
```bash
# Fase 1: Verificação inicial (1 usuário, r=1, 15s)
python -m locust -f pacote-B/desafio/desafio_locust.py --host http://127.0.0.1:8000 --headless -u 1 -r 1 -t 15s --stop-timeout 5s --csv resultados/pacote-B/desafio/verificacao1_r1 --html resultados/pacote-B/desafio/verificacao1_r1.html

# Fase 2: Referência (5 usuários, r=1, 90s)
python -m locust -f pacote-B/desafio/desafio_locust.py --host http://127.0.0.1:8000 --headless -u 5 -r 1 -t 90s --stop-timeout 5s --csv resultados/pacote-B/desafio/referencia5_r1 --html resultados/pacote-B/desafio/referencia5_r1.html

# Fase 3: Carga nominal (20 usuários, r=2, 90s)
python -m locust -f pacote-B/desafio/desafio_locust.py --host http://127.0.0.1:8000 --headless -u 20 -r 2 -t 90s --stop-timeout 5s --csv resultados/pacote-B/desafio/carga20_r1 --html resultados/pacote-B/desafio/carga20_r1.html

# Fase 4: Estresse 1 (50 usuários, r=5, 90s)
python -m locust -f pacote-B/desafio/desafio_locust.py --host http://127.0.0.1:8000 --headless -u 50 -r 5 -t 90s --stop-timeout 5s --csv resultados/pacote-B/desafio/estresse50_r1 --html resultados/pacote-B/desafio/estresse50_r1.html

# Fase 5: Estresse 2 (100 usuários, r=10, 90s)
python -m locust -f pacote-B/desafio/desafio_locust.py --host http://127.0.0.1:8000 --headless -u 100 -r 10 -t 90s --stop-timeout 5s --csv resultados/pacote-B/desafio/estresse100_r1 --html resultados/pacote-B/desafio/estresse100_r1.html

# Fase 6: Recuperação (20 usuários, r=2, 90s)
python -m locust -f pacote-B/desafio/desafio_locust.py --host http://127.0.0.1:8000 --headless -u 20 -r 2 -t 90s --stop-timeout 5s --csv resultados/pacote-B/desafio/recuperacao20_r1 --html resultados/pacote-B/desafio/recuperacao20_r1.html
```
*(Repita cada patamar alterando o sufixo `_r1`, `_r2` e `_r3` conforme os arquivos salvos em `resultados/pacote-B/desafio/`).*

---

## 4. Projeto Anterior – Clínica Agenda (API Django REST)

### Popular o banco local e subir o servidor (Terminal 1)
```bash
python projeto-anterior/seed_clinica.py
python projeto-anterior/run_server_clinica.py
# API disponível em http://127.0.0.1:8001/api/docs/
```

### Rodar os patamares de Carga, Estresse e Recuperação (Terminal 2)
```bash
# Carga Nominal (20 usuários, r=4)
python -m locust -f projeto-anterior/locustfile_clinica.py --host http://127.0.0.1:8001 --headless -u 20 -r 4 -t 45s --stop-timeout 5s --csv resultados/projeto-anterior/clinica_carga20_r1 --html resultados/projeto-anterior/clinica_carga20_r1.html

# Estresse (60 usuários, r=10)
python -m locust -f projeto-anterior/locustfile_clinica.py --host http://127.0.0.1:8001 --headless -u 60 -r 10 -t 45s --stop-timeout 5s --csv resultados/projeto-anterior/clinica_estresse60_r1 --html resultados/projeto-anterior/clinica_estresse60_r1.html

# Recuperação (20 usuários, r=4)
python -m locust -f projeto-anterior/locustfile_clinica.py --host http://127.0.0.1:8001 --headless -u 20 -r 4 -t 45s --stop-timeout 5s --csv resultados/projeto-anterior/clinica_recuperacao20_r1 --html resultados/projeto-anterior/clinica_recuperacao20_r1.html
```
