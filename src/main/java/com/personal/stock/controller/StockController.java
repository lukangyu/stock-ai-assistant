package com.personal.stock.controller;

import com.personal.stock.dto.StockAnalysisResult;
import com.personal.stock.service.DailyReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class StockController {
    
    private final DailyReportService dailyReportService;
    
    @PostMapping("/report/send")
    public String sendDailyReport() {
        dailyReportService.generateAndSendDailyReport();
        return "Daily report sent successfully";
    }
    
    @GetMapping("/analyze/{code}")
    public StockAnalysisResult analyzeStock(@PathVariable String code) {
        dailyReportService.analyzeAndSendStock(code);
        return StockAnalysisResult.builder()
            .code(code)
            .name("分析中...")
            .recommendation("PROCESSING")
            .build();
    }
    
    @GetMapping("/health")
    public String health() {
        return "OK";
    }
}
