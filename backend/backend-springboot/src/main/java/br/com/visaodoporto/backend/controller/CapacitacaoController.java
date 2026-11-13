package br.com.visaodoporto.backend.controller;

import java.util.List;
import java.util.UUID;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import br.com.visaodoporto.backend.dto.*;
import br.com.visaodoporto.backend.service.CapacitacaoService;

@RestController
@RequestMapping("/api/trabalhadores/{trabalhadorId}/capacitacoes")
public class CapacitacaoController {
    private final CapacitacaoService service;

    public CapacitacaoController(CapacitacaoService service) { this.service = service; }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CapacitacaoResponse cadastrar(@PathVariable UUID trabalhadorId,
            @Valid @RequestBody CapacitacaoRequest request) {
        return service.cadastrar(trabalhadorId, request);
    }

    @GetMapping
    public List<CapacitacaoResponse> listar(@PathVariable UUID trabalhadorId) {
        return service.listar(trabalhadorId);
    }

    @GetMapping("/{codigo}/situacao")
    public ConsultaCapacitacaoResponse consultar(@PathVariable UUID trabalhadorId,
            @PathVariable String codigo) {
        return service.consultar(trabalhadorId, codigo);
    }
}
