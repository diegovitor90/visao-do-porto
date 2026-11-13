package br.com.visaodoporto.backend.config;

import java.time.Clock;
import java.time.ZoneId;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TempoConfig {
    @Bean
    Clock relogio() { return Clock.system(ZoneId.of("America/Sao_Paulo")); }
}
