package br.com.visaodoporto.backend.dto.vision;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.List;
import java.util.UUID;

public record ZonaDto(
        @JsonProperty("zone_id") UUID zoneId,
        @NotBlank @Size(max = 120) String nome,
        @NotNull @Size(min = 3, max = 16) List<List<Double>> polygon,
        @JsonProperty("required_ppe") List<@NotNull Epi> requiredPpe,
        @JsonProperty("rule_type") @NotNull TipoRegra ruleType,
        @JsonProperty("rule_id") @Size(max = 120) String ruleId,
        @JsonProperty("rule_version") Integer ruleVersion,
        Boolean ativa) {

    public enum Epi { CAPACETE, COLETE }
    public enum TipoRegra { EPI_OBRIGATORIO, AREA_RESTRITA }
}
