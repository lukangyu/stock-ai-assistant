package com.personal.stock.service;

import com.personal.stock.config.StockEmailConfig;
import com.personal.stock.dto.DailyReport;
import com.personal.stock.dto.StockAnalysisResult;
import com.personal.stock.dto.NewsItem;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailService {
    
    private final JavaMailSender mailSender;
    private final StockEmailConfig emailConfig;
    private final TemplateEngine templateEngine;
    
    public void sendDailyReport(DailyReport report) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            helper.setFrom(emailConfig.getTo());
            helper.setTo(emailConfig.getTo());
            helper.setSubject("【股票助手】每日分析报告 - " + report.getDate());
            
            Context context = new Context();
            context.setVariable("report", report);
            context.setVariable("sendTime", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
            
            String htmlContent = templateEngine.process("daily-report", context);
            helper.setText(htmlContent, true);
            
            mailSender.send(message);
            log.info("Daily report email sent successfully");
        } catch (MessagingException e) {
            log.error("Failed to send daily report email", e);
        }
    }
    
    public void sendAlert(String title, String content) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            helper.setFrom(emailConfig.getTo());
            helper.setTo(emailConfig.getTo());
            helper.setSubject("【股票助手】预警通知 - " + title);
            
            Context context = new Context();
            context.setVariable("title", title);
            context.setVariable("content", content);
            context.setVariable("sendTime", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
            
            String htmlContent = templateEngine.process("alert", context);
            helper.setText(htmlContent, true);
            
            mailSender.send(message);
            log.info("Alert email sent successfully: {}", title);
        } catch (MessagingException e) {
            log.error("Failed to send alert email", e);
        }
    }
    
    public void sendStockAnalysis(StockAnalysisResult result) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            helper.setFrom(emailConfig.getTo());
            helper.setTo(emailConfig.getTo());
            helper.setSubject(String.format("【股票助手】%s(%s) 分析报告", result.getName(), result.getCode()));
            
            Context context = new Context();
            context.setVariable("stock", result);
            context.setVariable("sendTime", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
            
            String htmlContent = templateEngine.process("stock-analysis", context);
            helper.setText(htmlContent, true);
            
            mailSender.send(message);
            log.info("Stock analysis email sent: {}", result.getCode());
        } catch (MessagingException e) {
            log.error("Failed to send stock analysis email", e);
        }
    }
}
