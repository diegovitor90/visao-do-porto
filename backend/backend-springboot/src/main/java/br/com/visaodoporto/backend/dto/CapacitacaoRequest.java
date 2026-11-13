package br.com.visaodoporto.backend.dto;

import java.time.LocalDate;
import jakarta.validation.constraints.*;

public record CapacitacaoRequest(
        @NotBlank @Pattern(regexp = "[A-Z0-9_-]{1,64}") String codigo,
        @NotBlank @Size(max = 150) String nome,
        @NotNull LocalDate realizadaEm,
        @NotNull LocalDate validaAte,
        @NotNull Boolean verificada,
        @NotBlank @Size(max = 200) String fonte,
        @Size(max = 100) String verificadaPor) {
}
