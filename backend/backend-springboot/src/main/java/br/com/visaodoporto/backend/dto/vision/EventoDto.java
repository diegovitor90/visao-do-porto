package br.com.visaodoporto.backend.dto.vision;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonUnwrapped;
import jakarta.validation.constraints.*;

import java.time.Instant;
import java.util.UUID;

@JsonIgnoreProperties(ignoreUnknown = true)
public record EventoDto(
        @JsonProperty("schema_version") @NotNull @Pattern(regexp = "0\\.2") String schemaVersion,
        @JsonProperty("event_id") @NotNull UUID eventId,
        @JsonProperty("camera_id") @NotNull @Pattern(regexp = "[A-Za-z0-9_-]{1,100}") String cameraId,
        @JsonProperty("session_id") @NotNull UUID sessionId,
        @JsonProperty("zone_id") @NotNull UUID zoneId,
        @NotNull Instant timestamp,
        @JsonProperty("event_type") @NotNull TipoEvento eventType,
        @JsonProperty("track_id") @NotNull @PositiveOrZero Long trackId,
        @JsonProperty("rule_id") @NotBlank @Size(max = 120) String ruleId,
        @JsonProperty("rule_version") @NotNull @Positive Integer ruleVersion,
        @DecimalMin("0") @DecimalMax("1") Double confidence,
        @JsonProperty("evidence_ref")
        @Pattern(regexp = "[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\\.jpg") String evidenceRef,
        @NotNull Fonte source,
        @NotBlank @Size(max = 1024) String explanation) {

    public enum TipoEvento { INTRUSAO, EPI_AUSENTE, EPI_INDETERMINADO }
    public enum Fonte { ARQUIVO, WEBCAM, RTSP }
    public enum StatusRevisao { PENDENTE, CONFIRMADO, DESCARTADO, INDETERMINADO }

    public record Revisao(@NotNull StatusRevisao status, @Size(max = 500) String motivo) {}

    public record Resposta(@JsonUnwrapped EventoDto evento,
                           @JsonProperty("review_status") StatusRevisao reviewStatus,
                           @JsonProperty("received_at") Instant receivedAt,
                           @JsonProperty("reviewed_at") Instant reviewedAt,
                           @JsonProperty("review_reason") String reviewReason) {}
}
