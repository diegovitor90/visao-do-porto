package br.com.visaodoporto.backend;

import java.time.*;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import br.com.visaodoporto.backend.repository.*;
import tools.jackson.databind.json.JsonMapper;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
class CapacitacaoApiTest {
    @Autowired WebApplicationContext context;
    @Autowired CapacitacaoRepository capacitacoes;
    @Autowired TrabalhadorRepository trabalhadores;
    private MockMvc mvc;
    private String id;
    private final LocalDate hoje = LocalDate.now(ZoneId.of("America/Sao_Paulo"));

    @BeforeEach void preparar() throws Exception {
        capacitacoes.deleteAll();
        trabalhadores.deleteAll();
        mvc = MockMvcBuilders.webAppContextSetup(context).build();
        id = cadastrarTrabalhador("COL-023");
    }

    private String cadastrarTrabalhador(String matricula) throws Exception {
        String body = """
            {"nome":"Pessoa fictícia","matricula":"%s","empresa":"Empresa fictícia"}
            """.formatted(matricula);
        String resposta = mvc.perform(post("/api/trabalhadores")
                .contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isCreated()).andReturn().getResponse().getContentAsString();
        return JsonMapper.builder().build().readTree(resposta).get("id").asText();
    }

    private String caminho(String trabalhador) {
        return "/api/trabalhadores/" + trabalhador + "/capacitacoes";
    }

    private String corpo(String fim, boolean verificada) {
        return """
            {"codigo":"DEMO","nome":"Curso fictício","realizadaEm":"%s",
             "validaAte":"%s","verificada":%s,"fonte":"Demonstração",
             "verificadaPor":%s}
            """.formatted(hoje.minusDays(10), fim, verificada, verificada ? "\"OP-DEMO\"" : "null");
    }

    @Test void cadastraPersisteListaEConsultaCapacitacao() throws Exception {
        mvc.perform(post(caminho(id)).contentType(MediaType.APPLICATION_JSON)
                .content(corpo(hoje.plusDays(30).toString(), true)))
                .andExpect(status().isCreated()).andExpect(jsonPath("$.trabalhadorId").value(id))
                .andExpect(jsonPath("$.id").exists()).andExpect(jsonPath("$.registradaEm").exists());
        assertEquals(1, capacitacoes.count());
        mvc.perform(get(caminho(id))).andExpect(status().isOk())
                .andExpect(jsonPath("$[0].codigo").value("DEMO"));
        mvc.perform(get(caminho(id) + "/DEMO/situacao")).andExpect(status().isOk())
                .andExpect(jsonPath("$.situacao").value("VALIDA"))
                .andExpect(jsonPath("$.autorizacaoAcesso").value("NAO_AVALIADA"));
    }

    @Test void consultaVencidaNaoVerificadaEAusente() throws Exception {
        mvc.perform(get(caminho(id) + "/DEMO/situacao"))
                .andExpect(jsonPath("$.situacao").value("AUSENTE"));
        mvc.perform(post(caminho(id)).contentType(MediaType.APPLICATION_JSON)
                .content(corpo(hoje.minusDays(1).toString(), true))).andExpect(status().isCreated());
        mvc.perform(get(caminho(id) + "/DEMO/situacao"))
                .andExpect(jsonPath("$.situacao").value("VENCIDA"));
        mvc.perform(post(caminho(id)).contentType(MediaType.APPLICATION_JSON)
                .content(corpo(hoje.plusDays(30).toString(), false))).andExpect(status().isCreated());
        mvc.perform(get(caminho(id) + "/DEMO/situacao"))
                .andExpect(jsonPath("$.situacao").value("NAO_VERIFICADA"));
    }

    @Test void naoMisturaPessoasOuTiposDeCurso() throws Exception {
        String outro = cadastrarTrabalhador("COL-024");
        mvc.perform(post(caminho(id)).contentType(MediaType.APPLICATION_JSON)
                .content(corpo(hoje.plusDays(30).toString(), true))).andExpect(status().isCreated());
        mvc.perform(get(caminho(outro) + "/DEMO/situacao"))
                .andExpect(jsonPath("$.situacao").value("AUSENTE"));
        mvc.perform(get(caminho(id) + "/OUTRO/situacao"))
                .andExpect(jsonPath("$.situacao").value("AUSENTE"));
    }

    @Test void rejeitaCorposInvalidosSemGravar() throws Exception {
        for (String corpo : new String[]{"{}", "{\"codigo\":\"DEMO\",\"verificada\":null}",
                corpo(hoje.toString(), true).replace("\"DEMO\"", "\" \""),
                corpo("invalida", true), corpo(hoje.minusDays(20).toString(), true)}) {
            mvc.perform(post(caminho(id)).contentType(MediaType.APPLICATION_JSON).content(corpo))
                    .andExpect(status().isBadRequest());
        }
        assertEquals(0, capacitacoes.count());
    }

    @Test void trabalhadorInexistenteRetorna404() throws Exception {
        String caminho = caminho(UUID.randomUUID().toString());
        mvc.perform(get(caminho)).andExpect(status().isNotFound());
        mvc.perform(get(caminho + "/DEMO/situacao")).andExpect(status().isNotFound());
        mvc.perform(post(caminho).contentType(MediaType.APPLICATION_JSON)
                .content(corpo(hoje.toString(), true))).andExpect(status().isNotFound());
    }

    @Test void preservaCadastroERejeicaoDeMatriculaDuplicada() throws Exception {
        mvc.perform(get("/api/trabalhadores/" + id)).andExpect(status().isOk())
                .andExpect(jsonPath("$.matricula").value("COL-023"));
        mvc.perform(post("/api/trabalhadores").contentType(MediaType.APPLICATION_JSON)
                .content("{\"nome\":\"Teste\",\"matricula\":\"COL-023\",\"empresa\":\"Demo\"}"))
                .andExpect(status().isBadRequest());
        mvc.perform(post("/api/trabalhadores").contentType(MediaType.APPLICATION_JSON).content("{}"))
                .andExpect(status().isBadRequest());
    }
}
