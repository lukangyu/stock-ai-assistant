import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    
    def __init__(self):
        self.required_columns = ['open', 'high', 'low', 'close', 'volume']
    
    def _validate_df(self, df: pd.DataFrame) -> bool:
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            logger.warning(f"Missing columns: {missing}")
            return False
        return True
    
    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._validate_df(df):
            return df
        
        df = df.copy()
        
        df = self.add_moving_averages(df)
        df = self.add_macd(df)
        df = self.add_rsi(df)
        df = self.add_kdj(df)
        df = self.add_bollinger_bands(df)
        df = self.add_atr(df)
        df = self.add_adx(df)
        df = self.add_obv(df)
        df = self.add_vwap(df)
        df = self.add_cci(df)
        df = self.add_williams_r(df)
        df = self.add_mfi(df)
        df = self.add_roc(df)
        df = self.add_aroon(df)
        df = self.add_ichimoku(df)
        
        return df
    
    def add_moving_averages(self, df: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        if periods is None:
            periods = [5, 10, 20, 60, 120, 250]
        
        df = df.copy()
        for period in periods:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
            df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        df['SMA_SIGNAL'] = self._sma_signal(df)
        
        return df
    
    def _sma_signal(self, df: pd.DataFrame) -> pd.Series:
        signal = pd.Series(0, index=df.index)
        
        if 'MA5' in df.columns and 'MA20' in df.columns:
            golden_cross = (df['MA5'] > df['MA20']) & (df['MA5'].shift(1) <= df['MA20'].shift(1))
            death_cross = (df['MA5'] < df['MA20']) & (df['MA5'].shift(1) >= df['MA20'].shift(1))
            
            signal[golden_cross] = 1
            signal[death_cross] = -1
        
        return signal
    
    def add_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        df = df.copy()
        
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_SIGNAL'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_HISTOGRAM'] = df['MACD'] - df['MACD_SIGNAL']
        
        df['MACD_SIGNAL_TYPE'] = self._macd_signal(df)
        
        return df
    
    def _macd_signal(self, df: pd.DataFrame) -> pd.Series:
        signal = pd.Series(0, index=df.index)
        
        if 'MACD' in df.columns and 'MACD_SIGNAL' in df.columns:
            golden_cross = (df['MACD'] > df['MACD_SIGNAL']) & (df['MACD'].shift(1) <= df['MACD_SIGNAL'].shift(1))
            death_cross = (df['MACD'] < df['MACD_SIGNAL']) & (df['MACD'].shift(1) >= df['MACD_SIGNAL'].shift(1))
            
            signal[golden_cross] = 1
            signal[death_cross] = -1
        
        return signal
    
    def add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df = df.copy()
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df['RSI_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['RSI'] < 30, 'RSI_SIGNAL'] = 1
        df.loc[df['RSI'] > 70, 'RSI_SIGNAL'] = -1
        
        return df
    
    def add_kdj(self, df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        df = df.copy()
        
        low_min = df['low'].rolling(window=n).min()
        high_max = df['high'].rolling(window=n).max()
        
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        
        df['K'] = rsv.ewm(alpha=1/m1, adjust=False).mean()
        df['D'] = df['K'].ewm(alpha=1/m2, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        df['KDJ_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[(df['K'] > df['D']) & (df['K'].shift(1) <= df['D'].shift(1)), 'KDJ_SIGNAL'] = 1
        df.loc[(df['K'] < df['D']) & (df['K'].shift(1) >= df['D'].shift(1)), 'KDJ_SIGNAL'] = -1
        
        return df
    
    def add_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        df = df.copy()
        
        df['BB_MIDDLE'] = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        df['BB_UPPER'] = df['BB_MIDDLE'] + (std * std_dev)
        df['BB_LOWER'] = df['BB_MIDDLE'] - (std * std_dev)
        df['BB_WIDTH'] = (df['BB_UPPER'] - df['BB_LOWER']) / df['BB_MIDDLE'] * 100
        df['BB_PERCENT'] = (df['close'] - df['BB_LOWER']) / (df['BB_UPPER'] - df['BB_LOWER'])
        
        df['BB_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['close'] < df['BB_LOWER'], 'BB_SIGNAL'] = 1
        df.loc[df['close'] > df['BB_UPPER'], 'BB_SIGNAL'] = -1
        
        return df
    
    def add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df = df.copy()
        
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift(1))
        low_close = abs(df['low'] - df['close'].shift(1))
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=period).mean()
        
        df['ATR_RATIO'] = df['ATR'] / df['close'] * 100
        
        return df
    
    def add_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df = df.copy()
        
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = self._true_range(df)
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (abs(minus_dm).rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        df['ADX'] = dx.rolling(window=period).mean()
        df['PLUS_DI'] = plus_di
        df['MINUS_DI'] = minus_di
        
        df['ADX_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[(df['PLUS_DI'] > df['MINUS_DI']) & (df['ADX'] > 25), 'ADX_SIGNAL'] = 1
        df.loc[(df['PLUS_DI'] < df['MINUS_DI']) & (df['ADX'] > 25), 'ADX_SIGNAL'] = -1
        
        return df
    
    def _true_range(self, df: pd.DataFrame) -> pd.Series:
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift(1))
        low_close = abs(df['low'] - df['close'].shift(1))
        
        return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    def add_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        direction = np.where(df['close'] > df['close'].shift(1), 1,
                            np.where(df['close'] < df['close'].shift(1), -1, 0))
        
        df['OBV'] = (direction * df['volume']).cumsum()
        df['OBV_MA'] = df['OBV'].rolling(window=20).mean()
        
        df['OBV_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[(df['OBV'] > df['OBV_MA']) & (df['OBV'].shift(1) <= df['OBV_MA'].shift(1)), 'OBV_SIGNAL'] = 1
        df.loc[(df['OBV'] < df['OBV_MA']) & (df['OBV'].shift(1) >= df['OBV_MA'].shift(1)), 'OBV_SIGNAL'] = -1
        
        return df
    
    def add_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        df['VWAP'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        
        df['VWAP_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['close'] > df['VWAP'], 'VWAP_SIGNAL'] = 1
        df.loc[df['close'] < df['VWAP'], 'VWAP_SIGNAL'] = -1
        
        return df
    
    def add_cci(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        df = df.copy()
        
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        df['CCI'] = (tp - sma) / (0.015 * mad)
        
        df['CCI_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['CCI'] < -100, 'CCI_SIGNAL'] = 1
        df.loc[df['CCI'] > 100, 'CCI_SIGNAL'] = -1
        
        return df
    
    def add_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df = df.copy()
        
        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        
        df['WILLIAMS_R'] = (high_max - df['close']) / (high_max - low_min) * -100
        
        df['WR_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['WILLIAMS_R'] < -80, 'WR_SIGNAL'] = 1
        df.loc[df['WILLIAMS_R'] > -20, 'WR_SIGNAL'] = -1
        
        return df
    
    def add_mfi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df = df.copy()
        
        tp = (df['high'] + df['low'] + df['close']) / 3
        mf = tp * df['volume']
        
        positive_mf = pd.Series(0.0, index=df.index)
        negative_mf = pd.Series(0.0, index=df.index)
        
        positive_mf[tp > tp.shift(1)] = mf[tp > tp.shift(1)]
        negative_mf[tp < tp.shift(1)] = mf[tp < tp.shift(1)]
        
        positive_sum = positive_mf.rolling(window=period).sum()
        negative_sum = negative_mf.rolling(window=period).sum()
        
        mfi_ratio = positive_sum / negative_sum
        df['MFI'] = 100 - (100 / (1 + mfi_ratio))
        
        df['MFI_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['MFI'] < 20, 'MFI_SIGNAL'] = 1
        df.loc[df['MFI'] > 80, 'MFI_SIGNAL'] = -1
        
        return df
    
    def add_roc(self, df: pd.DataFrame, period: int = 12) -> pd.DataFrame:
        df = df.copy()
        
        df['ROC'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
        
        df['ROC_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['ROC'] > 0, 'ROC_SIGNAL'] = 1
        df.loc[df['ROC'] < 0, 'ROC_SIGNAL'] = -1
        
        return df
    
    def add_aroon(self, df: pd.DataFrame, period: int = 25) -> pd.DataFrame:
        df = df.copy()
        
        aroon_up = df['high'].rolling(window=period + 1).apply(lambda x: (period - x.argmax()) / period * 100)
        aroon_down = df['low'].rolling(window=period + 1).apply(lambda x: (period - x.argmin()) / period * 100)
        
        df['AROON_UP'] = aroon_up
        df['AROON_DOWN'] = aroon_down
        df['AROON_OSCILLATOR'] = aroon_up - aroon_down
        
        df['AROON_SIGNAL'] = pd.Series(0, index=df.index)
        df.loc[df['AROON_OSCILLATOR'] > 50, 'AROON_SIGNAL'] = 1
        df.loc[df['AROON_OSCILLATOR'] < -50, 'AROON_SIGNAL'] = -1
        
        return df
    
    def add_ichimoku(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        tenkan_high = df['high'].rolling(window=9).max()
        tenkan_low = df['low'].rolling(window=9).min()
        df['ICHIMOKU_TENKAN'] = (tenkan_high + tenkan_low) / 2
        
        kijun_high = df['high'].rolling(window=26).max()
        kijun_low = df['low'].rolling(window=26).min()
        df['ICHIMOKU_KIJUN'] = (kijun_high + kijun_low) / 2
        
        df['ICHIMOKU_SENKOU_A'] = ((df['ICHIMOKU_TENKAN'] + df['ICHIMOKU_KIJUN']) / 2).shift(26)
        
        senkou_b_high = df['high'].rolling(window=52).max()
        senkou_b_low = df['low'].rolling(window=52).min()
        df['ICHIMOKU_SENKOU_B'] = ((senkou_b_high + senkou_b_low) / 2).shift(26)
        
        df['ICHIMOKU_CHIKOU'] = df['close'].shift(-26)
        
        df['ICHIMOKU_SIGNAL'] = pd.Series(0, index=df.index)
        above_cloud = (df['close'] > df['ICHIMOKU_SENKOU_A']) & (df['close'] > df['ICHIMOKU_SENKOU_B'])
        below_cloud = (df['close'] < df['ICHIMOKU_SENKOU_A']) & (df['close'] < df['ICHIMOKU_SENKOU_B'])
        df.loc[above_cloud, 'ICHIMOKU_SIGNAL'] = 1
        df.loc[below_cloud, 'ICHIMOKU_SIGNAL'] = -1
        
        return df
    
    def get_indicator_summary(self, df: pd.DataFrame) -> Dict:
        if df.empty:
            return {}
        
        last = df.iloc[-1]
        summary = {
            'trend_indicators': {},
            'momentum_indicators': {},
            'volatility_indicators': {},
            'volume_indicators': {},
            'signals': {}
        }
        
        for col in ['MA5', 'MA10', 'MA20', 'MA60']:
            if col in df.columns:
                summary['trend_indicators'][col] = float(last[col]) if pd.notna(last[col]) else None
        
        for col in ['MACD', 'MACD_SIGNAL', 'MACD_HISTOGRAM']:
            if col in df.columns:
                summary['momentum_indicators'][col] = float(last[col]) if pd.notna(last[col]) else None
        
        for col in ['RSI', 'K', 'D', 'J', 'CCI', 'WILLIAMS_R', 'MFI', 'ROC']:
            if col in df.columns:
                summary['momentum_indicators'][col] = float(last[col]) if pd.notna(last[col]) else None
        
        for col in ['BB_UPPER', 'BB_LOWER', 'BB_WIDTH', 'ATR', 'ADX']:
            if col in df.columns:
                summary['volatility_indicators'][col] = float(last[col]) if pd.notna(last[col]) else None
        
        for col in ['OBV', 'VWAP']:
            if col in df.columns:
                summary['volume_indicators'][col] = float(last[col]) if pd.notna(last[col]) else None
        
        signal_cols = [col for col in df.columns if col.endswith('_SIGNAL')]
        for col in signal_cols:
            summary['signals'][col] = int(last[col]) if pd.notna(last[col]) else 0
        
        return summary
