package br.com.visaodoporto.backend.controller;

import br.com.visaodoporto.backend.dto.vision.ZonaDto;
import br.com.visaodoporto.backend.service.ZonaService;
import jakarta.validation.constraints.Pattern;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1/cameras/{cameraId}/zonas")
public class ZonaController {
    private final ZonaService service;

    public ZonaController(ZonaService service) { this.service = service; }

    @GetMapping
    public List<ZonaDto> listar(@PathVariable @Pattern(regexp = "[A-Za-z0-9_-]{1,100}") String cameraId) {
        return service.listar(cameraId);
    }

    @PutMapping
    public List<ZonaDto> substituir(@PathVariable @Pattern(regexp = "[A-Za-z0-9_-]{1,100}") String cameraId,
                                   @RequestBody List<ZonaDto> zonas) {
        return service.substituir(cameraId, zonas);
    }
}
