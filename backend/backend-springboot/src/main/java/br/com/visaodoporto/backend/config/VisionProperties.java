package br.com.visaodoporto.backend.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import java.time.Duration;

@ConfigurationProperties("visao.api")
public record VisionProperties(String url, Duration conexaoTimeout, Duration leituraTimeout) {}
