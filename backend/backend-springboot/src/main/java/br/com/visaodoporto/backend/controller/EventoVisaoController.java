package br.com.visaodoporto.backend.controller;

import br.com.visaodoporto.backend.dto.vision.EventoDto;
import br.com.visaodoporto.backend.dto.vision.EventoDto.*;
import br.com.visaodoporto.backend.service.EventoVisaoService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/eventos")
public class EventoVisaoController {
    private final EventoVisaoService service;

    public EventoVisaoController(EventoVisaoService service) { this.service = service; }

    @PostMapping
    public ResponseEntity<Resposta> receber(@RequestBody @Valid EventoDto evento) {
        var recebido = service.receber(evento);
        return ResponseEntity.status(recebido.criado() ? HttpStatus.CREATED : HttpStatus.OK)
                .body(recebido.resposta());
    }

    @GetMapping
    public List<Resposta> listar(@RequestParam(name = "camera_id", required = false) String camera,
                                 @RequestParam(name = "zone_id", required = false) UUID zona,
                                 @RequestParam(name = "event_type", required = false) TipoEvento tipo,
                                 @RequestParam(name = "review_status", required = false) StatusRevisao revisao,
                                 @RequestParam(required = false) Instant desde,
                                 @RequestParam(defaultValue = "100") @Min(1) @Max(500) int limite) {
        return service.listar(camera, zona, tipo, revisao, desde, limite);
    }

    @GetMapping("/{id}")
    public Resposta buscar(@PathVariable UUID id) { return service.buscar(id); }

    @PatchMapping("/{id}/revisao")
    public Resposta revisar(@PathVariable UUID id, @RequestBody @Valid Revisao revisao) {
        return service.revisar(id, revisao);
    }
}
