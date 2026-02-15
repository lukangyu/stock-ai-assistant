package com.personal.stock.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Data
@Configuration
@ConfigurationProperties(prefix = "python.service")
public class PythonServiceConfig {
    private String url = "http://localhost:8000";
}
