"""
Trabalho 1 - Projeto Anterior: Clínica Agenda (API Django REST)

Endpoints avaliados:
  - GET  /api/agendamentos/especialidades/          (peso 7 - 35%)
  - GET  /api/agendamentos/horarios/?status=DISPONIVEL (peso 7 - 35%)
  - GET  /api/usuarios/especialistas/               (peso 3 - 15%)
  - GET  /api/agendamentos/consultas/ (com JWT)     (peso 3 - 15%)

Metas (SLA definidas pela equipe para a carga nominal de 20 usuários):
  - p95 <= 600 ms
  - falhas técnicas <= 1%
  - Recuperação para p95 <= 600 ms após o patamar de estresse (60 usuários)
"""
import itertools
import threading
from locust import HttpUser, between, task

_lock_usr = threading.Lock()
_seq_usr = itertools.count(1)


def proximo_paciente():
    with _lock_usr:
        idx = ((next(_seq_usr) - 1) % 30) + 1
        return f"paciente{idx:02d}", "SenhaForte123!"


class UsuarioClinicaAgenda(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.username, self.password = proximo_paciente()
        self.token = None
        with self.client.post(
            "/api/token/",
            json={"username": self.username, "password": self.password},
            name="POST /api/token/",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Falha login JWT HTTP {resp.status_code}")
                return
            try:
                dados = resp.json()
                if "access" not in dados:
                    resp.failure("Token JWT ausente na resposta")
                    return
                self.token = dados["access"]
                resp.success()
            except (ValueError, KeyError, TypeError):
                resp.failure("JSON inválido em POST /api/token/")

    @task(7)
    def listar_especialidades(self):
        with self.client.get(
            "/api/agendamentos/especialidades/",
            name="GET /api/agendamentos/especialidades/",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            try:
                dados = resp.json()
                resultados = dados.get("results", [])
                nomes = [e.get("nome_especialidade") for e in resultados if isinstance(e, dict)]
                if dados.get("count", 0) < 3 or "Cardiologia" not in nomes:
                    resp.failure("Catálogo de especialidades incompleto")
                    return
                resp.success()
            except (ValueError, KeyError, TypeError):
                resp.failure("JSON inválido em especialidades")

    @task(7)
    def consultar_horarios_disponiveis(self):
        with self.client.get(
            "/api/agendamentos/horarios/?status=DISPONIVEL",
            name="GET /api/agendamentos/horarios/?status=DISPONIVEL",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            try:
                dados = resp.json()
                if "count" not in dados or not isinstance(dados.get("results"), list) or dados["count"] < 1:
                    resp.failure("Lista de horários disponíveis vazia ou inválida")
                    return
                resp.success()
            except (ValueError, KeyError, TypeError):
                resp.failure("JSON inválido em horários")

    @task(3)
    def listar_especialistas(self):
        with self.client.get(
            "/api/usuarios/especialistas/",
            name="GET /api/usuarios/especialistas/",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            try:
                dados = resp.json()
                if dados.get("count", 0) < 1 or not dados.get("results"):
                    resp.failure("Nenhum especialista retornado")
                    return
                resp.success()
            except (ValueError, KeyError, TypeError):
                resp.failure("JSON inválido em especialistas")

    @task(3)
    def consultar_minhas_consultas(self):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        with self.client.get(
            "/api/agendamentos/consultas/",
            headers=headers,
            name="GET /api/agendamentos/consultas/",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            try:
                dados = resp.json()
                if "count" not in dados or not isinstance(dados.get("results"), list):
                    resp.failure("Estrutura paginada inválida em consultas")
                    return
                resp.success()
            except (ValueError, KeyError, TypeError):
                resp.failure("JSON inválido em consultas")
