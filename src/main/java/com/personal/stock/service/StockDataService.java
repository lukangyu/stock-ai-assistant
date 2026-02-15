package com.personal.stock.service;

import com.personal.stock.dto.StockInfo;
import java.util.List;

public interface StockDataService {
    List<StockInfo> getRealtimeQuotes(List<String> codes);
    StockInfo getStockInfo(String code);
    List<StockInfo> getHotStocks(int limit);
    List<StockInfo> getStocksByCondition(StockFilterCondition condition);
}
