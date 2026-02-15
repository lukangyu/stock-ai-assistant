package com.personal.stock.dto;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NewsItem {
    private String title;
    private String summary;
    private String source;
    private String sentiment;
    private Double sentimentScore;
    private LocalDateTime publishTime;
    private String url;
}
