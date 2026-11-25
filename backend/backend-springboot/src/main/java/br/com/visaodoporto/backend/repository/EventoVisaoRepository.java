package br.com.visaodoporto.backend.repository;

import br.com.visaodoporto.backend.entity.EventoVisao;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import java.util.UUID;

public interface EventoVisaoRepository
        extends JpaRepository<EventoVisao, UUID>, JpaSpecificationExecutor<EventoVisao> {}
