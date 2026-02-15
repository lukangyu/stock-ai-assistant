package com.personal.stock.dto;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StockInfo {
    private String code;
    private String name;
    private Double currentPrice;
    private Double changePercent;
    private Double volume;
    private Double turnover;
    private Double high;
    private Double low;
    private Double open;
    private Double preClose;
    private LocalDateTime updateTime;
}
