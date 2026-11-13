package br.com.visaodoporto.backend.service;

import java.time.*;
import java.util.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.web.server.ResponseStatusException;
import br.com.visaodoporto.backend.dto.CapacitacaoRequest;
import br.com.visaodoporto.backend.entity.*;
import br.com.visaodoporto.backend.repository.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class CapacitacaoServiceTest {
    private final UUID id = UUID.randomUUID();
    private final LocalDate hoje = LocalDate.of(2026, 11, 13);
    private final Clock clock = Clock.fixed(Instant.parse("2026-11-13T15:00:00Z"),
            ZoneId.of("America/Sao_Paulo"));
    private CapacitacaoRepository repository;
    private TrabalhadorRepository trabalhadores;
    private Trabalhador trabalhador;
    private CapacitacaoService service;

    @BeforeEach
    void preparar() {
        repository = mock(CapacitacaoRepository.class);
        trabalhadores = mock(TrabalhadorRepository.class);
        trabalhador = new Trabalhador("Pessoa fictícia", "COL-023", "Empresa fictícia");
        when(trabalhadores.findById(id)).thenReturn(Optional.of(trabalhador));
        service = new CapacitacaoService(repository, trabalhadores, clock);
    }

    private Capacitacao registro(LocalDate fim, boolean verificada) {
        return new Capacitacao(trabalhador, "DEMO", "Curso fictício", hoje.minusDays(10),
                fim, verificada, "Demonstração", verificada ? "OPERADOR-DEMO" : null, clock.instant());
    }

    private void registros(Capacitacao... registros) {
        when(repository.findByTrabalhadorIdAndCodigoOrderByRegistradaEmDesc(id, "DEMO"))
                .thenReturn(List.of(registros));
    }

    @Test void validadeIncluiUltimoDiaSemAutorizarAcesso() {
        registros(registro(hoje, true));
        var resultado = service.consultar(id, "DEMO");
        assertEquals("VALIDA", resultado.situacao());
        assertEquals("NAO_AVALIADA", resultado.autorizacaoAcesso());
    }

    @Test void validadeMudaNoDiaSeguinteSemAlterarRegistro() {
        registros(registro(hoje, true));
        Clock amanha = Clock.offset(clock, Duration.ofDays(1));
        var outroServico = new CapacitacaoService(repository, trabalhadores, amanha);
        assertEquals("VENCIDA", outroServico.consultar(id, "DEMO").situacao());
    }

    @Test void usaDataDeSaoPauloNaViradaUtc() {
        registros(registro(hoje, true));
        Clock noite = Clock.fixed(Instant.parse("2026-11-14T01:00:00Z"), clock.getZone());
        var outroServico = new CapacitacaoService(repository, trabalhadores, noite);
        assertEquals("VALIDA", outroServico.consultar(id, "DEMO").situacao());
        assertEquals(hoje, outroServico.consultar(id, "DEMO").dataReferencia());
    }

    @Test void informaAusenteSemInventarCapacitacao() {
        registros();
        assertEquals("AUSENTE", service.consultar(id, "DEMO").situacao());
    }

    @Test void documentoNaoVerificadoNuncaProvaValidade() {
        registros(registro(hoje.plusDays(10), false));
        assertEquals("NAO_VERIFICADA", service.consultar(id, "DEMO").situacao());
    }

    @Test void renovacaoVerificadaSuperaRegistroVencido() {
        registros(registro(hoje.minusDays(1), true), registro(hoje.plusDays(10), true));
        assertEquals("VALIDA", service.consultar(id, "DEMO").situacao());
        assertEquals(2, service.consultar(id, "DEMO").registros().size());
    }

    @Test void renovacaoPendenteNaoFicaValida() {
        registros(registro(hoje.minusDays(1), true), registro(hoje.plusDays(10), false));
        assertEquals("NAO_VERIFICADA", service.consultar(id, "DEMO").situacao());
    }

    @Test void exigeTrabalhadorExistente() {
        UUID desconhecido = UUID.randomUUID();
        when(trabalhadores.findById(desconhecido)).thenReturn(Optional.empty());
        var erro = assertThrows(ResponseStatusException.class,
                () -> service.consultar(desconhecido, "DEMO"));
        assertEquals(404, erro.getStatusCode().value());
        verifyNoInteractions(repository);
    }

    @Test void rejeitaRealizacaoFuturaEDatasInvertidas() {
        for (var r : List.of(
                new CapacitacaoRequest("DEMO", "Curso", hoje.plusDays(1), hoje.plusDays(30), true, "Demo", "OP"),
                new CapacitacaoRequest("DEMO", "Curso", hoje, hoje.minusDays(1), true, "Demo", "OP"))) {
            assertThrows(ResponseStatusException.class, () -> service.cadastrar(id, r));
        }
        verify(repository, never()).save(any());
    }

    @Test void exigeVerificadorQuandoVerificada() {
        var r = new CapacitacaoRequest("DEMO", "Curso", hoje, hoje.plusDays(1), true, "Demo", " ");
        assertThrows(ResponseStatusException.class, () -> service.cadastrar(id, r));
        verify(repository, never()).save(any());
    }

    @Test void rejeitaVerificadorQuandoNaoVerificada() {
        var r = new CapacitacaoRequest("DEMO", "Curso", hoje, hoje.plusDays(1), false, "Demo", "OP");
        assertThrows(ResponseStatusException.class, () -> service.cadastrar(id, r));
    }
}
