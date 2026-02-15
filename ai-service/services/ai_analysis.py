from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    
    def __init__(self):
        self._model = None
    
    def get_recommendation(self, code: str, tech_analysis: Dict, news_sentiment: Dict) -> Dict[str, Any]:
        score = 0
        reasons = []
        
        trend = tech_analysis.get("trend", "")
        if "上涨" in trend:
            score += 30
            reasons.append(f"技术面：{trend}")
        elif "下跌" in trend:
            score -= 20
            reasons.append(f"技术面：{trend}")
        
        signals = tech_analysis.get("signals", [])
        for signal in signals:
            if "金叉" in signal or "买入" in signal or "超卖" in signal:
                score += 15
                reasons.append(signal)
            elif "死叉" in signal or "卖出" in signal or "超买" in signal:
                score -= 15
                reasons.append(signal)
        
        sentiment = news_sentiment.get("sentiment", "中性")
        sentiment_score = news_sentiment.get("score", 0.5)
        if sentiment == "正面":
            score += 20
            reasons.append(f"新闻情绪：正面({sentiment_score:.2f})")
        elif sentiment == "负面":
            score -= 15
            reasons.append(f"新闻情绪：负面({sentiment_score:.2f})")
        
        indicators = tech_analysis.get("indicators", {})
        rsi = indicators.get("rsi")
        if rsi:
            if rsi < 30:
                score += 10
                reasons.append(f"RSI超卖区域({rsi:.1f})，存在反弹机会")
            elif rsi > 70:
                score -= 10
                reasons.append(f"RSI超买区域({rsi:.1f})，注意回调风险")
        
        macd = indicators.get("macd")
        if macd and macd > 0:
            score += 5
        
        confidence = min(max((score + 50) / 100, 0.3), 0.95)
        
        if score >= 30:
            action = "BUY"
            risk = "中等偏低"
        elif score <= -20:
            action = "SELL"
            risk = "较高"
        else:
            action = "HOLD"
            risk = "中等"
        
        if not reasons:
            reasons.append("综合分析建议观望")
        
        return {
            "action": action,
            "confidence": confidence,
            "risk": risk,
            "reasons": reasons[:5],
            "score": score
        }
    
    def predict_trend(self, code: str, historical_data: List[Dict]) -> Dict[str, Any]:
        try:
            from prophet import Prophet
            import pandas as pd
            
            df = pd.DataFrame(historical_data)
            df = df.rename(columns={'date': 'ds', 'close': 'y'})
            
            model = Prophet(daily_seasonality=True)
            model.fit(df)
            
            future = model.make_future_dataframe(periods=7)
            forecast = model.predict(future)
            
            last_price = df['y'].iloc[-1]
            predicted_price = forecast['yhat'].iloc[-1]
            
            change_pct = (predicted_price - last_price) / last_price * 100
            
            if change_pct > 2:
                direction = "上涨"
            elif change_pct < -2:
                direction = "下跌"
            else:
                direction = "横盘"
            
            return {
                "direction": direction,
                "predicted_change": change_pct,
                "predicted_price": predicted_price,
                "confidence": 0.6
            }
            
        except Exception as e:
            logger.error(f"Prophet prediction failed: {e}")
            return {
                "direction": "未知",
                "predicted_change": 0,
                "predicted_price": 0,
                "confidence": 0
            }
