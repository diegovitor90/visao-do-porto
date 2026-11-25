package br.com.visaodoporto.backend.entity;

import br.com.visaodoporto.backend.dto.vision.ZonaDto.TipoRegra;
import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "zonas", indexes = @Index(name = "idx_zona_camera", columnList = "cameraId"))
public class Zona {
    @Id
    private UUID id;
    @Column(nullable = false, length = 100)
    private String cameraId;
    @Column(nullable = false, length = 120)
    private String nome;
    @Lob
    @Column(nullable = false)
    private String polygon;
    @Column(nullable = false)
    private String requiredPpe;
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TipoRegra ruleType;
    @Column(nullable = false, length = 120)
    private String ruleId;
    @Column(nullable = false)
    private int ruleVersion;
    @Column(nullable = false)
    private boolean ativa;

    protected Zona() {}

    public Zona(String cameraId, String ruleId) {
        id = UUID.randomUUID();
        this.cameraId = cameraId;
        this.ruleId = ruleId == null || ruleId.isBlank() ? id.toString() : ruleId;
    }

    public void atualizar(String nome, String polygon, String requiredPpe, TipoRegra ruleType, boolean ativa) {
        if (!polygon.equals(this.polygon) || !requiredPpe.equals(this.requiredPpe) || ruleType != this.ruleType) {
            ruleVersion++;
        }
        this.nome = nome;
        this.polygon = polygon;
        this.requiredPpe = requiredPpe;
        this.ruleType = ruleType;
        this.ativa = ativa;
    }

    public void desativar() { ativa = false; }
    public UUID getId() { return id; }
    public String getNome() { return nome; }
    public String getPolygon() { return polygon; }
    public String getRequiredPpe() { return requiredPpe; }
    public TipoRegra getRuleType() { return ruleType; }
    public String getRuleId() { return ruleId; }
    public int getRuleVersion() { return ruleVersion; }
    public boolean isAtiva() { return ativa; }
}
