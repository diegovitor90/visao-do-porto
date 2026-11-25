package br.com.visaodoporto.backend.controller;

import br.com.visaodoporto.backend.client.VisionClient;
import br.com.visaodoporto.backend.dto.vision.AnaliseImagem;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import tools.jackson.databind.JsonNode;
import java.io.IOException;

@RestController
@RequestMapping("/api/v1/vision")
public class VisionController {
    private final VisionClient client;

    public VisionController(VisionClient client) {
        this.client = client;
    }

    @PostMapping(value = "/analyze", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public AnaliseImagem analisar(@RequestParam("file") MultipartFile file) throws IOException {
        return client.analisar(file, false);
    }

    @PostMapping(value = "/analyze/ppe", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public AnaliseImagem analisarEpi(@RequestParam("file") MultipartFile file) throws IOException {
        return client.analisar(file, true);
    }

    @GetMapping("/status")
    public JsonNode status() {
        return client.status();
    }
}
