
package br.com.visaodoporto.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record TrabalhadorRequest(
    @NotBlank @Size(max = 255) String nome,
    @NotBlank @Size(max = 255) String matricula,
    @NotBlank @Size(max = 255) String empresa
) {}
