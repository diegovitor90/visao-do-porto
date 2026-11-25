package br.com.visaodoporto.backend;

import br.com.visaodoporto.backend.repository.EventoVisaoRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.context.WebApplicationContext;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.node.ObjectNode;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.springframework.test.web.servlet.setup.MockMvcBuilders.webAppContextSetup;

@SpringBootTest
class EventoVisaoApiTest {
    private static final String ROTA = "/api/v1/eventos";
    @Autowired WebApplicationContext context;
    @Autowired EventoVisaoRepository eventos;
    @Autowired ObjectMapper json;
    private MockMvc mvc;

    @BeforeEach
    void preparar() {
        eventos.deleteAll();
        mvc = webAppContextSetup(context).build();
    }

    @Test
    void recebeReenvioIgnoraRevisaoERejeitaConflito() throws Exception {
        var payload = evento("CAM-A", "EPI_AUSENTE", "2026-11-24T17:00:00Z");
        payload.put("review_status", "CONFIRMADO");
        payload.put("cpf", "fictício");
        mvc.perform(post(ROTA).contentType(MediaType.APPLICATION_JSON).content(payload.toString()))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.event_id").value(payload.get("event_id").asString()))
                .andExpect(jsonPath("$.review_status").value("PENDENTE"))
                .andExpect(jsonPath("$.cpf").doesNotExist())
                .andExpect(jsonPath("$.received_at").isString());
        payload.remove("review_status");
        mvc.perform(post(ROTA).contentType(MediaType.APPLICATION_JSON).content(payload.toString()))
                .andExpect(status().isOk());
        payload.put("track_id", 3);
        mvc.perform(post(ROTA).contentType(MediaType.APPLICATION_JSON).content(payload.toString()))
                .andExpect(status().isConflict());
        assertEquals(1, eventos.count());
    }

    @ParameterizedTest
    @CsvSource({
            "event_type, '\"OUTRO\"'", "source, '\"OUTRO\"'", "confidence, 1.1",
            "track_id, -1", "rule_version, 0", "schema_version, '\"0.1\"'",
            "evidence_ref, '\"../fora.jpg\"'",
            "evidence_ref, '\"00000000-0000-0000-0000-000000000000.jpg\"'"
    })
    void rejeitaCamposInvalidos(String field, String invalid) throws Exception {
        var payload = evento("CAM-A", "EPI_AUSENTE", "2026-11-24T17:00:00Z");
        payload.set(field, json.readTree(invalid));
        mvc.perform(post(ROTA).contentType(MediaType.APPLICATION_JSON).content(payload.toString()))
                .andExpect(status().isBadRequest());
        assertEquals(0, eventos.count());
    }

    @Test
    void listaOrdenadaComFiltrosERevisa() throws Exception {
        var primeiro = evento("CAM-A", "EPI_AUSENTE", "2026-11-24T17:00:00Z");
        var segundo = evento("CAM-A", "INTRUSAO", "2026-11-24T18:00:00Z");
        var terceiro = evento("CAM-B", "EPI_AUSENTE", "2026-11-24T19:00:00Z");
        for (var payload : new ObjectNode[]{primeiro, segundo, terceiro}) {
            mvc.perform(post(ROTA).contentType(MediaType.APPLICATION_JSON).content(payload.toString()))
                    .andExpect(status().isCreated());
        }
        String id = segundo.get("event_id").asString();
        mvc.perform(get(ROTA).param("camera_id", "CAM-A").param("limite", "1"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].event_id").value(id));
        mvc.perform(get(ROTA).param("limite", "501")).andExpect(status().isBadRequest());
        mvc.perform(get(ROTA + "/" + UUID.randomUUID())).andExpect(status().isNotFound());
        mvc.perform(patch(ROTA + "/" + id + "/revisao").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"DESCARTADO\"}")).andExpect(status().isBadRequest());
        mvc.perform(patch(ROTA + "/" + id + "/revisao").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"DESCARTADO\",\"motivo\":\"imagem inconclusiva\"}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.review_reason").value("imagem inconclusiva"))
                .andExpect(jsonPath("$.reviewed_at").isString());
        mvc.perform(get(ROTA).param("camera_id", "CAM-A").param("zone_id", segundo.get("zone_id").asString())
                        .param("event_type", "INTRUSAO").param("review_status", "DESCARTADO")
                        .param("desde", "2026-11-24T17:30:00Z"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].event_id").value(id));
        mvc.perform(post(ROTA).contentType(MediaType.APPLICATION_JSON).content(segundo.toString()))
                .andExpect(status().isOk()).andExpect(jsonPath("$.review_status").value("DESCARTADO"));
        mvc.perform(patch(ROTA + "/" + id + "/revisao").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"CONFIRMADO\"}")).andExpect(status().isOk());
        mvc.perform(get(ROTA + "/" + id)).andExpect(status().isOk())
                .andExpect(jsonPath("$.review_status").value("CONFIRMADO"));
    }

    private ObjectNode evento(String camera, String tipo, String timestamp) {
        return (ObjectNode) json.readTree("""
                {"schema_version":"0.2","event_id":"%s","camera_id":"%s","session_id":"%s","zone_id":"%s",
                 "timestamp":"%s","event_type":"%s","track_id":1,"rule_id":"R","rule_version":1,
                 "confidence":0.9,"evidence_ref":null,"source":"ARQUIVO","explanation":"Teste local."}
                """.formatted(UUID.randomUUID(), camera, UUID.randomUUID(), UUID.randomUUID(), timestamp, tipo));
    }
}
