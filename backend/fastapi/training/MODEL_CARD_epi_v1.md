# Modelo de EPI v1

`best_epi_grupo_yolo26s.pt` é o peso local do notebook
`notebook2_download_automatico.ipynb`. Coloque-o em `backend/fastapi/models/`.
SHA-256 esperado `06905756c9063483e657b90f5677170a567eb7ec725a6f1943c2d38c1cbed262`.

Treino no Kaggle com YOLO26s, Ultralytics 8.4.215, 4.060 imagens do dataset
ndomalau, seed 42, resolução 640, até 40 épocas e divisão por grupos de cenas.
Os arquivos `data_epi_grupo.yaml` e `split_por_grupo.csv` registram a configuração.

| Classe | Precisão | Recall | mAP50 | mAP50–95 |
| --- | ---: | ---: | ---: | ---: |
| helmet | 0,927787 | 0,901611 | 0,946941 | 0,637142 |
| no_helmet | 0,864997 | 0,760459 | 0,820277 | 0,476466 |
| no_vest | 0,862787 | 0,782676 | 0,849940 | 0,496637 |
| person | 0,938885 | 0,881087 | 0,931061 | 0,718269 |
| vest | 0,923596 | 0,909148 | 0,956994 | 0,744108 |
| Teste agregado | 0,903610 | 0,846996 | 0,901042 | 0,614524 |

Valores arredondados dos CSVs `metricas_grupo.csv` e
`metricas_por_classe_teste_yolo26s.csv`. O teste no Kaggle registrou
11,383562 ms/imagem. Essa medição corresponde ao ambiente de treinamento.

Uso experimental para observar EPIs. Distância, oclusões e mudança de câmera
podem reduzir a qualidade. Ausência de detecção é indeterminada. Licenças
indicadas no plano: Ultralytics AGPL-3.0 e dataset CC BY 4.0. A confirmação
do orientador segue pendente.

```powershell
cd backend/fastapi
.\.venv\Scripts\python.exe training/verificar_modelo.py models/best_epi_grupo_yolo26s.pt C:/caminho/imagem.png
```

Em 24/11/2026, o verificador confirmou o SHA-256, as cinco classes e uma inferência em CPU com Ultralytics 8.4.212 no ambiente fixado.
