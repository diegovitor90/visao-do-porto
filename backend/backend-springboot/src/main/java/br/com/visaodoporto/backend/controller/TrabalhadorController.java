
package br.com.visaodoporto.backend.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import br.com.visaodoporto.backend.dto.TrabalhadorRequest;
import br.com.visaodoporto.backend.entity.Trabalhador;
import br.com.visaodoporto.backend.service.TrabalhadorService;

@RestController
@RequestMapping("/api/trabalhadores")
public class TrabalhadorController {

    private final TrabalhadorService service;

    public TrabalhadorController(TrabalhadorService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Trabalhador cadastrar(
            @RequestBody TrabalhadorRequest request) {
        try {
            return service.cadastrar(
                request.nome(),
                request.matricula(),
                request.empresa()
            );
        } catch (IllegalArgumentException ex) {
            throw new ResponseStatusException(
                HttpStatus.BAD_REQUEST, ex.getMessage()
            );
        }
    }

    @GetMapping
    public List<Trabalhador> listar() {
        return service.listar();
    }

    @GetMapping("/{id}")
    public Trabalhador buscar(@PathVariable UUID id) {
        try {
            return service.buscarPorId(id);
        } catch (IllegalArgumentException ex) {
            throw new ResponseStatusException(
                HttpStatus.NOT_FOUND, ex.getMessage()
            );
        }
    }
}