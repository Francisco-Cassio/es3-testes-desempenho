"""
DESAFIO A - Trabalho 1: abertura da matrícula 2026.2 (Locust / Python)

Cenário: Às 19h a coordenação libera a matrícula e até 200 alunos entram no portal.
Endpoints testados:
  - GET  /api/disciplinas                  (peso 5 - 50%)
  - POST /api/matriculas                   (peso 3 - 30%)
  - GET  /api/matriculas/<id>/comprovante  (peso 2 - 20%)

Metas da coordenação (SLA no teste de carga - 100 alunos por 2 min):
  - p95 geral <= 800 ms
  - p95 do comprovante <= 1500 ms (1,5 s)
  - erros técnicos (5xx, timeout) < 1%
  - respostas 409 e 422 são regras de negócio válidas (não contam como falha técnica)
  - nunca pode haver vagas negativas em nenhuma disciplina
"""
import itertools
import os
import random
import threading

from locust import HttpUser, LoadTestShape, between, events, task

SLA_P95_GERAL_MS = 800
SLA_P95_COMPROVANTE_MS = 1500
SLA_ERRO_TECNICO_MAX = 0.01

_lock_aluno = threading.Lock()
_contador_alunos = itertools.count(1)

# Contadores separados para regras de negócio (409 e 422) e auditoria de integridade
CONTAGEM_NEGOCIO = {
    "201_matriculado": 0,
    "409_conflito_ou_vagas": 0,
    "422_regra_validacao": 0,
    "erros_tecnicos": 0,
    "vagas_negativas_detectadas": 0,
}

# Combinações válidas sem choque de horário (SEG-19h tem ES3 e RED, então nunca juntas)
GRADES_SEM_CHOQUE = [
    ["ES3", "BD2", "PW2"],
    ["RED", "IHC", "EMP"],
    ["ES3", "IHC", "EMP", "MOB"],
    ["BD2", "PW2", "IHC"],
    ["RED", "BD2", "EMP"],
    ["ES3", "BD2", "PW2", "IHC", "EMP"],
]


def proximo_aluno():
    """Garante um aluno distinto (20260001..20260200) para cada usuário virtual."""
    with _lock_aluno:
        idx = ((next(_contador_alunos) - 1) % 200) + 1
        return f"2026{idx:04d}"


class Aluno(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.matricula = proximo_aluno()
        self.id_matricula = None
        self.grade_escolhida = random.choice(GRADES_SEM_CHOQUE)

    @task(5)
    def consultar_oferta(self):
        with self.client.get(
            "/api/disciplinas",
            name="GET /api/disciplinas",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code != 200:
                CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                resp.failure(f"Erro técnico HTTP {resp.status_code}")
                return
            try:
                disciplinas = resp.json()
                if not isinstance(disciplinas, list) or len(disciplinas) == 0:
                    CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                    resp.failure("Lista de disciplinas vazia ou inválida")
                    return
                negativas = [d["codigo"] for d in disciplinas if d.get("vagas", 0) < 0]
                if negativas:
                    CONTAGEM_NEGOCIO["vagas_negativas_detectadas"] += 1
                    resp.failure(f"Integridade violada! Vagas negativas em: {negativas}")
                    return
                resp.success()
            except (ValueError, KeyError, TypeError) as exc:
                CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                resp.failure(f"JSON inválido: {exc}")

    @task(3)
    def realizar_matricula(self):
        payload = {
            "aluno": self.matricula,
            "disciplinas": self.grade_escolhida,
        }
        with self.client.post(
            "/api/matriculas",
            json=payload,
            name="POST /api/matriculas",
            catch_response=True,
            timeout=5,
        ) as resp:
            if resp.status_code == 201:
                try:
                    dados = resp.json()
                    if "id" not in dados or not str(dados.get("comprovante", "")).startswith("COMP-"):
                        CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                        resp.failure("Resposta 201 sem id ou comprovante válido")
                        return
                    self.id_matricula = dados["id"]
                    CONTAGEM_NEGOCIO["201_matriculado"] += 1
                    resp.success()
                except (ValueError, KeyError, TypeError) as exc:
                    CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                    resp.failure(f"JSON 201 inválido: {exc}")
            elif resp.status_code == 409:
                # Regra de negócio esperada: aluno já matriculado ou vagas esgotadas
                CONTAGEM_NEGOCIO["409_conflito_ou_vagas"] += 1
                resp.success()
            elif resp.status_code == 422:
                # Regra de negócio esperada: validação de grade/horário
                CONTAGEM_NEGOCIO["422_regra_validacao"] += 1
                resp.success()
            else:
                CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                resp.failure(f"Erro técnico HTTP {resp.status_code}")

    @task(2)
    def baixar_comprovante(self):
        # Caso este VU ainda não tenha obtido id próprio (ex.: vagas esgotadas),
        # consulta o comprovante #1 caso já exista matrícula no sistema
        alvo_id = self.id_matricula or 1
        with self.client.get(
            f"/api/matriculas/{alvo_id}/comprovante",
            name="GET /api/matriculas/[id]/comprovante",
            catch_response=True,
            timeout=10,
        ) as resp:
            if resp.status_code == 200:
                try:
                    dados = resp.json()
                    if not str(dados.get("comprovante", "")).startswith("COMP-"):
                        CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                        resp.failure("Comprovante retornado sem código COMP-")
                        return
                    resp.success()
                except (ValueError, KeyError, TypeError) as exc:
                    CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                    resp.failure(f"JSON comprovante inválido: {exc}")
            elif resp.status_code == 404 and self.id_matricula is None:
                # Antes da primeira matrícula do sistema existir, 404 para id=1 não é falha técnica
                resp.success()
            else:
                CONTAGEM_NEGOCIO["erros_tecnicos"] += 1
                resp.failure(f"Erro técnico comprovante HTTP {resp.status_code}")


class Perfil(LoadTestShape):
    """
    Perfis exigidos no Guia do Aluno (seção Desafio A):
      - carga    : 100 alunos por 2 minutos (120 s)
      - pico     : 0 -> 200 alunos em até 10 s (rampa de 20/s, sustenta até 60 s, reduz para 20 até 90 s)
      - estresse : degraus de +50 alunos a cada 25 s até 400 alunos (50, 100, 150, ..., 400)
    """
    tipo = os.getenv("TIPO_TESTE", "carga")

    def tick(self):
        t = self.get_run_time()
        if self.tipo == "carga":
            return (100, 20) if t < 120 else None

        if self.tipo == "pico":
            if t < 15:
                return (10, 10)
            if t < 60:
                # Salto brusco até 200 alunos em menos de 10 segundos (taxa 40/s)
                return (200, 40)
            if t < 90:
                return (20, 40)
            return None

        if self.tipo == "estresse":
            degrau = int(t // 25) + 1
            usuarios = 50 * degrau
            return (usuarios, 25) if usuarios <= 400 else None

        raise ValueError(f"TIPO_TESTE inválido: {self.tipo}")


@events.quitting.add_listener
def relatorio_sla_matricula(environment, **_):
    total = environment.stats.total
    if total.num_requests == 0:
        return

    p95_geral = total.get_response_time_percentile(0.95)
    taxa_erro = total.fail_ratio

    ep_comp = environment.stats.entries.get(("GET /api/matriculas/[id]/comprovante", "GET"))
    p95_comp = ep_comp.get_response_time_percentile(0.95) if (ep_comp and ep_comp.num_requests) else 0

    print("\n" + "=" * 68)
    print(f"[RESUMO MATRÍCULA - PERFIL: {os.getenv('TIPO_TESTE', 'carga').upper()}]")
    print(f"  p95 Geral       : {p95_geral:.0f} ms (meta <= {SLA_P95_GERAL_MS} ms)")
    print(f"  p95 Comprovante : {p95_comp:.0f} ms (meta <= {SLA_P95_COMPROVANTE_MS} ms)")
    print(f"  Erros Técnicos  : {taxa_erro:.2%} (meta < {SLA_ERRO_TECNICO_MAX:.0%})")
    print(f"  Contagem Negócio: 201={CONTAGEM_NEGOCIO['201_matriculado']} | "
          f"409={CONTAGEM_NEGOCIO['409_conflito_ou_vagas']} | "
          f"422={CONTAGEM_NEGOCIO['422_regra_validacao']} | "
          f"Vagas Negativas={CONTAGEM_NEGOCIO['vagas_negativas_detectadas']}")

    atendeu = (
        p95_geral <= SLA_P95_GERAL_MS
        and p95_comp <= SLA_P95_COMPROVANTE_MS
        and taxa_erro < SLA_ERRO_TECNICO_MAX
        and CONTAGEM_NEGOCIO["vagas_negativas_detectadas"] == 0
    )
    print("  Resultado SLA   :", "ATENDE" if atendeu else "VIOLA SLA")
    print("=" * 68)
