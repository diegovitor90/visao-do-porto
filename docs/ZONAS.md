# Zonas e regras

Desenhe de uma a duas zonas de quatro pontos sobre o chão no primeiro quadro
do vídeo de demonstração. A presença usa o centro da borda inferior da caixa
da pessoa. Confira a perspectiva no vídeo anotado e deixe folga nas fronteiras.

Use coordenadas normalizadas entre 0 e 1. Prefira polígonos simples com 4 a 8
vértices. A API aceita 3 a 16 vértices, inclusive polígonos côncavos. A área
mínima padrão é 0,0001 da área do quadro (`visao.zonas.area-minima`).

`GET /api/v1/cameras/{cameraId}/zonas` devolve as zonas ativas. O PUT substitui
a lista. Para criar, omita `zone_id`. Para atualizar, informe o UUID da zona.
A omissão de uma zona a desativa. A propriedade `ativa` é opcional no PUT e
assume `true`; o retorno contém o estado ativo. `rule_id` é fixo após a criação.
A versão começa em 1 e sobe quando polígono, conjunto de EPIs ou tipo mudam.

Cada zona tem uma regra. `EPI_OBRIGATORIO` verifica `CAPACETE` e/ou `COLETE`
conforme `required_ppe`. `AREA_RESTRITA` sinaliza presença e mantém autorização
de acesso em `NAO_AVALIADA`.

## Aplicação das alterações nas fontes

As fontes consultam zonas no início e na reconexão. Uma alteração feita pelo PUT
não atualiza automaticamente uma sessão ativa. Para aplicar a nova configuração
imediatamente no piloto, encerre e inicie novamente a fonte. O CLI com `--spring`
consulta as zonas no início de cada execução.

Em caso de falha de comunicação com o Spring, o FastAPI tenta o cache local.
Sem cache válido, o processamento continua sem avaliação de regras por zona.
Verifique o cadastro e os avisos nos logs antes de interpretar os resultados.
Consulte [limitações do piloto](LIMITACOES_VC.md).

## Exemplo de cadastro

```powershell
$zona = @{
    nome = 'Área de EPI obrigatório'
    polygon = @(@(0.15,0.55), @(0.70,0.55), @(0.85,0.90), @(0.10,0.90))
    required_ppe = @('CAPACETE','COLETE')
    rule_type = 'EPI_OBRIGATORIO'
    rule_id = 'EPI-OBRIG'
}
$body = ConvertTo-Json -InputObject @($zona) -Depth 5
Invoke-RestMethod 'http://127.0.0.1:8080/api/v1/cameras/CAM-LAB-01/zonas' -Method Put -ContentType 'application/json' -Body $body
```
