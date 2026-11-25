package br.com.visaodoporto.backend.client;

import br.com.visaodoporto.backend.config.VisionProperties;
import br.com.visaodoporto.backend.dto.vision.AnaliseImagem;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.InvalidMediaTypeException;
import org.springframework.http.MediaType;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;
import tools.jackson.databind.JsonNode;

import java.io.IOException;
import java.net.SocketTimeoutException;
import java.net.http.HttpClient;
import java.net.http.HttpTimeoutException;
import java.util.function.Supplier;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.util.LinkedMultiValueMap;

@Component
@EnableConfigurationProperties(VisionProperties.class)
public class VisionClient {
    private final RestClient http;

    @Autowired
    public VisionClient(VisionProperties config) {
        var factory = new JdkClientHttpRequestFactory(
                HttpClient.newBuilder().connectTimeout(config.conexaoTimeout()).build());
        factory.setReadTimeout(config.leituraTimeout());
        http = RestClient.builder().baseUrl(config.url()).requestFactory(factory).build();
    }

    VisionClient(RestClient http) {
        this.http = http;
    }

    public AnaliseImagem analisar(MultipartFile file, boolean epi) throws IOException {
        String filename = file.getOriginalFilename() == null ? "" : file.getOriginalFilename();
        var arquivo = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return filename;
            }
        };
        var headers = new HttpHeaders();
        try {
            headers.setContentType(file.getContentType() == null ? MediaType.APPLICATION_OCTET_STREAM
                    : MediaType.parseMediaType(file.getContentType()));
        } catch (InvalidMediaTypeException ex) {
            throw new ResponseStatusException(HttpStatus.UNSUPPORTED_MEDIA_TYPE, "Formato não suportado.");
        }
        var multipart = new LinkedMultiValueMap<String, Object>();
        multipart.add("file", new HttpEntity<>(arquivo, headers));
        String path = epi ? "/api/v1/vision/analyze/ppe" : "/api/v1/vision/analyze";
        return chamar(() -> http.post().uri(path)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(multipart).retrieve().body(AnaliseImagem.class));
    }

    public JsonNode status() {
        var body = chamar(() -> http.get().uri("/api/v1/vision/status").retrieve().body(JsonNode.class));
        if (!body.path("status").isString()) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Resposta inválida da Vision API.");
        }
        return body;
    }

    private <T> T chamar(Supplier<T> request) {
        try {
            T body = request.get();
            if (body == null) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Resposta vazia da Vision API.");
            }
            return body;
        } catch (RestClientResponseException ex) {
            int code = ex.getStatusCode().value();
            if (code == 413 || code == 415 || code == 422) {
                String message = "A Vision API rejeitou a imagem.";
                try {
                    JsonNode body = ex.getResponseBodyAs(JsonNode.class);
                    if (body != null && body.path("detail").isString()) {
                        message = body.path("detail").asString();
                    }
                } catch (RestClientException ignored) {
                    // Preserva o status do upload mesmo com corpo de erro inválido.
                }
                throw new ResponseStatusException(ex.getStatusCode(), message);
            }
            if (ex.getStatusCode().is5xxServerError()) {
                throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Vision API indisponível.");
            }
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Resposta inesperada da Vision API.");
        } catch (ResourceAccessException ex) {
            for (Throwable cause = ex; cause != null; cause = cause.getCause()) {
                if (cause instanceof HttpTimeoutException || cause instanceof SocketTimeoutException) {
                    throw new ResponseStatusException(HttpStatus.GATEWAY_TIMEOUT, "Tempo limite da Vision API.");
                }
            }
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Vision API indisponível.");
        } catch (RestClientException ex) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Resposta inválida da Vision API.");
        }
    }
}
