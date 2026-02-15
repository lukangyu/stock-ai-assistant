from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import json

from services.stock_data import StockDataService
from services.technical_analysis import TechnicalAnalysisService
from services.news_service import NewsService
from services.tongyi_service import TongyiAnalysisService
from services.feature_engineering.technical_indicators import TechnicalIndicators
from services.visualization.chart_builder import StockVisualizationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Stock AI Assistant",
    version="2.0.0",
    description="AI-powered stock analysis with Tongyi Qwen"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stock_service = StockDataService()
tech_service = TechnicalAnalysisService()
news_service = NewsService()
tongyi_service = TongyiAnalysisService()
tech_indicators = TechnicalIndicators()
viz_engine = StockVisualizationEngine()


class StockAnalysisRequest(BaseModel):
    codes: List[str]


class StockScreenRequest(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_change: Optional[float] = None
    max_change: Optional[float] = None
    min_volume: Optional[float] = None
    industry: Optional[str] = None
    limit: Optional[int] = 10


class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "ai_provider": "tongyi_qwen",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/quotes/realtime")
async def get_realtime_quotes(codes: str = ""):
    try:
        code_list = [c.strip() for c in codes.split(",") if c.strip()]
        if not code_list:
            code_list = ["600519", "000858", "000001", "600036", "601318"]
        
        quotes = stock_service.get_realtime_quotes(code_list)
        return {"data": quotes, "count": len(quotes)}
    except Exception as e:
        logger.error(f"Failed to get realtime quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyze/stock/{code}")
async def analyze_single_stock(code: str):
    try:
        quote = stock_service.get_stock_quote(code)
        if not quote:
            raise HTTPException(status_code=404, detail=f"Stock {code} not found")
        
        history = stock_service.get_history(code, 120)
        if not history:
            raise HTTPException(status_code=404, detail=f"No history data for {code}")
        
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        df = tech_indicators.add_all_indicators(df)
        
        tech_analysis = tech_service.analyze(code)
        news_sentiment = news_service.get_stock_sentiment(code)
        
        indicators_summary = tech_indicators.get_indicator_summary(df)
        
        historical_summary = f"""
        近30日涨跌幅: {(df['close'].iloc[-1] / df['close'].iloc[-30] - 1) * 100:.2f}%
        近60日涨跌幅: {(df['close'].iloc[-1] / df['close'].iloc[-60] - 1) * 100:.2f}%
        30日最高价: {df['high'].iloc[-30:].max():.2f}
        30日最低价: {df['low'].iloc[-30:].min():.2f}
        平均成交量: {df['volume'].iloc[-20:].mean():.0f}
        """
        
        result = tongyi_service.analyze_stock(
            code=code,
            name=quote.get('name', ''),
            current_price=quote.get('currentPrice', 0),
            tech_indicators=indicators_summary,
            news_sentiment=news_sentiment,
            historical_summary=historical_summary
        )
        
        result['indicators'] = indicators_summary
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to analyze stock {code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/stocks")
async def analyze_multiple_stocks(request: StockAnalysisRequest):
    try:
        results = []
        for code in request.codes:
            try:
                quote = stock_service.get_stock_quote(code)
                if not quote:
                    continue
                
                history = stock_service.get_history(code, 60)
                if not history:
                    continue
                
                df = pd.DataFrame(history)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                df = tech_indicators.add_all_indicators(df)
                
                tech_analysis = tech_service.analyze(code)
                news_sentiment = news_service.get_stock_sentiment(code)
                indicators_summary = tech_indicators.get_indicator_summary(df)
                
                result = tongyi_service.analyze_stock(
                    code=code,
                    name=quote.get('name', ''),
                    current_price=quote.get('currentPrice', 0),
                    tech_indicators=indicators_summary,
                    news_sentiment=news_sentiment
                )
                
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to analyze {code}: {e}")
                continue
        
        results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return results
    except Exception as e:
        logger.error(f"Failed to analyze stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features/technical/{code}")
async def get_technical_features(code: str, days: int = 120):
    try:
        history = stock_service.get_history(code, days)
        if not history:
            raise HTTPException(status_code=404, detail=f"No history data for {code}")
        
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        df = tech_indicators.add_all_indicators(df)
        
        return {
            "code": code,
            "indicators": tech_indicators.get_indicator_summary(df),
            "latest_data": df.tail(10).to_dict()
        }
    except Exception as e:
        logger.error(f"Failed to get technical features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visualization/chart/{code}")
async def get_stock_chart(code: str, days: int = 120):
    try:
        history = stock_service.get_history(code, days)
        if not history:
            raise HTTPException(status_code=404, detail=f"No history data for {code}")
        
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        df = tech_indicators.add_all_indicators(df)
        
        chart_data = viz_engine.create_candlestick_chart(
            df, 
            title=f"{code} Stock Chart",
            show_volume=True,
            show_ma=True,
            show_macd=True,
            show_rsi=True
        )
        
        return chart_data
    except Exception as e:
        logger.error(f"Failed to create chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visualization/dashboard/{code}")
async def get_analysis_dashboard(code: str):
    try:
        history = stock_service.get_history(code, 120)
        if not history:
            raise HTTPException(status_code=404, detail=f"No history data for {code}")
        
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        df = tech_indicators.add_all_indicators(df)
        
        charts = {
            'Price Chart': viz_engine.create_candlestick_chart(df, title=f"{code} Price"),
            'Volume Analysis': viz_engine.create_volume_analysis_chart(df, title=f"{code} Volume")
        }
        
        html = viz_engine.create_dashboard_html(charts, title=f"{code} Analysis Dashboard")
        
        return HTMLResponse(content=html)
    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        response = tongyi_service.chat(request.question, request.context)
        return {
            "question": request.question,
            "answer": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/hot")
async def get_hot_news(limit: int = 10):
    try:
        news = news_service.get_hot_news(limit)
        return news
    except Exception as e:
        logger.error(f"Failed to get hot news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/analyze")
async def analyze_news(title: str):
    try:
        result = tongyi_service.analyze_news_impact(title)
        return result
    except Exception as e:
        logger.error(f"Failed to analyze news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/screen/stocks")
async def screen_stocks(request: StockScreenRequest):
    try:
        conditions = {
            "min_price": request.min_price,
            "max_price": request.max_price,
            "min_change": request.min_change,
            "max_change": request.max_change,
            "min_volume": request.min_volume,
            "industry": request.industry,
            "limit": request.limit
        }
        results = stock_service.screen_stocks(conditions)
        return results
    except Exception as e:
        logger.error(f"Failed to screen stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{code}/history")
async def get_stock_history(code: str, days: int = 30):
    try:
        history = stock_service.get_history(code, days)
        return {"data": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to get history for {code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/summary")
async def get_market_summary():
    try:
        hot_stocks = stock_service.get_hot_stocks(10)
        
        market_data = {
            "hot_stocks_count": len(hot_stocks),
            "top_gainers": [s for s in hot_stocks if s.get('changePercent', 0) > 3][:5],
            "top_losers": [s for s in hot_stocks if s.get('changePercent', 0) < -3][:5],
            "avg_turnover": np.mean([s.get('turnover', 0) for s in hot_stocks]) if hot_stocks else 0
        }
        
        summary = tongyi_service.generate_market_summary(market_data)
        
        return {
            "summary": summary,
            "market_data": market_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get market summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
