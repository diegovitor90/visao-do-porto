package br.com.visaodoporto.backend.client;

import br.com.visaodoporto.backend.controller.VisionController;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.client.RestClient;

import java.net.ConnectException;
import java.net.http.HttpTimeoutException;
import java.nio.charset.StandardCharsets;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.setup.MockMvcBuilders.standaloneSetup;

class VisionClientTest {
    @org.springframework.web.bind.annotation.RestControllerAdvice
    static class ApiErrors extends org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler {}

    private static final String BASE = "/api/v1/vision";
    private MockRestServiceServer servidor;
    private MockMvc mvc;
    private final MockMultipartFile imagem = new MockMultipartFile(
            "file", "porto.png", "image/png", "imagem".getBytes(StandardCharsets.UTF_8));

    @BeforeEach
    void preparar() {
        var builder = RestClient.builder().baseUrl("http://127.0.0.1:8000");
        servidor = MockRestServiceServer.bindTo(builder).build();
        mvc = standaloneSetup(new VisionController(new VisionClient(builder.build())))
                .setControllerAdvice(new ApiErrors())
                .build();
    }

    @ParameterizedTest
    @ValueSource(strings = {"/analyze", "/analyze/ppe"})
    void repassaImagemEContrato(String rota) throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + rota))
                .andExpect(content().string(containsString("filename=\"porto.png\"")))
                .andExpect(content().string(containsString("Content-Type: image/png")))
                .andRespond(withSuccess("""
                    {"filename":"porto.png","width":100,"height":50,"status":"COMPLETED",
                     "inference_performed":true,"model":"teste","detections":[],
                     "message":"ok","campo_novo":1}
                    """, MediaType.APPLICATION_JSON));
        mvc.perform(multipart(BASE + rota).file(imagem)).andExpect(status().isOk())
                .andExpect(jsonPath("$.inference_performed").value(true))
                .andExpect(jsonPath("$.filename").value("porto.png"))
                .andExpect(jsonPath("$.campo_novo").doesNotExist());
        servidor.verify();
    }

    @ParameterizedTest
    @ValueSource(ints = {413, 415, 422})
    void repassaStatusEExplicacao(int code) throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + "/analyze"))
                .andRespond(withStatus(HttpStatus.valueOf(code)).contentType(MediaType.APPLICATION_JSON)
                        .body("{\"detail\":\"Imagem inválida.\"}"));
        mvc.perform(multipart(BASE + "/analyze").file(imagem)).andExpect(status().is(code))
                .andExpect(jsonPath("$.detail").value("Imagem inválida."));
        servidor.verify();
    }

    @Test
    void statusPreservaExtensoes() throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + "/status"))
                .andRespond(withSuccess("{\"status\":\"READY\",\"ppe_model_loaded\":false}", MediaType.APPLICATION_JSON));
        mvc.perform(get(BASE + "/status")).andExpect(status().isOk())
                .andExpect(jsonPath("$.ppe_model_loaded").value(false));
        servidor.verify();
    }

    @Test
    void semArquivo() throws Exception {
        mvc.perform(multipart(BASE + "/analyze")).andExpect(status().isBadRequest());
        servidor.verify();
    }

    @Test
    void corpoInvalido() throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + "/analyze"))
                .andRespond(withSuccess("{}", MediaType.APPLICATION_JSON));
        mvc.perform(multipart(BASE + "/analyze").file(imagem)).andExpect(status().isBadGateway());
    }

    @Test
    void respostaComDeteccoesNulasEhInvalida() throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + "/analyze"))
                .andRespond(withSuccess("""
                    {"filename":"porto.png","width":100,"height":50,"status":"COMPLETED",
                     "inference_performed":true,"model":"teste","detections":null,"message":"ok"}
                    """, MediaType.APPLICATION_JSON));
        mvc.perform(multipart(BASE + "/analyze").file(imagem)).andExpect(status().isBadGateway());
        servidor.verify();
    }

    @Test
    void statusSemCampoObrigatorioEhInvalido() throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + "/status"))
                .andRespond(withSuccess("{}", MediaType.APPLICATION_JSON));
        mvc.perform(get(BASE + "/status")).andExpect(status().isBadGateway());
        servidor.verify();
    }

    @Test
    void rejeitaTipoMimeMalformado() throws Exception {
        var invalida = new MockMultipartFile("file", "porto.png", "image", new byte[]{1});
        mvc.perform(multipart(BASE + "/analyze").file(invalida)).andExpect(status().isUnsupportedMediaType());
        servidor.verify();
    }

    @Test
    void indisponibilidade() throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + "/status"))
                .andRespond(withException(new ConnectException()));
        mvc.perform(get(BASE + "/status")).andExpect(status().isServiceUnavailable());
    }

    @Test
    void timeout() throws Exception {
        servidor.expect(requestTo("http://127.0.0.1:8000" + BASE + "/status"))
                .andRespond(withException(new HttpTimeoutException("timeout")));
        mvc.perform(get(BASE + "/status")).andExpect(status().isGatewayTimeout());
    }
}
