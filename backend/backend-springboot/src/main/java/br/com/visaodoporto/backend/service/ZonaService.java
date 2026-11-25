package br.com.visaodoporto.backend.service;

import br.com.visaodoporto.backend.dto.vision.ZonaDto;
import br.com.visaodoporto.backend.dto.vision.ZonaDto.Epi;
import br.com.visaodoporto.backend.entity.Zona;
import br.com.visaodoporto.backend.repository.ZonaRepository;
import jakarta.validation.Validator;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.web.server.ResponseStatusException;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.List;
import java.util.UUID;

@Service
public class ZonaService {
    private static final double EPS = 1e-10;
    private final ZonaRepository repository;
    private final ObjectMapper json;
    private final Validator validator;
    private final TransactionTemplate transaction;
    private final double areaMinima;

    public ZonaService(ZonaRepository repository, ObjectMapper json, Validator validator,
                       PlatformTransactionManager manager, @Value("${visao.zonas.area-minima:0.0001}") double areaMinima) {
        this.repository = repository;
        this.json = json;
        this.validator = validator;
        this.transaction = new TransactionTemplate(manager);
        this.areaMinima = areaMinima;
    }

    public List<ZonaDto> listar(String camera) {
        return repository.findByCameraIdOrderById(camera).stream().filter(Zona::isAtiva).map(this::dto).toList();
    }

    public synchronized List<ZonaDto> substituir(String camera, List<ZonaDto> novas) {
        return transaction.execute(status -> {
            var atuais = new HashMap<UUID, Zona>();
            for (var zona : repository.findByCameraIdOrderById(camera)) {
                atuais.put(zona.getId(), zona);
            }
            for (var zona : novas) {
                if (zona == null || !validator.validate(zona).isEmpty()) {
                    throw invalida("Campos da zona inválidos.");
                }
                validarPoligono(zona.polygon());
                Zona entity = zona.zoneId() == null ? new Zona(camera, zona.ruleId()) : atuais.remove(zona.zoneId());
                if (entity == null) {
                    throw invalida("zone_id repetido ou inexistente nesta câmera.");
                }
                if (zona.zoneId() != null && zona.ruleId() != null && !entity.getRuleId().equals(zona.ruleId())) {
                    throw invalida("rule_id de uma zona existente é fixo.");
                }
                List<Epi> epis = zona.requiredPpe() == null ? List.of()
                        : zona.requiredPpe().stream().distinct().sorted().toList();
                entity.atualizar(zona.nome(), json.writeValueAsString(zona.polygon()),
                        json.writeValueAsString(epis), zona.ruleType(), !Boolean.FALSE.equals(zona.ativa()));
                repository.save(entity);
            }
            atuais.values().forEach(Zona::desativar);
            return listar(camera);
        });
    }

    private ZonaDto dto(Zona zona) {
        return new ZonaDto(zona.getId(), zona.getNome(),
                json.readValue(zona.getPolygon(), new TypeReference<List<List<Double>>>() {}),
                json.readValue(zona.getRequiredPpe(), new TypeReference<List<Epi>>() {}),
                zona.getRuleType(), zona.getRuleId(), zona.getRuleVersion(), zona.isAtiva());
    }

    private void validarPoligono(List<List<Double>> polygon) {
        for (var vertex : polygon) {
            if (vertex == null || vertex.size() != 2 || vertex.stream().anyMatch(
                    n -> n == null || !Double.isFinite(n) || n < 0 || n > 1)) {
                throw invalida("Vértices devem ter duas coordenadas normalizadas.");
            }
        }
        int n = polygon.size();
        double area = 0;
        for (int i = 0; i < n; i++) {
            var a = polygon.get(i);
            var b = polygon.get((i + 1) % n);
            var c = polygon.get((i + 2) % n);
            double dot = (a.get(0) - b.get(0)) * (c.get(0) - b.get(0))
                    + (a.get(1) - b.get(1)) * (c.get(1) - b.get(1));
            if (a.equals(b) || (Math.abs(cross(a, b, c)) <= EPS && dot > EPS)) {
                throw invalida("O polígono tem lados degenerados ou sobrepostos.");
            }
            area += a.get(0) * b.get(1) - b.get(0) * a.get(1);
            for (int j = i + 2; j < n; j++) {
                if (i == 0 && j == n - 1) continue;
                if (intersectam(a, b, polygon.get(j), polygon.get((j + 1) % n))) {
                    throw invalida("Os lados do polígono não podem se cruzar.");
                }
            }
        }
        if (Math.abs(area) / 2 < areaMinima || Math.abs(area) <= EPS) {
            throw invalida("Área do polígono inferior ao mínimo.");
        }
    }

    private boolean intersectam(List<Double> a, List<Double> b, List<Double> c, List<Double> d) {
        for (int axis = 0; axis < 2; axis++) {
            if (Math.max(a.get(axis), b.get(axis)) + EPS < Math.min(c.get(axis), d.get(axis))
                    || Math.max(c.get(axis), d.get(axis)) + EPS < Math.min(a.get(axis), b.get(axis))) {
                return false;
            }
        }
        return orientation(cross(a, b, c)) * orientation(cross(a, b, d)) <= 0
                && orientation(cross(c, d, a)) * orientation(cross(c, d, b)) <= 0;
    }

    private int orientation(double cross) {
        if (Math.abs(cross) <= EPS) return 0;
        return cross > 0 ? 1 : -1;
    }

    private double cross(List<Double> a, List<Double> b, List<Double> c) {
        return (b.get(0) - a.get(0)) * (c.get(1) - a.get(1))
                - (b.get(1) - a.get(1)) * (c.get(0) - a.get(0));
    }

    private ResponseStatusException invalida(String mensagem) {
        return new ResponseStatusException(HttpStatus.BAD_REQUEST, mensagem);
    }
}
