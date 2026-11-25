package br.com.visaodoporto.backend.service;

import br.com.visaodoporto.backend.dto.vision.EventoDto;
import br.com.visaodoporto.backend.dto.vision.EventoDto.Resposta;
import br.com.visaodoporto.backend.dto.vision.EventoDto.Revisao;
import br.com.visaodoporto.backend.dto.vision.EventoDto.StatusRevisao;
import br.com.visaodoporto.backend.dto.vision.EventoDto.TipoEvento;
import br.com.visaodoporto.backend.entity.EventoVisao;
import br.com.visaodoporto.backend.repository.EventoVisaoRepository;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.web.server.ResponseStatusException;
import tools.jackson.databind.ObjectMapper;

import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class EventoVisaoService {
    private final EventoVisaoRepository repository;
    private final ObjectMapper json;
    private final Clock clock;
    private final TransactionTemplate transaction;

    public EventoVisaoService(EventoVisaoRepository repository, ObjectMapper json, Clock clock,
                              PlatformTransactionManager manager) {
        this.repository = repository;
        this.json = json;
        this.clock = clock;
        this.transaction = new TransactionTemplate(manager);
    }

    public record Recebimento(boolean criado, Resposta resposta) {}

    public synchronized Recebimento receber(EventoDto dto) {
        if (dto.evidenceRef() != null && !dto.evidenceRef().equals(dto.eventId() + ".jpg")) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "evidence_ref deve corresponder ao event_id.");
        }
        return transaction.execute(status -> {
            var existente = repository.findById(dto.eventId());
            if (existente.isPresent()) {
                var resposta = resposta(existente.get());
                if (!resposta.evento().equals(dto)) {
                    throw new ResponseStatusException(HttpStatus.CONFLICT, "event_id já usado com conteúdo diferente.");
                }
                return new Recebimento(false, resposta);
            }
            var evento = repository.save(new EventoVisao(dto, json.writeValueAsString(dto), clock.instant()));
            return new Recebimento(true, resposta(evento));
        });
    }

    public List<Resposta> listar(String camera, UUID zona, TipoEvento tipo, StatusRevisao revisao,
                                 Instant desde, int limite) {
        var page = PageRequest.of(0, limite, Sort.by(Sort.Direction.DESC, "timestamp", "id"));
        return repository.findAll((root, query, cb) -> {
            var filtros = new ArrayList<Predicate>();
            if (camera != null) filtros.add(cb.equal(root.get("cameraId"), camera));
            if (zona != null) filtros.add(cb.equal(root.get("zoneId"), zona));
            if (tipo != null) filtros.add(cb.equal(root.get("eventType"), tipo));
            if (revisao != null) filtros.add(cb.equal(root.get("reviewStatus"), revisao));
            if (desde != null) filtros.add(cb.greaterThanOrEqualTo(root.get("timestamp"), desde));
            return cb.and(filtros.toArray(Predicate[]::new));
        }, page).stream().map(this::resposta).toList();
    }

    public Resposta buscar(UUID id) { return resposta(encontrar(id)); }

    @Transactional
    public Resposta revisar(UUID id, Revisao revisao) {
        var evento = encontrar(id);
        if (revisao.status() == StatusRevisao.DESCARTADO && (revisao.motivo() == null || revisao.motivo().isBlank())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Informe o motivo do descarte.");
        }
        evento.revisar(revisao.status(), revisao.motivo(), clock.instant());
        return resposta(evento);
    }

    private EventoVisao encontrar(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Evento não encontrado."));
    }

    private Resposta resposta(EventoVisao evento) {
        return new Resposta(json.readValue(evento.getPayload(), EventoDto.class), evento.getReviewStatus(),
                evento.getReceivedAt(), evento.getReviewedAt(), evento.getReviewReason());
    }
}
