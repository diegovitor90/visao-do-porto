package br.com.visaodoporto.backend.service;

import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import br.com.visaodoporto.backend.entity.Trabalhador;
import br.com.visaodoporto.backend.repository.TrabalhadorRepository;

@Service
@Transactional(readOnly = true)
public class TrabalhadorService {
    private final TrabalhadorRepository repository;

    public TrabalhadorService(TrabalhadorRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public Trabalhador cadastrar(String nome, String matricula, String empresa) {
        if (nome == null || nome.isBlank() || matricula == null || matricula.isBlank()
                || empresa == null || empresa.isBlank()) {
            throw new IllegalArgumentException("Nome, matrícula e empresa são obrigatórios.");
        }
        String codigo = matricula.strip();
        if (repository.existsByMatricula(codigo)) {
            throw new IllegalArgumentException("Matrícula já cadastrada.");
        }
        return repository.save(new Trabalhador(nome.strip(), codigo, empresa.strip()));
    }

    public List<Trabalhador> listar() { return repository.findAll(); }

    public Trabalhador buscarPorId(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Trabalhador não encontrado."));
    }
}
