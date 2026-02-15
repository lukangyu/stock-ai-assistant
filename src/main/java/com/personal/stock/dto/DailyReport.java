package com.personal.stock.dto;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DailyReport {
    private String date;
    private String marketSummary;
    private List<StockAnalysisResult> recommendedStocks;
    private List<NewsItem> hotNews;
    private List<String> watchListAlerts;
}
