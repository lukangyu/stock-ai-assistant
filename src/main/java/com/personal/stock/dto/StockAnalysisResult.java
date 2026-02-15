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
public class StockAnalysisResult {
    private String code;
    private String name;
    private Double currentPrice;
    private String recommendation;
    private Double confidence;
    private List<String> reasons;
    private String trendDirection;
    private String riskLevel;
    private String newsSentiment;
    private String technicalAnalysis;
}
