import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StockDataService:
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = 60
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache_time:
            return False
        return (datetime.now() - self._cache_time[key]).seconds < self._cache_ttl
    
    def get_realtime_quotes(self, codes: List[str]) -> List[Dict[str, Any]]:
        results = []
        try:
            df = ak.stock_zh_a_spot_em()
            
            for code in codes:
                stock_data = df[df['代码'] == code]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    results.append({
                        "code": code,
                        "name": row.get('名称', ''),
                        "currentPrice": float(row.get('最新价', 0)),
                        "changePercent": float(row.get('涨跌幅', 0)),
                        "volume": float(row.get('成交量', 0)),
                        "turnover": float(row.get('成交额', 0)),
                        "high": float(row.get('最高', 0)),
                        "low": float(row.get('最低', 0)),
                        "open": float(row.get('今开', 0)),
                        "preClose": float(row.get('昨收', 0)),
                        "updateTime": datetime.now().isoformat()
                    })
        except Exception as e:
            logger.error(f"Failed to get realtime quotes: {e}")
        
        return results
    
    def get_stock_quote(self, code: str) -> Optional[Dict[str, Any]]:
        quotes = self.get_realtime_quotes([code])
        return quotes[0] if quotes else None
    
    def get_hot_stocks(self, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        try:
            df = ak.stock_zh_a_spot_em()
            df = df.sort_values(by='成交额', ascending=False)
            
            for _, row in df.head(limit).iterrows():
                results.append({
                    "code": row.get('代码', ''),
                    "name": row.get('名称', ''),
                    "currentPrice": float(row.get('最新价', 0)),
                    "changePercent": float(row.get('涨跌幅', 0)),
                    "volume": float(row.get('成交量', 0)),
                    "turnover": float(row.get('成交额', 0)),
                    "high": float(row.get('最高', 0)),
                    "low": float(row.get('最低', 0)),
                    "open": float(row.get('今开', 0)),
                    "preClose": float(row.get('昨收', 0))
                })
        except Exception as e:
            logger.error(f"Failed to get hot stocks: {e}")
        
        return results
    
    def get_history(self, code: str, days: int = 30) -> List[Dict[str, Any]]:
        results = []
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                   start_date=start_date, end_date=end_date, adjust="qfq")
            
            df = df.tail(days)
            
            for _, row in df.iterrows():
                results.append({
                    "date": row.get('日期', '').strftime('%Y-%m-%d') if hasattr(row.get('日期', ''), 'strftime') else str(row.get('日期', '')),
                    "open": float(row.get('开盘', 0)),
                    "high": float(row.get('最高', 0)),
                    "low": float(row.get('最低', 0)),
                    "close": float(row.get('收盘', 0)),
                    "volume": float(row.get('成交量', 0)),
                    "turnover": float(row.get('成交额', 0)),
                    "changePercent": float(row.get('涨跌幅', 0))
                })
        except Exception as e:
            logger.error(f"Failed to get history for {code}: {e}")
        
        return results
    
    def screen_stocks(self, conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        try:
            df = ak.stock_zh_a_spot_em()
            
            if conditions.get("min_price"):
                df = df[df['最新价'] >= conditions["min_price"]]
            if conditions.get("max_price"):
                df = df[df['最新价'] <= conditions["max_price"]]
            if conditions.get("min_change"):
                df = df[df['涨跌幅'] >= conditions["min_change"]]
            if conditions.get("max_change"):
                df = df[df['涨跌幅'] <= conditions["max_change"]]
            if conditions.get("min_volume"):
                df = df[df['成交量'] >= conditions["min_volume"]]
            
            df = df.sort_values(by='成交额', ascending=False)
            limit = conditions.get("limit", 10)
            
            for _, row in df.head(limit).iterrows():
                results.append({
                    "code": row.get('代码', ''),
                    "name": row.get('名称', ''),
                    "currentPrice": float(row.get('最新价', 0)),
                    "changePercent": float(row.get('涨跌幅', 0)),
                    "volume": float(row.get('成交量', 0)),
                    "turnover": float(row.get('成交额', 0))
                })
        except Exception as e:
            logger.error(f"Failed to screen stocks: {e}")
        
        return results
