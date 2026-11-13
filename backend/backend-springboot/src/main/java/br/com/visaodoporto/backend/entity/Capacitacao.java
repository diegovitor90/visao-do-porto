package br.com.visaodoporto.backend.entity;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;
import jakarta.persistence.*;

@Entity
@Table(name = "capacitacoes", indexes = {
    @Index(name = "idx_capacitacao_trabalhador_codigo", columnList = "trabalhador_id,codigo")
})
public class Capacitacao {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "trabalhador_id", nullable = false)
    private Trabalhador trabalhador;
    @Column(nullable = false, length = 64)
    private String codigo;
    @Column(nullable = false, length = 150)
    private String nome;
    @Column(nullable = false)
    private LocalDate realizadaEm;
    @Column(nullable = false)
    private LocalDate validaAte;
    @Column(nullable = false)
    private boolean verificada;
    @Column(nullable = false, length = 200)
    private String fonte;
    @Column(length = 100)
    private String verificadaPor;
    @Column(nullable = false)
    private Instant registradaEm;

    protected Capacitacao() {}

    public Capacitacao(Trabalhador trabalhador, String codigo, String nome,
            LocalDate realizadaEm, LocalDate validaAte, boolean verificada,
            String fonte, String verificadaPor, Instant registradaEm) {
        this.trabalhador = trabalhador;
        this.codigo = codigo;
        this.nome = nome;
        this.realizadaEm = realizadaEm;
        this.validaAte = validaAte;
        this.verificada = verificada;
        this.fonte = fonte;
        this.verificadaPor = verificadaPor;
        this.registradaEm = registradaEm;
    }
    public UUID getId() { return id; }
    public Trabalhador getTrabalhador() { return trabalhador; }
    public String getCodigo() { return codigo; }
    public String getNome() { return nome; }
    public LocalDate getRealizadaEm() { return realizadaEm; }
    public LocalDate getValidaAte() { return validaAte; }
    public boolean isVerificada() { return verificada; }
    public String getFonte() { return fonte; }
    public String getVerificadaPor() { return verificadaPor; }
    public Instant getRegistradaEm() { return registradaEm; }
}
