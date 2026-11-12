
package br.com.visaodoporto.backend.service;

import br.com.visaodoporto.backend.entity.Trabalhador;
import br.com.visaodoporto.backend.repository.TrabalhadorRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class TrabalhadorServiceTest {

    private TrabalhadorRepository repository;
    private TrabalhadorService service;

    @BeforeEach
    void configurar() {
        repository = mock(TrabalhadorRepository.class);
        service = new TrabalhadorService(repository);
    }

    @Test
    void deveCadastrarTrabalhador() {

        when(repository.save(any(Trabalhador.class)))
            .thenAnswer(invocation -> invocation.getArgument(0));

        Trabalhador trabalhador = service.cadastrar(
            "João Silva",
            "PORTO-001",
            "Operadora Portuária A"
        );

        assertEquals("João Silva", trabalhador.getNome());
        assertEquals("PORTO-001", trabalhador.getMatricula());
        assertTrue(trabalhador.isAtivo());

        verify(repository).save(any(Trabalhador.class));
    }

    @Test
    void naoDeveCadastrarMatriculaDuplicada() {

        when(repository.existsByMatricula("PORTO-001"))
            .thenReturn(true);

        assertThrows(
            IllegalArgumentException.class,
            () -> service.cadastrar(
                "João Silva",
                "PORTO-001",
                "Operadora Portuária A"
            )
        );

        verify(repository, never()).save(any());
    }
}
