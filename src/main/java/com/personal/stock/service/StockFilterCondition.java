package com.personal.stock.service;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StockFilterCondition {
    private Double minPrice;
    private Double maxPrice;
    private Double minChangePercent;
    private Double maxChangePercent;
    private Double minVolume;
    private Double minTurnover;
    private String industry;
}
