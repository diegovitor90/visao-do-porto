# Avaliação de visão computacional

## Vídeos públicos

Execução em 24/11/2026 no workspace da branch `feat/vc-implementacao-local`,
a partir de `65c5f23`. Windows 11 Home build 26200, Intel Core i7-1165G7,
Python 3.12.7, Ultralytics 8.4.212, Torch 2.15.0, OpenCV 5.0.0.93, NumPy 2.4.6
e lap 0.5.12. Foram usados os três primeiros segundos de cada vídeo,
redimensionados proporcionalmente para 640 px no lado maior. Execução em CPU
com `--sem-descarte`, vídeo anotado, sem zonas ou envio HTTP e limiar de
EPI 0,40. A latência vai da leitura à gravação do quadro anotado. O FPS
inclui a carga inicial dos modelos nesta execução curta.

| Vídeo | Configuração | Resolução | Quadros | FPS | Mediana (ms) | p95 (ms) | Descartados |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| [Construction Workers Walking at the Construction Site](https://www.pexels.com/video/construction-workers-walking-at-the-construction-site-8965526/), Mikael Blomkvist | YOLO11n + ByteTrack | 360×640 | 75 | 6,7632 | 117,8140 | 183,9339 | 0 |
| Mesmo vídeo | YOLO11n + ByteTrack + YOLO26s | 360×640 | 75 | 3,8794 | 395,4508 | 495,7065 | 0 |
| [Workers Walking in Construction Site](https://www.pexels.com/video/workers-walking-in-construction-site-5434223/), Everett Bumstead | YOLO11n + ByteTrack + YOLO26s | 640×360 | 72 | 4,4329 | 306,2836 | 383,3464 | 0 |

As mídias usam a [licença da Pexels](https://www.pexels.com/license/) e ficaram
em pasta temporária. O YOLO26n fica como opção futura. Rótulos manuais
para acerto de estado, precisão e recall de eventos ainda estão pendentes.
As medições são exploratórias: não representam desempenho sustentado em fontes
ao vivo, múltiplas câmeras ou ambiente portuário. As métricas de detecção do
modelo de EPI não substituem as métricas de qualidade de eventos do pipeline.

## Laboratório

| Item | Estado |
| --- | --- |
| Hardware e câmera, resolução, distância, posição | A definir com o laboratório |
| Rótulos, FPS, latência, acerto de estado, alertas e reconexão | Avaliação pendente |
| Metas de aceitação | A definir (#2) |
| Calibração | Valores iniciais de `vision/config.py`. Rodar uma alteração por vez e registrar antes/depois com os mesmos clipes |

## Exportar e medir

A partir de `backend/fastapi`, processe cada clipe com as mesmas zonas que
serão usadas nos rótulos. O CLI exporta `execucao.json`, `observacoes.csv`
e `eventos.csv`. Use a pasta ignorada `avaliacao_saida/` ou uma pasta externa.

```powershell
.\.venv\Scripts\python.exe -m vision.cli --source C:/clips/obra.mp4 --epi models/best_epi_grupo_yolo26s.pt --zonas zonas/CAM-LAB-01.exemplo.json --sem-descarte --avaliacao avaliacao_saida/obra
.\.venv\Scripts\python.exe -m avaliacao.medir --execucao avaliacao_saida/obra --rotulos C:/clips/estados.csv --rotulos-eventos C:/clips/eventos-reais.csv
.\.venv\Scripts\python.exe -m avaliacao.reconexao --fonte UUID-DA-FONTE --duracao 60
```

Rótulos de estado em CSV com cabeçalho
`clip,frame_inicio,frame_fim,track_id,item,estado_real`. Use o nome do arquivo
com extensão em `clip`, numeração a partir de zero, intervalos inclusivos,
`CAPACETE` ou `COLETE` e valores do contrato para o estado. A referência de
track é a execução do clipe. Um quadro rotulado sem observação conta como erro.

Para obter métricas de eventos, forneça CSV com
`clip,frame_inicio,frame_fim,track_id,zone_id,event_type`. O pareamento
é um a um dentro do intervalo rotulado e o atraso é calculado a partir do
quadro inicial. Sem esse CSV, o relatório contém as métricas de estado e
execução. Para medir reconexão, monitore uma fonte já ativa e provoque
a interrupção no ambiente de teste.

Os scripts possuem testes com entradas sintéticas. Os números de FPS e
latência da tabela são medições reais nos trechos públicos.

## Próxima validação

A T17 permanece parcial. A validação com a equipe deverá registrar os resultados
com rótulos reais e equipamento de laboratório, incluindo webcam física e
transmissão RTSP. Não há resultados adicionais dessas atividades nesta revisão
documental. Ver [limitações e prioridades](LIMITACOES_VC.md).
