package com.personal.stock.service;

import com.personal.stock.config.StockEmailConfig;
import com.personal.stock.dto.DailyReport;
import com.personal.stock.dto.StockAnalysisResult;
import com.personal.stock.dto.NewsItem;
import com.personal.stock.service.client.PythonServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.ArrayList;

@Slf4j
@Service
@RequiredArgsConstructor
public class DailyReportService {
    
    private final PythonServiceClient pythonClient;
    private final EmailService emailService;
    
    private static final List<String> WATCH_LIST = List.of(
        "600519", "000858", "000001", "600036", "601318"
    );
    
    @Scheduled(cron = "${stock.schedule.cron}")
    public void generateAndSendDailyReport() {
        log.info("Starting daily report generation...");
        
        try {
            List<StockAnalysisResult> recommendedStocks = pythonClient.analyzeStocks(WATCH_LIST);
            List<NewsItem> hotNews = pythonClient.getHotNews(10);
            List<String> alerts = checkWatchListAlerts();
            
            DailyReport report = DailyReport.builder()
                .date(LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")))
                .marketSummary(generateMarketSummary())
                .recommendedStocks(recommendedStocks)
                .hotNews(hotNews)
                .watchListAlerts(alerts)
                .build();
            
            emailService.sendDailyReport(report);
            log.info("Daily report sent successfully");
        } catch (Exception e) {
            log.error("Failed to generate daily report", e);
        }
    }
    
    public void analyzeAndSendStock(String code) {
        log.info("Analyzing stock: {}", code);
        
        try {
            StockAnalysisResult result = pythonClient.analyzeSingleStock(code);
            if (result != null) {
                emailService.sendStockAnalysis(result);
            }
        } catch (Exception e) {
            log.error("Failed to analyze stock: {}", code, e);
        }
    }
    
    private List<String> checkWatchListAlerts() {
        List<String> alerts = new ArrayList<>();
        return alerts;
    }
    
    private String generateMarketSummary() {
        return "今日A股市场整体表现平稳，主要指数窄幅震荡。" +
               "建议关注消费、科技板块的投资机会。";
    }
}
