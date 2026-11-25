package br.com.visaodoporto.backend.entity;

import br.com.visaodoporto.backend.dto.vision.EventoDto;
import br.com.visaodoporto.backend.dto.vision.EventoDto.StatusRevisao;
import br.com.visaodoporto.backend.dto.vision.EventoDto.TipoEvento;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "eventos_visao", indexes = @Index(name = "idx_evento_timestamp", columnList = "detectado_em"))
public class EventoVisao {
    @Id
    private UUID id;
    @Column(nullable = false, length = 100)
    private String cameraId;
    @Column(nullable = false)
    private UUID zoneId;
    @Column(name = "detectado_em", nullable = false)
    private Instant timestamp;
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TipoEvento eventType;
    @Lob
    @Column(nullable = false)
    private String payload;
    @Column(nullable = false)
    private Instant receivedAt;
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StatusRevisao reviewStatus;
    private Instant reviewedAt;
    @Column(length = 500)
    private String reviewReason;

    protected EventoVisao() {}

    public EventoVisao(EventoDto evento, String payload, Instant recebido) {
        id = evento.eventId();
        cameraId = evento.cameraId();
        zoneId = evento.zoneId();
        timestamp = evento.timestamp();
        eventType = evento.eventType();
        this.payload = payload;
        receivedAt = recebido;
        reviewStatus = StatusRevisao.PENDENTE;
    }

    public void revisar(StatusRevisao status, String motivo, Instant data) {
        reviewStatus = status;
        reviewReason = motivo;
        reviewedAt = data;
    }

    public String getPayload() { return payload; }
    public Instant getReceivedAt() { return receivedAt; }
    public StatusRevisao getReviewStatus() { return reviewStatus; }
    public Instant getReviewedAt() { return reviewedAt; }
    public String getReviewReason() { return reviewReason; }
}
