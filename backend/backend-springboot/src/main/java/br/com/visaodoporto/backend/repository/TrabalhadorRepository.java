
package br.com.visaodoporto.backend.repository;

import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

import br.com.visaodoporto.backend.entity.Trabalhador;

public interface TrabalhadorRepository
        extends JpaRepository<Trabalhador, UUID> {

    Optional<Trabalhador> findByMatricula(String matricula);

    boolean existsByMatricula(String matricula);
}
