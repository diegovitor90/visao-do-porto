package br.com.visaodoporto.backend.repository;

import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import br.com.visaodoporto.backend.entity.Capacitacao;

public interface CapacitacaoRepository extends JpaRepository<Capacitacao, UUID> {
    List<Capacitacao> findByTrabalhadorIdOrderByRegistradaEmDesc(UUID trabalhadorId);
    List<Capacitacao> findByTrabalhadorIdAndCodigoOrderByRegistradaEmDesc(UUID trabalhadorId, String codigo);
}
