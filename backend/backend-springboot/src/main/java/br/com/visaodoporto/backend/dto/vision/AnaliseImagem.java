package br.com.visaodoporto.backend.dto.vision;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Objects;

@JsonIgnoreProperties(ignoreUnknown = true)
public record AnaliseImagem(
        @JsonProperty(required = true) String filename,
        @JsonProperty(required = true) int width,
        @JsonProperty(required = true) int height,
        @JsonProperty(required = true) String status,
        @JsonProperty(value = "inference_performed", required = true) boolean inferencePerformed,
        @JsonProperty(required = true) String model,
        @JsonProperty(required = true) List<Deteccao> detections,
        @JsonProperty(required = true) String message) {
    public AnaliseImagem {
        if (filename == null || width <= 0 || height <= 0 || status == null || model == null
                || message == null || detections == null || detections.stream().anyMatch(Objects::isNull)) {
            throw new IllegalArgumentException("Resultado de imagem incompleto.");
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Deteccao(
            @JsonProperty(value = "class_id", required = true) int classId,
            @JsonProperty(value = "class_name", required = true) String className,
            @JsonProperty(required = true) double confidence,
            @JsonProperty(required = true) Caixa bbox) {
        public Deteccao {
            if (className == null || bbox == null) {
                throw new IllegalArgumentException("Detecção incompleta.");
            }
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Caixa(
            @JsonProperty(required = true) double x1,
            @JsonProperty(required = true) double y1,
            @JsonProperty(required = true) double x2,
            @JsonProperty(required = true) double y2) {}
}
