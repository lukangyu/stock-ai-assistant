package com.personal.stock;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class StockAssistantApplication {
    public static void main(String[] args) {
        SpringApplication.run(StockAssistantApplication.class, args);
    }
}
