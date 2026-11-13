package br.com.visaodoporto.backend.dto;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

public record ConsultaCapacitacaoResponse(UUID trabalhadorId, String codigo,
        LocalDate dataReferencia, String fuso, String situacao,
        String autorizacaoAcesso, List<CapacitacaoResponse> registros) {
}
