import akshare as ak
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    
    def __init__(self):
        self._history_cache = {}
    
    def _get_history_df(self, code: str, days: int = 120) -> pd.DataFrame:
        cache_key = f"{code}_{days}"
        if cache_key in self._history_cache:
            cached_df, cached_time = self._history_cache[cache_key]
            if (datetime.now() - cached_time).seconds < 300:
                return cached_df
        
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                   start_date=start_date, end_date=end_date, adjust="qfq")
            
            self._history_cache[cache_key] = (df, datetime.now())
            return df
        except Exception as e:
            logger.error(f"Failed to get history for {code}: {e}")
            return pd.DataFrame()
    
    def analyze(self, code: str) -> Dict[str, Any]:
        df = self._get_history_df(code)
        if df.empty:
            return {"trend": "未知", "summary": "无法获取数据", "signals": []}
        
        df = self._calculate_indicators(df)
        
        trend = self._determine_trend(df)
        signals = self._generate_signals(df)
        summary = self._generate_summary(df, trend, signals)
        
        return {
            "trend": trend,
            "summary": summary,
            "signals": signals,
            "indicators": {
                "ma5": float(df['MA5'].iloc[-1]) if 'MA5' in df.columns else None,
                "ma10": float(df['MA10'].iloc[-1]) if 'MA10' in df.columns else None,
                "ma20": float(df['MA20'].iloc[-1]) if 'MA20' in df.columns else None,
                "rsi": float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else None,
                "macd": float(df['MACD'].iloc[-1]) if 'MACD' in df.columns else None
            }
        }
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        df['MA60'] = df['收盘'].rolling(window=60).mean()
        
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        ema12 = df['收盘'].ewm(span=12, adjust=False).mean()
        ema26 = df['收盘'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Histogram'] = df['MACD'] - df['Signal']
        
        low_min = df['最低'].rolling(window=9).min()
        high_max = df['最高'].rolling(window=9).max()
        df['K'] = 100 * (df['收盘'] - low_min) / (high_max - low_min)
        df['D'] = df['K'].rolling(window=3).mean()
        
        return df
    
    def _determine_trend(self, df: pd.DataFrame) -> str:
        if len(df) < 20:
            return "数据不足"
        
        last_close = df['收盘'].iloc[-1]
        ma5 = df['MA5'].iloc[-1]
        ma10 = df['MA10'].iloc[-1]
        ma20 = df['MA20'].iloc[-1]
        
        if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20):
            return "数据不足"
        
        if last_close > ma5 > ma10 > ma20:
            return "强势上涨"
        elif last_close > ma20 and ma5 > ma10:
            return "上涨趋势"
        elif last_close < ma5 < ma10 < ma20:
            return "弱势下跌"
        elif last_close < ma20 and ma5 < ma10:
            return "下跌趋势"
        else:
            return "横盘震荡"
    
    def _generate_signals(self, df: pd.DataFrame) -> List[str]:
        signals = []
        
        if len(df) < 20:
            return ["数据不足，无法生成信号"]
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        if 'MA5' in df.columns and 'MA20' in df.columns:
            if prev['MA5'] <= prev['MA20'] and last['MA5'] > last['MA20']:
                signals.append("金叉：MA5上穿MA20，买入信号")
            elif prev['MA5'] >= prev['MA20'] and last['MA5'] < last['MA20']:
                signals.append("死叉：MA5下穿MA20，卖出信号")
        
        if 'RSI' in df.columns:
            rsi = last['RSI']
            if rsi < 30:
                signals.append(f"RSI超卖({rsi:.1f})，可能反弹")
            elif rsi > 70:
                signals.append(f"RSI超买({rsi:.1f})，注意回调风险")
        
        if 'MACD' in df.columns and 'Signal' in df.columns:
            if prev['MACD'] <= prev['Signal'] and last['MACD'] > last['Signal']:
                signals.append("MACD金叉，看涨信号")
            elif prev['MACD'] >= prev['Signal'] and last['MACD'] < last['Signal']:
                signals.append("MACD死叉，看跌信号")
        
        if not signals:
            signals.append("暂无明显技术信号")
        
        return signals
    
    def _generate_summary(self, df: pd.DataFrame, trend: str, signals: List[str]) -> str:
        if len(df) < 2:
            return "数据不足"
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        change_pct = (last['收盘'] - prev['收盘']) / prev['收盘'] * 100
        
        summary = f"当前趋势：{trend}。"
        summary += f"最新收盘价{last['收盘']:.2f}，"
        
        if change_pct > 0:
            summary += f"上涨{change_pct:.2f}%。"
        else:
            summary += f"下跌{abs(change_pct):.2f}%。"
        
        if signals:
            summary += "技术信号：" + "；".join(signals[:2])
        
        return summary
