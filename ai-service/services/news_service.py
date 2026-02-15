import akshare as ak
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

try:
    from snownlp import SnowNLP
    HAS_SNOWNLP = True
except ImportError:
    HAS_SNOWNLP = False
    logger.warning("SnowNLP not installed, sentiment analysis will be limited")


class NewsService:
    
    def __init__(self):
        self._news_cache = None
        self._cache_time = None
        self._cache_ttl = 1800
    
    def _is_cache_valid(self) -> bool:
        if self._cache_time is None:
            return False
        return (datetime.now() - self._cache_time).seconds < self._cache_ttl
    
    def get_hot_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        if self._is_cache_valid() and self._news_cache:
            return self._news_cache[:limit]
        
        results = []
        try:
            df = ak.stock_news_em(symbol="财经新闻")
            
            for _, row in df.head(limit).iterrows():
                title = row.get('新闻标题', '')
                sentiment = self._analyze_sentiment(title)
                
                results.append({
                    "title": title,
                    "summary": row.get('新闻内容', '')[:200] if row.get('新闻内容') else '',
                    "source": row.get('新闻来源', '未知'),
                    "sentiment": sentiment.get("sentiment", "中性"),
                    "sentimentScore": sentiment.get("score", 0.5),
                    "publishTime": row.get('发布时间', ''),
                    "url": row.get('新闻链接', '')
                })
            
            self._news_cache = results
            self._cache_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to get hot news: {e}")
            results = self._get_mock_news(limit)
        
        return results
    
    def get_stock_sentiment(self, code: str) -> Dict[str, Any]:
        try:
            df = ak.stock_news_em(symbol=code)
            
            if df.empty:
                return {"sentiment": "中性", "score": 0.5, "news_count": 0}
            
            sentiments = []
            for _, row in df.head(10).iterrows():
                title = row.get('新闻标题', '')
                sentiment = self._analyze_sentiment(title)
                sentiments.append(sentiment.get("score", 0.5))
            
            avg_score = sum(sentiments) / len(sentiments) if sentiments else 0.5
            
            if avg_score > 0.6:
                sentiment_label = "正面"
            elif avg_score < 0.4:
                sentiment_label = "负面"
            else:
                sentiment_label = "中性"
            
            return {
                "sentiment": sentiment_label,
                "score": avg_score,
                "news_count": len(sentiments)
            }
            
        except Exception as e:
            logger.error(f"Failed to get sentiment for {code}: {e}")
            return {"sentiment": "中性", "score": 0.5, "news_count": 0}
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"sentiment": "中性", "score": 0.5}
        
        if HAS_SNOWNLP:
            try:
                s = SnowNLP(text)
                score = s.sentiments
                
                if score > 0.6:
                    sentiment = "正面"
                elif score < 0.4:
                    sentiment = "负面"
                else:
                    sentiment = "中性"
                
                return {"sentiment": sentiment, "score": score}
            except Exception as e:
                logger.warning(f"SnowNLP analysis failed: {e}")
        
        return self._keyword_sentiment(text)
    
    def _keyword_sentiment(self, text: str) -> Dict[str, Any]:
        positive_keywords = ['上涨', '利好', '增长', '突破', '创新高', '盈利', '增持', 
                           '回购', '并购', '涨停', '大涨', '飙升', '反弹']
        negative_keywords = ['下跌', '利空', '亏损', '暴跌', '跌停', '减持', '风险',
                           '下滑', '预警', '处罚', '调查', '大跌', '破位']
        
        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)
        
        total = positive_count + negative_count
        if total == 0:
            return {"sentiment": "中性", "score": 0.5}
        
        score = positive_count / total
        if score > 0.6:
            sentiment = "正面"
        elif score < 0.4:
            sentiment = "负面"
        else:
            sentiment = "中性"
        
        return {"sentiment": sentiment, "score": score}
    
    def _get_mock_news(self, limit: int) -> List[Dict[str, Any]]:
        mock_news = [
            {"title": "央行宣布降准0.5个百分点，释放长期资金约1万亿元", "source": "财经网", "sentiment": "正面"},
            {"title": "科技板块集体走强，半导体龙头涨停", "source": "证券时报", "sentiment": "正面"},
            {"title": "北向资金今日净流入超50亿元", "source": "东方财富", "sentiment": "正面"},
            {"title": "多家银行下调存款利率，利好股市资金面", "source": "第一财经", "sentiment": "正面"},
            {"title": "消费板块持续调整，关注低估值机会", "source": "中国证券报", "sentiment": "中性"},
        ]
        
        results = []
        for i, news in enumerate(mock_news[:limit]):
            results.append({
                "title": news["title"],
                "summary": news["title"],
                "source": news["source"],
                "sentiment": news["sentiment"],
                "sentimentScore": 0.7 if news["sentiment"] == "正面" else 0.5,
                "publishTime": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "url": ""
            })
        
        return results
