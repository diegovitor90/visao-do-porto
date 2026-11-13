package br.com.visaodoporto.backend.dto;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;
import br.com.visaodoporto.backend.entity.Capacitacao;

public record CapacitacaoResponse(UUID id, UUID trabalhadorId, String codigo, String nome,
        LocalDate realizadaEm, LocalDate validaAte, boolean verificada, String fonte,
        String verificadaPor, Instant registradaEm) {
    public static CapacitacaoResponse de(Capacitacao c) {
        return new CapacitacaoResponse(c.getId(), c.getTrabalhador().getId(), c.getCodigo(),
                c.getNome(), c.getRealizadaEm(), c.getValidaAte(), c.isVerificada(),
                c.getFonte(), c.getVerificadaPor(), c.getRegistradaEm());
    }
}
