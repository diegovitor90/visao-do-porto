package br.com.visaodoporto.backend.service;

import java.time.Clock;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import br.com.visaodoporto.backend.dto.*;
import br.com.visaodoporto.backend.entity.*;
import br.com.visaodoporto.backend.repository.*;

@Service
@Transactional(readOnly = true)
public class CapacitacaoService {
    private final CapacitacaoRepository repository;
    private final TrabalhadorRepository trabalhadores;
    private final Clock clock;

    public CapacitacaoService(CapacitacaoRepository repository,
            TrabalhadorRepository trabalhadores, Clock clock) {
        this.repository = repository;
        this.trabalhadores = trabalhadores;
        this.clock = clock;
    }

    private Trabalhador trabalhador(UUID id) {
        return trabalhadores.findById(id).orElseThrow(() ->
                new ResponseStatusException(HttpStatus.NOT_FOUND, "Trabalhador não encontrado."));
    }

    @Transactional
    public CapacitacaoResponse cadastrar(UUID id, CapacitacaoRequest r) {
        Trabalhador t = trabalhador(id);
        if (!t.isAtivo()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Trabalhador inativo.");
        }
        if (r.validaAte().isBefore(r.realizadaEm()) || r.realizadaEm().isAfter(LocalDate.now(clock))) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "A realização não pode estar no futuro; a validade não pode anteceder a realização.");
        }
        if (r.verificada() && (r.verificadaPor() == null || r.verificadaPor().isBlank())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "Informe quem verificou o registro fictício.");
        }
        if (!r.verificada() && r.verificadaPor() != null && !r.verificadaPor().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "Registro não verificado não deve indicar verificador.");
        }
        Capacitacao c = new Capacitacao(t, r.codigo(), r.nome().strip(), r.realizadaEm(),
                r.validaAte(), r.verificada(), r.fonte().strip(),
                r.verificada() ? r.verificadaPor().strip() : null, clock.instant());
        return CapacitacaoResponse.de(repository.save(c));
    }

    public List<CapacitacaoResponse> listar(UUID id) {
        trabalhador(id);
        return repository.findByTrabalhadorIdOrderByRegistradaEmDesc(id).stream()
                .map(CapacitacaoResponse::de).toList();
    }

    public ConsultaCapacitacaoResponse consultar(UUID id, String codigo) {
        trabalhador(id);
        if (!codigo.matches("[A-Z0-9_-]{1,64}")) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Código de capacitação inválido.");
        }
        LocalDate hoje = LocalDate.now(clock);
        List<Capacitacao> registros = repository.findByTrabalhadorIdAndCodigoOrderByRegistradaEmDesc(id, codigo);
        String situacao;
        if (registros.isEmpty()) {
            situacao = "AUSENTE";
        } else if (registros.stream().anyMatch(c -> c.isVerificada()
                && !c.getRealizadaEm().isAfter(hoje) && !c.getValidaAte().isBefore(hoje))) {
            situacao = "VALIDA";
        } else if (registros.stream().anyMatch(c -> !c.isVerificada())) {
            situacao = "NAO_VERIFICADA";
        } else {
            situacao = "VENCIDA";
        }
        return new ConsultaCapacitacaoResponse(id, codigo, hoje, clock.getZone().getId(), situacao,
                "NAO_AVALIADA", registros.stream().map(CapacitacaoResponse::de).toList());
    }
}
