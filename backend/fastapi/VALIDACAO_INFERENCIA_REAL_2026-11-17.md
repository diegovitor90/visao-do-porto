# Validação de inferência real — FastAPI + YOLO11

Data: 17/11/2026, America/Sao_Paulo. Código local priorizado.

## Inspeção e ambiente

Inspecionados: main.py, vision_detector.py, test_main.py, teste_pessoas.png e yolo11n.pt.
Único arquivo criado nesta validação: este Markdown. Nenhuma correção de código necessária.
Nenhum mock usado na requisição real. Testes unitários rápidos preservados.
API/OpenAPI: 0.3.0. Contrato: filename, width, height, status, inference_performed,
model, detections, message. Detecção tipada: class_id:int, class_name:str,
confidence:float, bbox com x1/y1/x2/y2:float.
Detector: YOLO11n, CPU, confiança mínima 0.40, classe 0/person, pesos sob demanda.

Windows, Python 3.11.9 da .venv. Versões por importlib.metadata.version:
fastapi 0.162.5; starlette 1.10.0; pydantic 2.14.3; pillow 13.0.0;
ultralytics 8.4.212; torch 2.15.0; torchvision 0.29.2; uvicorn 0.54.0;
pytest 9.2.0; python-multipart 0.0.33; httpx 0.28.1.

Integridade:
- teste_pessoas.png: 476023 bytes, PNG 767 × 766; PIL.Image.verify aprovado.
  SHA-256: ae72800496bfae8956fb91baa352e948a28150b958408169753e5723bc0bb18c.
- yolo11n.pt: 5613764 bytes, ZIP/PyTorch com 507 entradas; ZipFile.testzip aprovado.
  SHA-256: 0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1.
- Carregamento e execução reais confirmaram pesos utilizáveis. Hashes identificam
  os arquivos usados; não foram comparados com fonte externa de autenticidade.

## Comandos usados e reprodução

Na raiz, antes e depois da inferência:

```powershell
git status --short
& backend/fastapi/.venv/Scripts/python.exe --version
& backend/fastapi/.venv/Scripts/python.exe -m pytest backend/fastapi/test_main.py -q
```

Arquivos Python lidos com Get-Content. Hashes calculados com hashlib.sha256.
A consulta inicial com pip show teve erro Unicode cp1252 na saída; a consulta de
versões por importlib.metadata funcionou, sem alterar dependências.

Servidor iniciado em backend/fastapi, diretório dos pesos:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& .venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 18765
```

Em outro terminal, no mesmo diretório, executar o Python abaixo pela entrada padrão
de `.venv/Scripts/python.exe -` (PowerShell: here-string canalizada ao executável).
Esta é uma reprodução manual; não integra a suíte unitária.

```python
import httpx, json, time
with httpx.Client(base_url="http://127.0.0.1:18765", timeout=180, trust_env=False) as c:
    assert c.get("/openapi.json").json()["info"]["version"] == "0.3.0"
    print(c.get("/api/v1/vision/status").json())
    with open("teste_pessoas.png", "rb") as f:
        start = time.perf_counter()
        r = c.post("/api/v1/vision/analyze", files={"file": ("teste_pessoas.png", f, "image/png")})
        elapsed = time.perf_counter() - start
    print(r.status_code, elapsed, json.dumps(r.json(), ensure_ascii=False, indent=2))
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "COMPLETED" and d["inference_performed"] is True
    assert d["model"] == "yolo11n"
    assert (d["width"], d["height"]) == (767, 766)
    assert isinstance(d["detections"], list)
    for person in d["detections"]:
        assert person["class_id"] == 0 and person["class_name"] == "person"
        assert 0 <= person["confidence"] <= 1
        b = person["bbox"]
        assert 0 <= b["x1"] <= b["x2"] <= d["width"]
        assert 0 <= b["y1"] <= b["y2"] <= d["height"]
    print("Pessoas:", len(d["detections"]))
    print(c.get("/api/v1/vision/status").json())
```

## Resultado real

HTTP 200; 1 pessoa; duração aproximada 7.794 segundos na primeira requisição POST.
Tempo no cliente inclui carregamento inicial dos pesos e inferência; a importação
do detector já havia ocorrido no GET de status anterior.

```json
{
  "filename": "teste_pessoas.png",
  "width": 767,
  "height": 766,
  "status": "COMPLETED",
  "inference_performed": true,
  "model": "yolo11n",
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.8246,
      "bbox": {"x1": 37.02, "y1": 34.14, "x2": 731.36, "y2": 751.73}
    }
  ],
  "message": "Análise de imagem concluída."
}
```

Verificações de contrato, classe, confiança e limites das coordenadas aprovadas.
GET status antes: model_loaded=false, inference_available=true, status=READY.
GET status depois: model_loaded=true, inference_available=true, status=READY.
Servidor registrou HTTP 200 para OpenAPI, status, POST e status final.
Servidor de validação encerrado após execução.

## Regressão, erros e pendências

Antes: 17 passed, 1 warning in 1.78s.
Depois: 17 passed, 1 warning in 0.90s.
Aviso existente: StarletteDeprecationWarning sobre httpx/TestClient e futura adoção de httpx2.
Nenhum erro de inferência; nenhuma correção em código ou dependências.
Um erro de sintaxe PowerShell ao preparar este documento foi corrigido antes da gravação.
Nenhum arquivo não rastreado foi sobrescrito ou excluído. Nenhum comando Git de
alteração foi executado. Pesos e imagens não foram adicionados ao Git.

Limitações: uma imagem, uma requisição real, CPU local. Não comprova desempenho de
produção, concorrência ou precisão em dataset. Tempo e confiança podem variar.
O caminho dos pesos permanece relativo: iniciar o servidor em backend/fastapi.
Sem pendências para comprovar esta inferência. Avaliação ampla de desempenho/precisão
e atualização de dependências ficam fora deste escopo.
