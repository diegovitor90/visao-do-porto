# Roteiro de testes manuais no Windows

Use o Windows PowerShell e mídias autorizadas para teste. As saídas vão para
uma pasta ignorada pelo Git. O [README](../README.md) orienta a instalação e os
pesos. Ajuste $Repo em cada terminal se o projeto estiver em outro diretório.

## 1. Iniciar os serviços

**Terminal A, Spring Boot**

```powershell
$Repo = Join-Path $env:USERPROFILE 'OneDrive\Desktop\visao-do-porto\visao-do-porto'
Set-Location -LiteralPath (Join-Path $Repo 'backend\backend-springboot')
.\mvnw.cmd spring-boot:run
```

**Terminais B e C, FastAPI e teste**. Execute este bloco nos dois terminais.

```powershell
$Repo = Join-Path $env:USERPROFILE 'OneDrive\Desktop\visao-do-porto\visao-do-porto'
Set-Location -LiteralPath (Join-Path $Repo 'backend\fastapi')
$Python = (Resolve-Path -LiteralPath '.\.venv\Scripts\python.exe').Path
$Dados = Join-Path (Get-Location) 'avaliacao_saida\roteiro'
New-Item -ItemType Directory -Path $Dados -Force | Out-Null
$env:VISION_EVIDENCE_DIR = Join-Path $Dados 'evidencias'
$env:VISION_EVENTS_FILE = Join-Path $Dados 'eventos_locais.jsonl'
$env:VISION_EVENT_QUEUE = Join-Path $Dados 'eventos.sqlite3'
$env:VISION_ZONES_CACHE = Join-Path $Dados 'zonas_cache'
$Fast = 'http://127.0.0.1:8000'
$Spring = 'http://127.0.0.1:8080'
$PesoEpi = Join-Path (Get-Location) 'models\best_epi_grupo_yolo26s.pt'
```

**Só no terminal B**, inicie a API e deixe o terminal aberto.

```powershell
& $Python -m uvicorn main:app --host 127.0.0.1 --port 8000 --timeout-graceful-shutdown 10
```

**Terminal C**, confira os três HTTP 200.

```powershell
Invoke-RestMethod "$Fast/api/health"
Invoke-RestMethod "$Spring/api/health"
Invoke-RestMethod "$Spring/api/v1/vision/status"
```

## 2. Pessoas, EPIs e encaminhamento de imagem ao Spring

**Terminal C, backend/fastapi**. A detecção de pessoas usa a foto de exemplo
instalada com o Ultralytics. No teste de EPI, informe uma foto JPEG ou PNG de
uma pessoa com equipamentos visíveis.

```powershell
$Pessoa = (Resolve-Path -LiteralPath '.\.venv\Lib\site-packages\ultralytics\assets\bus.jpg').Path
$Epi = (Resolve-Path -LiteralPath ((Read-Host 'Caminho da foto de EPI').Trim('"'))).Path
$MimeEpi = if ([IO.Path]::GetExtension($Epi) -ieq '.png') { 'image/png' } else { 'image/jpeg' }

$pessoas = curl.exe --fail -sS -F "file=@$Pessoa;type=image/jpeg" "$Fast/api/v1/vision/analyze" | ConvertFrom-Json
$pessoas | Select-Object filename, model, status, inference_performed
$pessoas.detections | Format-Table class_name, confidence

$EpiDireto = Join-Path $Dados 'epi-fastapi.json'
$EpiSpring = Join-Path $Dados 'epi-spring.json'
curl.exe --fail -sS -F "file=@$Epi;type=$MimeEpi" "$Fast/api/v1/vision/analyze/ppe" --output $EpiDireto
if ($LASTEXITCODE -ne 0) { throw 'Falha na detecção direta de EPIs.' }
curl.exe --fail -sS -F "file=@$Epi;type=$MimeEpi" "$Spring/api/v1/vision/analyze/ppe" --output $EpiSpring
if ($LASTEXITCODE -ne 0) { throw 'Falha no encaminhamento de EPIs pelo Spring.' }
$epis = Get-Content -Raw -LiteralPath $EpiDireto -Encoding UTF8 | ConvertFrom-Json
$epis | Select-Object filename, model, status, inference_performed
$epis.detections | Format-Table class_name, confidence
& $Python -c "from pathlib import Path; import json,sys; print(json.loads(Path(sys.argv[1]).read_bytes()) == json.loads(Path(sys.argv[2]).read_bytes()))" $EpiDireto $EpiSpring
```

Espere **COMPLETED** e detecções **person** na primeira foto. Na segunda,
observe as classes que o modelo encontra, como **helmet** e **vest**.
Uma lista vazia pode vir com HTTP 200. A comparação direta e via Spring
deve retornar **True**.

## 3. Vídeo e ByteTrack

**Terminal C, backend/fastapi**. Selecione um MP4 com a pessoa visível de corpo
inteiro. Para conferir EPI, prefira dez segundos ou mais com câmera fixa e
trechos de uso de EPI, ausência visível e oclusão.

```powershell
$Video = (Resolve-Path -LiteralPath ((Read-Host 'Caminho do vídeo MP4').Trim('"'))).Path
$SemModelo = Join-Path $Dados '01-video.mp4'
$ComTrack = Join-Path $Dados '02-bytetrack.mp4'
& $Python -m vision.cli --source $Video --sem-descarte --saida $SemModelo
& $Python -m vision.cli --source $Video --sem-descarte --track --saida $ComTrack
Invoke-Item -LiteralPath $ComTrack
```

Espere contagem de quadros, FPS, mediana, p95 e zero descartes.
No segundo vídeo, procure o ID junto da caixa e confira sua continuidade
enquanto a pessoa permanece visível. Repita o comando de tracking para observar
a mudança de **session_id**.

## 4. Cadastro de zonas, associação e estados

**Terminal C, backend/fastapi**. Os polígonos amplos facilitam o teste.
Ao cadastrar zonas reais, desenhe sobre o chão e ajuste os vértices ao ponto
dos pés.

```powershell
$Camera = 'MANUAL-' + (Get-Date -Format 'yyyyMMddHHmmss')
$Poligono = @(@(0.01,0.01), @(0.99,0.01), @(0.99,0.98), @(0.01,0.98))
$Zonas = @(
    @{ nome='EPIs do roteiro'; polygon=$Poligono; required_ppe=@('CAPACETE','COLETE'); rule_type='EPI_OBRIGATORIO'; rule_id='EPI-MANUAL' },
    @{ nome='Area restrita do roteiro'; polygon=$Poligono; required_ppe=@(); rule_type='AREA_RESTRITA'; rule_id='RESTRITA-MANUAL' }
)
$JsonZonas = ConvertTo-Json -InputObject $Zonas -Depth 8
Invoke-RestMethod "$Spring/api/v1/cameras/$Camera/zonas" -Method Put -ContentType 'application/json; charset=utf-8' -Body $JsonZonas
Invoke-RestMethod "$Spring/api/v1/cameras/$Camera/zonas" | Format-Table zone_id, nome, rule_type, rule_version

$Avaliacao = Join-Path $Dados $Camera
$Anotado = Join-Path $Dados "$Camera-anotado.mp4"
& $Python -m vision.cli --source $Video --camera $Camera --spring --epi $PesoEpi --sem-descarte --avaliacao $Avaliacao --saida $Anotado
Invoke-Item -LiteralPath $Anotado
Import-Csv -LiteralPath (Join-Path $Avaliacao 'observacoes.csv') |
    Group-Object track_id, item, estado | Sort-Object Name | Format-Table Name, Count
```

O GET deve listar duas zonas com **rule_version** 1. No vídeo, confira os
polígonos e os estados sobre cada pessoa. No CSV, compare capacete e colete
para cada track. **CONFORME** exige sinal positivo consistente.
**NAO_CONFORME** exige sinal negativo consistente. Sinais ausentes,
contraditórios ou de qualidade insuficiente podem manter **INDETERMINADO**.
O modelo pode ficar indeterminado mesmo quando você retira um equipamento.

Para conferir os três estados e a atribuição de cada EPI a no máximo uma
pessoa com entradas controladas, rode estes testes no mesmo terminal:

```powershell
& $Python -m pytest -v test_association.py test_state.py test_zones.py test_rules.py
```

## 5. Eventos, revisão e evidências

**Terminal C, backend/fastapi**. O publicador é assíncrono.

```powershell
$Eventos = @()
for ($tentativa = 0; $tentativa -lt 10; $tentativa++) {
    $Eventos = @((Invoke-RestMethod "$Spring/api/v1/eventos?camera_id=$Camera"))
    if ($Eventos.Count -gt 0) { break }
    Start-Sleep -Seconds 1
}
$Eventos | Format-Table event_type, track_id, review_status, evidence_ref

$ComEvidencia = $Eventos | Where-Object { $_.evidence_ref } | Select-Object -First 1
if (-not $ComEvidencia) { throw 'Sem evidência. Confira os pés no polígono e pelo menos cinco quadros dentro.' }
$Id = $ComEvidencia.event_id
$Jpeg = Join-Path $Dados $ComEvidencia.evidence_ref
Invoke-WebRequest "$Fast/api/v1/evidencias/$($ComEvidencia.evidence_ref)" -UseBasicParsing -OutFile $Jpeg
Invoke-Item -LiteralPath $Jpeg

$Revisao = @{ status='CONFIRMADO' } | ConvertTo-Json
Invoke-RestMethod "$Spring/api/v1/eventos/$Id/revisao" -Method Patch -ContentType 'application/json' -Body $Revisao
Invoke-RestMethod "$Spring/api/v1/eventos/$Id" | Select-Object event_id, review_status, reviewed_at
curl.exe -sS -o NUL -w '%{http_code}\n' "$Fast/api/v1/evidencias/..%5Cfora.jpg"
```

Espere uma **INTRUSAO** por condição contínua de cada track na zona restrita.
**EPI_AUSENTE** exige estado negativo confirmado. **EPI_INDETERMINADO**
exige mais de cinco segundos contínuos nesse estado dentro da zona.
Confira o JPEG anotado, o status **CONFIRMADO** e o HTTP 404 da última chamada.

## 6. Webcam do computador

**Terminal C, backend/fastapi**. Feche outros aplicativos que usam a webcam.
Aponte a câmera para a cena de teste e enquadre o corpo inteiro. Altere
**webcam_index** se o dispositivo estiver em outro índice.

```powershell
$Config = @{ camera_id=$Camera; source='WEBCAM'; webcam_index=0 } | ConvertTo-Json
$Fonte = Invoke-RestMethod "$Fast/api/v1/sources" -Method Post -ContentType 'application/json' -Body $Config
$FonteId = $Fonte.id
$Mjpeg = Join-Path $Dados 'webcam.mjpeg'
$Quadro = Join-Path $Dados 'webcam-quadro.jpg'
try {
    for ($tentativa = 0; $tentativa -lt 15; $tentativa++) {
        $Estado = (Invoke-RestMethod "$Fast/api/v1/vision/status").sources |
            Where-Object { $_.id -eq $FonteId }
        if ($Estado.status -eq 'ATIVA') { break }
        Start-Sleep -Seconds 1
    }
    $Estado | Format-List id, status, session_id, fps, quadros, descartados
    if ($Estado.status -ne 'ATIVA') { throw 'Confira o índice, as permissões do Windows e outros aplicativos que usam a webcam.' }

    curl.exe --fail -sS --max-time 12 --output $Mjpeg "$Fast/api/v1/sources/$FonteId/stream"
    if ($LASTEXITCODE -notin @(0,28)) { throw 'Falha HTTP ou de conexão ao capturar o stream.' }
    & $Python -c "from pathlib import Path; import sys; data=Path(sys.argv[1]).read_bytes(); i=data.index(bytes.fromhex('ffd8')); j=data.index(bytes.fromhex('ffd9'),i)+2; Path(sys.argv[2]).write_bytes(data[i:j])" $Mjpeg $Quadro
    if ($LASTEXITCODE -ne 0) { throw 'Nenhum JPEG completo encontrado no stream.' }
    Invoke-Item -LiteralPath $Quadro
} finally {
    Invoke-RestMethod "$Fast/api/v1/sources/$FonteId" -Method Delete
}
(Invoke-RestMethod "$Fast/api/v1/vision/status").sources | Where-Object { $_.id -eq $FonteId }
```

Espere **ATIVA**, sessão preenchida, FPS positivo e um JPEG extraído do
stream. O limite de 12 segundos pode encerrar o curl com código 28. Depois do
DELETE, a última consulta deve retornar vazia para aquele ID. Se a pessoa
permaneceu na zona, repita a listagem do passo 5 e procure **source = WEBCAM**.

O Spring usa H2 em memória. Ao reiniciar, cadastre novamente as zonas
necessárias. Os arquivos do roteiro ficam na pasta $Dados.
