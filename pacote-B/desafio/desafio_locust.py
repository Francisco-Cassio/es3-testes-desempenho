"""
DESAFIO B - Trabalho 1: Consulta de minicursos (Locust / Python)

Mistura exigida pelo Guia do Aluno:
  - GET /api/cursos   : 70% (peso 7) -> HTTP 200, total == 3 e presença de um curso esperado ('Python')
  - GET /api/cursos/1 : 30% (peso 3) -> HTTP 200, id == 1, nome == 'Python' e vagas == 2

Metas:
  - Com 20 usuários (carga nominal): p95 <= 500 ms e falhas <= 1%
  - Recuperação: após o estresse, voltar a p95 <= 500 ms e falhas <= 1% em até 30 s com 20 usuários
"""
from locust import HttpUser, between, task


class Visitante(HttpUser):
    wait_time = between(0.2, 0.6)

    @task(7)
    def listar_cursos(self):
        with self.client.get(
            "/api/cursos",
            name="GET /api/cursos",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            try:
                dados = resp.json()
                itens = dados.get("itens", [])
                nomes = [c.get("nome") for c in itens if isinstance(c, dict)]
                if dados.get("total") != 3 or "Python" not in nomes:
                    resp.failure("Conteúdo inválido em GET /api/cursos")
                    return
                resp.success()
            except (ValueError, KeyError, TypeError, AttributeError):
                resp.failure("JSON inválido em GET /api/cursos")

    @task(3)
    def detalhe_curso_python(self):
        with self.client.get(
            "/api/cursos/1",
            name="GET /api/cursos/1",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            try:
                dados = resp.json()
                if (
                    dados.get("id") != 1
                    or dados.get("nome") != "Python"
                    or dados.get("vagas") != 2
                ):
                    resp.failure("Conteúdo inválido em GET /api/cursos/1")
                    return
                resp.success()
            except (ValueError, KeyError, TypeError, AttributeError):
                resp.failure("JSON inválido em GET /api/cursos/1")
