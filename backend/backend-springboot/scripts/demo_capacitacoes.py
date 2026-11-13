"""Demonstração HTTP local com dados fictícios; requer o Spring Boot iniciado."""
import json
import uuid
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8080"


def chamar(method, path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request = Request(BASE + path, data=data, method=method,
                      headers={"Content-Type": "application/json; charset=utf-8"})
    with urlopen(request, timeout=10) as response:
        return json.load(response)


def main():
    chamar("GET", "/api/health")
    # Fuso do laboratório em São Luís: UTC-03. A API usa America/Sao_Paulo.
    hoje = datetime.now(timezone(timedelta(hours=-3))).date()
    rodada = uuid.uuid4().hex[:8]
    for situacao in ("VALIDA", "VENCIDA", "AUSENTE", "NAO_VERIFICADA"):
        trabalhador = chamar("POST", "/api/trabalhadores", {
            "nome": f"Pessoa fictícia {situacao}",
            "matricula": f"COL-023-{rodada}-{situacao}",
            "empresa": "Empresa fictícia do laboratório",
        })
        caminho = f"/api/trabalhadores/{trabalhador['id']}/capacitacoes"
        if situacao != "AUSENTE":
            verificada = situacao != "NAO_VERIFICADA"
            chamar("POST", caminho, {
                "codigo": "DEMO-ZONA-A", "nome": "Capacitação fictícia para demonstração",
                "realizadaEm": (hoje - timedelta(days=30)).isoformat(),
                "validaAte": (hoje + timedelta(days=-1 if situacao == "VENCIDA" else 30)).isoformat(),
                "verificada": verificada, "fonte": "Simulação, sem certificado real",
                "verificadaPor": "OPERADOR-DEMO" if verificada else None,
            })
        resultado = chamar("GET", caminho + "/DEMO-ZONA-A/situacao")
        if resultado["situacao"] != situacao or resultado["autorizacaoAcesso"] != "NAO_AVALIADA":
            raise RuntimeError(f"Resultado inesperado: {resultado}")
        print(f"OK | {situacao} | trabalhador {trabalhador['id']} | acesso não avaliado")
    print("Quatro cenários conferidos. Não houve vídeo, ByteTrack ou liberação de acesso.")


if __name__ == "__main__":
    try:
        main()
    except HTTPError as exc:
        raise SystemExit(f"Erro HTTP {exc.code}: {exc.read().decode('utf-8')}") from exc
    except URLError as exc:
        raise SystemExit("Inicie o Spring Boot em 127.0.0.1:8080 antes da demonstração.") from exc
