package br.com.visaodoporto.backend;

import br.com.visaodoporto.backend.repository.ZonaRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.context.WebApplicationContext;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.node.ObjectNode;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.springframework.test.web.servlet.setup.MockMvcBuilders.webAppContextSetup;

@SpringBootTest
class ZonaApiTest {
    private static final String ROTA = "/api/v1/cameras/CAM-A/zonas";
    private static final String VALIDO = "[[0.1,0.1],[0.9,0.1],[0.9,0.9],[0.5,0.6],[0.1,0.9]]";
    @Autowired WebApplicationContext context;
    @Autowired ZonaRepository zonas;
    @Autowired ObjectMapper json;
    private MockMvc mvc;

    @BeforeEach
    void preparar() {
        zonas.deleteAll();
        mvc = webAppContextSetup(context).build();
    }

    @Test
    void listaSemZonas() throws Exception {
        mvc.perform(get(ROTA)).andExpect(status().isOk()).andExpect(content().json("[]"));
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "[[0,0],[1,1]]",
            "[[0,0],[2,0],[0,1]]",
            "[[0,0],[1,1],[0,1],[1,0]]",
            "[[0,0],[1,0],[1,0],[0,1]]",
            "[[0,0],[1,0],[0.5,0],[0,1]]",
            "[[0,0],[0.001,0],[0,0.001]]"
    })
    void rejeitaPoligonoInvalidoSemGravarOutroItem(String invalido) throws Exception {
        mvc.perform(put(ROTA).contentType(MediaType.APPLICATION_JSON)
                        .content("[" + zona("válido", VALIDO) + "," + zona("inválido", invalido) + "]"))
                .andExpect(status().isBadRequest());
        assertEquals(0, zonas.count());
    }

    @Test
    void versionaSoARegraAlteradaEDesativaOmitida() throws Exception {
        var created = mvc.perform(put(ROTA).contentType(MediaType.APPLICATION_JSON)
                        .content("[" + zona("A", VALIDO) + "," + zona("B", VALIDO) + "]"))
                .andExpect(status().isOk()).andReturn();
        var body = json.readTree(created.getResponse().getContentAsString());
        assertEquals(1, body.get(0).get("rule_version").asInt());
        assertEquals(1, body.get(1).get("rule_version").asInt());
        ObjectNode a = (ObjectNode) body.get(0);
        a.set("required_ppe", json.readTree("[\"COLETE\"]"));
        var update = mvc.perform(put(ROTA).contentType(MediaType.APPLICATION_JSON).content(body.toString()))
                .andExpect(status().isOk()).andExpect(jsonPath("$[0].rule_version").value(2))
                .andExpect(jsonPath("$[1].rule_version").value(1)).andReturn();
        a = (ObjectNode) json.readTree(update.getResponse().getContentAsString()).get(0);
        a.put("nome", "Nome atualizado");
        mvc.perform(put(ROTA).contentType(MediaType.APPLICATION_JSON).content("[" + a + "]"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].rule_version").value(2));
        assertEquals(2, zonas.count());
        mvc.perform(put("/api/v1/cameras/CAM-B/zonas").contentType(MediaType.APPLICATION_JSON)
                        .content("[" + a + "]")).andExpect(status().isBadRequest());
    }

    private String zona(String nome, String polygon) {
        return """
                {"nome":"%s","polygon":%s,"rule_type":"EPI_OBRIGATORIO","rule_id":"EPI-OBRIG",
                 "required_ppe":["CAPACETE"]}
                """.formatted(nome, polygon);
    }
}
