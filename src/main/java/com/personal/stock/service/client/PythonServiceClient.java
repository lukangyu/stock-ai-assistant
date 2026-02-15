package com.personal.stock.service.client;

import com.personal.stock.config.PythonServiceConfig;
import com.personal.stock.dto.StockAnalysisResult;
import com.personal.stock.dto.NewsItem;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class PythonServiceClient {
    
    private final PythonServiceConfig config;
    private final WebClient.Builder webClientBuilder;
    
    public List<StockAnalysisResult> analyzeStocks(List<String> codes) {
        WebClient client = webClientBuilder.baseUrl(config.getUrl()).build();
        
        try {
            @SuppressWarnings("unchecked")
            List<StockAnalysisResult> results = client.post()
                .uri("/api/analyze/stocks")
                .bodyValue(Map.of("codes", codes))
                .retrieve()
                .bodyToMono(List.class)
                .block();
            return results;
        } catch (Exception e) {
            log.error("Failed to analyze stocks via Python service", e);
            return List.of();
        }
    }
    
    public StockAnalysisResult analyzeSingleStock(String code) {
        WebClient client = webClientBuilder.baseUrl(config.getUrl()).build();
        
        try {
            return client.get()
                .uri("/api/analyze/stock/{code}", code)
                .retrieve()
                .bodyToMono(StockAnalysisResult.class)
                .block();
        } catch (Exception e) {
            log.error("Failed to analyze stock: {}", code, e);
            return null;
        }
    }
    
    public List<NewsItem> getHotNews(int limit) {
        WebClient client = webClientBuilder.baseUrl(config.getUrl()).build();
        
        try {
            @SuppressWarnings("unchecked")
            List<NewsItem> news = client.get()
                .uri(uriBuilder -> uriBuilder
                    .path("/api/news/hot")
                    .queryParam("limit", limit)
                    .build())
                .retrieve()
                .bodyToMono(List.class)
                .block();
            return news;
        } catch (Exception e) {
            log.error("Failed to get hot news", e);
            return List.of();
        }
    }
    
    public List<StockAnalysisResult> screenStocks(Map<String, Object> conditions) {
        WebClient client = webClientBuilder.baseUrl(config.getUrl()).build();
        
        try {
            @SuppressWarnings("unchecked")
            List<StockAnalysisResult> results = client.post()
                .uri("/api/screen/stocks")
                .bodyValue(conditions)
                .retrieve()
                .bodyToMono(List.class)
                .block();
            return results;
        } catch (Exception e) {
            log.error("Failed to screen stocks", e);
            return List.of();
        }
    }
}
