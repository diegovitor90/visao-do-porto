
package br.com.visaodoporto.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record TrabalhadorRequest(
    @NotBlank @Size(max = 255) String nome,
    @NotBlank @Size(max = 255) String matricula,
    @NotBlank @Size(max = 255) String empresa,
    @Size(max = 255) String setor,
    @Size(max = 255) String cargo
) {
    public TrabalhadorRequest(String nome, String matricula, String empresa) {
        this(nome, matricula, empresa, null, null);
    }
}
