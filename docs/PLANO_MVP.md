# Visão do Porto: plano do primeiro MVP

## Situação

Planejamento inicial. O repositório ainda não contém o código do protótipo mostrado no vídeo. Este documento não atesta integrações implementadas nem validação em ambiente portuário. A arquitetura completa é uma visão de evolução; o primeiro incremento terá um recorte controlado.

## Objetivo proposto

Em uma câmera fixa do laboratório, detectar e acompanhar pessoas, permitir que um operador vincule uma trajetória a um cadastro fictício e mostrar a situação do treinamento exigido por uma zona. O piloto apoia a conferência humana; não controla máquinas ou libera acesso físico automaticamente.

Diferencial proposto: integração entre trajetória, cadastro, treinamento e contexto da zona. ByteTrack é um componente existente, não uma inovação criada pelo grupo.

## Arquitetura do incremento

- Vídeo ou webcam -> detector de pessoas -> ByteTrack -> trajetórias.
- Operador confirma o vínculo da pessoa visível com um cadastro de demonstração, em ponto de entrada com uma pessoa por vez.
- Serviço de cadastro fornece treinamento, conclusão, validade e situação da verificação do registro.
- Serviço de regras relaciona zona ativa, atividade, treinamento exigido e permissão de acesso.
- Painel exibe trajetória, vínculo e situação; eventos registram motivo, horário e origem da decisão.

O identificador técnico deve incluir câmera, sessão e track_id. O worker_id é separado e persistente. Um ID de trajetória não comprova identidade. A ocorrência de treinamento no cadastro não equivale, isoladamente, a autorização de acesso.

## Etapas adaptadas ao projeto

| Etapa | Trabalho do grupo | Entrega verificável |
| --- | --- | --- |
| 1. Objetivos | Fechar uma câmera, uma zona, um treinamento de exemplo, quem confirma o vínculo e quais estados serão exibidos. | Escopo e critérios de aceite. |
| 2. Dados | Gravar sequências controladas com uso autorizado; marcar pessoas, trajetórias e entradas/saídas. Criar cadastros fictícios com treinamento válido, vencido, ausente e não verificado. | Vídeos e referências de avaliação; registros fictícios separados dos dados visuais. |
| 3. Separação dos dados | Reservar sessões completas para teste; não distribuir quadros vizinhos do mesmo vídeo entre ajuste e teste. Se houver treinamento, separar treino/validação/teste antes de aumentar dados. | Manifesto de arquivos e divisão por sessão. |
| 4. Solução inicial | Avaliar detector pré-treinado de pessoas com ByteTrack. Implementar vínculo manual, consulta de treinamento e regra de zona. Ajuste fino do detector só após medir falhas. | Fluxo executável de ponta a ponta. |
| 5. Avaliação e ajustes | Medir perdas de pessoas, trocas de ID, vínculos incorretos, alertas indevidos e latência no equipamento usado. | Relatório da configuração inicial e erros observados. |
| 6. Teste reservado | Testar cruzamento de pessoas, oclusão, saída/reentrada, reinício, cadastro sem treinamento e câmera desconectada. | Resultados em sequências não usadas no ajuste. |
| 7. Piloto integrado | Conectar processamento ao painel existente após disponibilização do código; registrar versões e instruções. | Demonstração no laboratório e roteiro reproduzível. |
| 8. Acompanhamento | Revisar ocorrências, registrar limitações e selecionar o próximo incremento. | Histórico de versões e tarefas priorizadas. |

O treinamento do modelo de IA e o treinamento profissional do trabalhador são processos distintos. O segundo vem de registros administrativos verificados, não de inferência visual.

## Regras mínimas propostas

1. Vínculo inexistente ou duvidoso: identificação não confirmada. Não declarar treinamento ausente apenas por falta de identidade.
2. Treinamento: válido, vencido, ausente ou não verificado. Considerar conclusão, verificação e validade segundo regra cadastrada.
3. Perda de trajetória, reinício ou troca de câmera: invalidar o vínculo para decisão até nova confirmação. Trocas silenciosas de ID também são possíveis e precisam ser testadas; não há garantia de identidade contínua.
4. Entrada em polígono é um fato geométrico. Classificar violação depende da zona ativa e das regras aplicáveis.
5. Registrar separadamente situação de treinamento e permissão. Exibir o motivo e os dados usados.

## Primeira tarefa técnica

Implementar detecção de pessoas + ByteTrack com vínculo manual a cadastro fictício e consulta de treinamento. Para a primeira demonstração, manter uma pessoa por vez na área de vinculação. QR Code automatizado fica para incremento posterior; leitura de QR não garante por si só que o portador é o titular.

### Critérios de aceite

- Fonte de vídeo configurável e caixas com IDs visíveis.
- Cadastro persistido de demonstração, sem dados reais de trabalhadores.
- Operador seleciona trajetória ativa e confirma cadastro; registrar confirmação.
- Painel mostra ID técnico, cadastro vinculado e situação do treinamento exigido.
- Casos válido, vencido, ausente, não verificado e sem vínculo demonstrados.
- Perda/reinício invalida vínculo; indisponibilidade de câmera ou cadastro não reutiliza estado antigo como válido.
- Registrar configuração, equipamento, FPS e latência do fluxo; metas numéricas serão acordadas após a medição inicial.
- Reportar número de associações incorretas e trocas de ID, com denominadores; nenhum erro observado em poucos testes prova segurança operacional.

## Dados e contrato proposto

Entidades: trabalhador fictício; treinamento; registro de conclusão/verificação/validade; zona; regra da zona; vínculo de trajetória; evento.

Saída para o painel: camera_id, session_id, track_id, timestamp, bbox, detection_confidence, worker_id opcional, binding_status, zone_id, training_status, access_status e reason.

Não utilizar a confiança do detector como confiança de identidade. Documentar a semântica de cada campo antes de integrar front-end e back-end.

## Organização sugerida

- src/vision: captura, detecção e rastreamento.
- src/registry: cadastros e registros de treinamento.
- src/rules: zonas e condições.
- src/api: contrato com o painel.
- tests: vínculo, validade, perda de sessão e eventos.
- configs: configuração sem credenciais.
- docs: arquitetura, dados, instalação e avaliações.

Essa estrutura é proposta; adaptar ao código existente quando ele for enviado. Não versionar credenciais, vídeos de trabalhadores, documentos pessoais ou certificados reais. Antes de incorporar dependências/modelos, conferir suas licenças e registrar versões.

## Divisão de trabalho proposta a partir das referências do grupo

Diego: back-end e vínculo cadastral. Jason: interface e exibição de estados. Hugo: requisitos, organização e registros de treinamento de demonstração. Responsável por IA/visão computacional: ainda a confirmar. Não foram atribuídas tarefas a contas GitHub não verificadas.

## Evolução após o primeiro incremento

EPIs (capacete/colete), leitura de QR, múltiplas câmeras, solicitações do campo, integração com registros institucionais e relatórios. Reconhecimento facial e associação entre câmeras não fazem parte desta primeira entrega.

## Referências

- Guia de etapas: https://docs.ultralytics.com/pt/guides/steps-of-a-cv-project/
- ByteTrack oficial: https://github.com/FoundationVision/ByteTrack
- Arquitetura indicada pelo grupo: https://excalidraw.com/#json=bfOGqeFUAc2f7SfcG8_Iw,YeRc1H65m6-Lo3VBv4mUnQ

Plano proposto em 12/11/2026. O guia orienta o ciclo de visão computacional; cadastro, vínculo, regras e critérios acima são adaptações ao Visão do Porto.
