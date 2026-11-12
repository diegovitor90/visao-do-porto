
package br.com.visaodoporto.backend.dto;

public record TrabalhadorRequest(
    String nome,
    String matricula,
    String empresa
) {}
