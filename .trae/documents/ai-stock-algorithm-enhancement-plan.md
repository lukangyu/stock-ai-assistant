# AI股票推荐算法增强计划

## 📋 项目概述

### 目标
增强现有股票分析与推荐AI助手，集成先进的量化分析方法论和机器学习技术，提供更精准的趋势预测和可视化展示。

### 当前状态分析
- **现有算法**: 简单的多因子加权评分模型
- **技术指标**: MA、MACD、RSI、KDJ（基础实现）
- **情感分析**: SnowNLP关键词匹配
- **预测能力**: Prophet时序预测（未启用）

---

## 🎯 增强方案架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Enhanced AI Stock Recommendation System               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Data Layer  │  │ Feature Eng │  │  ML Models  │  │  Ensemble   │        │
│  │  数据获取层  │→│  特征工程层  │→│  模型层     │→│  集成层     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│         ↓                ↓                ↓                ↓               │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                    Visualization & Reporting                     │       │
│  │                      可视化与报告层                              │       │
│  └─────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Phase 1: 高级特征工程 (Feature Engineering)

### 1.1 技术指标扩展

参考项目: [talipp](https://github.com/nardew/talipp), [pandas_talib](https://github.com/femtotrader/pandas_talib)

| 类别 | 指标 | 说明 | 权重 |
|------|------|------|------|
| **趋势类** | ADX, Aroon, Ichimoku Cloud | 判断趋势强度和方向 | 高 |
| **动量类** | CCI, Williams %R, ROC | 超买超卖判断 | 中 |
| **波动率** | ATR, Bollinger Band Width | 风险评估 | 高 |
| **成交量** | OBV, VWAP, MFI | 量价关系验证 | 中 |
| **资金流** | CMF, EMV, NVI | 主力资金动向 | 高 |

### 1.2 Alpha因子库

基于学术论文和开源量化库实现：

```python
# Alpha因子示例 (WorldQuant 101 Alpha因子)
class AlphaFactorEngine:
    def alpha_001(self, close, returns, volume):
        """Rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5))"""
        pass
    
    def alpha_002(self, close, open_, volume):
        """(-1 * correlation(open, volume, 10))"""
        pass
    
    def alpha_054(self, close, low, high):
        """((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)))"""
        pass
```

### 1.3 时间序列特征

```python
class TimeSeriesFeatures:
    def extract_features(self, df):
        features = {
            # 统计特征
            'rolling_mean_5': df['close'].rolling(5).mean(),
            'rolling_std_20': df['close'].rolling(20).std(),
            'rolling_skew_20': df['close'].rolling(20).skew(),
            'rolling_kurt_20': df['close'].rolling(20).kurt(),
            
            # 价格形态
            'price_momentum': df['close'].pct_change(5),
            'volatility_ratio': df['high'] / df['low'],
            'gap_ratio': (df['open'] - df['close'].shift(1)) / df['close'].shift(1),
            
            # 时间特征
            'day_of_week': df.index.dayofweek,
            'month': df.index.month,
            'quarter': df.index.quarter,
        }
        return features
```

---

## 🤖 Phase 2: 多模型集成预测系统

### 2.1 LSTM深度学习模型

参考项目: [Stock-Price-Prediction-LSTM](https://github.com/NourozR/Stock-Price-Prediction-LSTM), [StockPredictionRNN](https://github.com/dzitkowskik/StockPredictionRNN)

```python
class LSTMStockPredictor:
    """
    基于LSTM的股价预测模型
    架构: 多层LSTM + Attention机制 + Dropout正则化
    """
    def __init__(self, sequence_length=60, features=20):
        self.model = self._build_model()
    
    def _build_model(self):
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(60, 20)),
            Dropout(0.2),
            LSTM(64, return_sequences=True),
            Attention(),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='huber')
        return model
```

### 2.2 Transformer时序模型

参考项目: [iTransformer](https://github.com/thuml/iTransformer), [PatchTST](https://github.com/yuqinie98/PatchTST)

```python
class TimeSeriesTransformer:
    """
    基于Transformer的时间序列预测
    参考: iTransformer (ICLR 2024 Spotlight)
    """
    def __init__(self, d_model=512, nhead=8, num_layers=6):
        self.encoder = TransformerEncoder(
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            dim_feedforward=2048
        )
    
    def forward(self, x):
        # Patch embedding for time series
        x = self.patch_embedding(x)
        # Positional encoding
        x = self.pos_encoder(x)
        # Transformer encoding
        x = self.encoder(x)
        return self.projection(x)
```

### 2.3 集成学习模型

参考项目: [stock-trading-ml](https://github.com/yacoubb/stock-trading-ml)

```python
class EnsemblePredictor:
    """
    集成多模型预测
    - XGBoost: 梯度提升树
    - LightGBM: 轻量级梯度提升
    - CatBoost: 类别特征处理
    - Random Forest: 随机森林
    """
    def __init__(self):
        self.models = {
            'xgboost': XGBClassifier(n_estimators=200, max_depth=6),
            'lightgbm': LGBMClassifier(n_estimators=200, num_leaves=31),
            'catboost': CatBoostClassifier(iterations=200, depth=6),
            'rf': RandomForestClassifier(n_estimators=100, max_depth=10)
        }
        self.weights = {'xgboost': 0.3, 'lightgbm': 0.3, 'catboost': 0.25, 'rf': 0.15}
    
    def predict(self, X):
        predictions = {}
        for name, model in self.models.items():
            pred = model.predict_proba(X)
            predictions[name] = pred * self.weights[name]
        return sum(predictions.values())
```

### 2.4 模型权重动态调整

```python
class DynamicWeightOptimizer:
    """
    基于历史表现动态调整模型权重
    使用贝叶斯优化或强化学习
    """
    def update_weights(self, model_performances):
        # 计算各模型近期准确率
        # 使用指数移动平均平滑
        # 应用约束优化更新权重
        pass
```

---

## 📈 Phase 3: 交互式可视化系统

### 3.1 K线图与技术指标可视化

```python
class StockVisualizationEngine:
    """
    基于Plotly的交互式可视化
    """
    def create_candlestick_chart(self, df, indicators):
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5, 0.2, 0.15, 0.15]
        )
        
        # K线图
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['open'], high=df['high'],
            low=df['low'], close=df['close'], name='K线'
        ), row=1, col=1)
        
        # 均线
        for ma in ['MA5', 'MA10', 'MA20', 'MA60']:
            fig.add_trace(go.Scatter(x=df.index, y=df[ma], name=ma), row=1, col=1)
        
        # 成交量
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='成交量'), row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD'), row=3, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI'), row=4, col=1)
        
        return fig
```

### 3.2 预测趋势可视化

```python
class PredictionVisualizer:
    """
    预测结果可视化
    """
    def plot_prediction_with_confidence(self, historical, predicted, confidence_interval):
        fig = go.Figure()
        
        # 历史数据
        fig.add_trace(go.Scatter(
            x=historical.index, y=historical['close'],
            mode='lines', name='历史价格', line=dict(color='blue')
        ))
        
        # 预测数据
        fig.add_trace(go.Scatter(
            x=predicted.index, y=predicted['price'],
            mode='lines', name='预测价格', line=dict(color='red', dash='dash')
        ))
        
        # 置信区间
        fig.add_trace(go.Scatter(
            x=confidence_interval.index,
            y=confidence_interval['upper'],
            fill=None, mode='lines', line=dict(color='rgba(255,0,0,0.2)'),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=confidence_interval.index,
            y=confidence_interval['lower'],
            fill='tonexty', mode='lines',
            fillcolor='rgba(255,0,0,0.2)', name='95%置信区间'
        ))
        
        return fig
```

### 3.3 模型性能仪表板

```python
class ModelPerformanceDashboard:
    """
    模型性能监控仪表板
    """
    def generate_dashboard(self, metrics):
        dashboard = {
            'accuracy_trend': self._plot_accuracy_over_time(metrics),
            'model_comparison': self._plot_model_comparison(metrics),
            'feature_importance': self._plot_feature_importance(metrics),
            'confusion_matrix': self._plot_confusion_matrix(metrics),
            'backtest_results': self._plot_backtest_results(metrics)
        }
        return dashboard
```

---

## 🔄 Phase 4: 回测验证系统

参考项目: [backtrader](https://github.com/mementum/backtrader), [backtesting.py](https://github.com/kernc/backtesting.py)

### 4.1 策略回测框架

```python
class BacktestEngine:
    """
    基于backtesting.py的回测引擎
    """
    def run_backtest(self, strategy, data, cash=100000, commission=0.001):
        bt = Backtest(data, strategy, cash=cash, commission=commission)
        stats = bt.run()
        
        return {
            'total_return': stats['Return [%]'],
            'sharpe_ratio': stats['Sharpe Ratio'],
            'max_drawdown': stats['Max. Drawdown [%]'],
            'win_rate': stats['Win Rate [%]'],
            'trades': stats['# Trades']
        }
```

### 4.2 验证指标

| 指标 | 计算公式 | 目标值 |
|------|----------|--------|
| **准确率** | 正确预测数 / 总预测数 | >55% |
| **精确率** | TP / (TP + FP) | >60% |
| **召回率** | TP / (TP + FN) | >50% |
| **F1分数** | 2 * (P * R) / (P + R) | >0.55 |
| **夏普比率** | (R_p - R_f) / σ_p | >1.5 |
| **最大回撤** | (Peak - Trough) / Peak | <20% |

---

## 📁 文件结构规划

```
ai-service/
├── services/
│   ├── feature_engineering/
│   │   ├── __init__.py
│   │   ├── technical_indicators.py    # 技术指标计算
│   │   ├── alpha_factors.py           # Alpha因子
│   │   └── time_series_features.py    # 时序特征
│   ├── models/
│   │   ├── __init__.py
│   │   ├── lstm_predictor.py          # LSTM模型
│   │   ├── transformer_predictor.py   # Transformer模型
│   │   ├── ensemble_predictor.py      # 集成模型
│   │   └── model_trainer.py           # 模型训练
│   ├── backtest/
│   │   ├── __init__.py
│   │   ├── backtest_engine.py         # 回测引擎
│   │   └── strategy_base.py           # 策略基类
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── chart_builder.py           # 图表构建
│   │   └── dashboard.py               # 仪表板
│   ├── ai_analysis.py                 # 增强版AI分析
│   ├── technical_analysis.py          # 增强版技术分析
│   ├── news_service.py
│   └── stock_data.py
├── models/                            # 预训练模型存储
│   ├── lstm_stock.h5
│   ├── transformer_stock.pt
│   └── ensemble_model.pkl
├── config/
│   ├── model_config.yaml              # 模型配置
│   └── feature_config.yaml            # 特征配置
└── requirements.txt                   # 更新依赖
```

---

## 📦 依赖更新

```txt
# 现有依赖
akshare>=1.12.0
fastapi>=0.104.0
pandas>=2.0.0
numpy>=1.24.0
prophet>=1.1.5
transformers>=4.35.0
torch>=2.1.0

# 新增依赖
tensorflow>=2.15.0
xgboost>=2.0.0
lightgbm>=4.1.0
catboost>=1.2.0
scikit-learn>=1.3.0
ta-lib>=0.4.28
pandas-ta>=0.3.14b
plotly>=5.18.0
backtesting>=0.3.3
optuna>=3.4.0              # 超参数优化
shap>=0.43.0               # 特征重要性解释
joblib>=1.3.0              # 模型持久化
```

---

## 🗓️ 实施计划

### Phase 1: 特征工程 (预计3天)
- [ ] 实现扩展技术指标计算模块
- [ ] 开发Alpha因子库
- [ ] 构建时序特征提取器
- [ ] 编写特征工程文档

### Phase 2: 模型开发 (预计5天)
- [ ] 实现LSTM预测模型
- [ ] 实现Transformer预测模型
- [ ] 开发集成学习框架
- [ ] 模型训练与验证

### Phase 3: 可视化系统 (预计3天)
- [ ] 开发K线图可视化组件
- [ ] 实现预测趋势图表
- [ ] 构建性能仪表板
- [ ] 集成到邮件报告

### Phase 4: 回测验证 (预计2天)
- [ ] 搭建回测框架
- [ ] 运行历史数据回测
- [ ] 生成验证报告
- [ ] 性能优化

### Phase 5: 文档与测试 (预计2天)
- [ ] 编写算法文档
- [ ] 编写API文档
- [ ] 单元测试
- [ ] 集成测试

---

## 📚 参考文献

1. **iTransformer**: "Inverted Transformers Are Effective for Time Series Forecasting" (ICLR 2024)
2. **PatchTST**: "A Time Series is Worth 64 Words" (ICLR 2023)
3. **WorldQuant Alpha101**: "101 Formulaic Alphas" by Zura Kakushadze
4. **LSTM Stock Prediction**: Various implementations on GitHub
5. **Backtesting.py**: Python backtesting framework documentation

---

## ⚠️ 风险提示

1. **过拟合风险**: 使用交叉验证和正则化防止过拟合
2. **数据泄露**: 确保特征工程中不使用未来数据
3. **市场变化**: 模型需要定期重新训练以适应市场变化
4. **计算资源**: 深度学习模型需要GPU支持

---

## ✅ 验收标准

| 功能 | 验收标准 |
|------|----------|
| 特征工程 | 支持50+技术指标，20+Alpha因子 |
| LSTM模型 | 预测准确率 >52%，训练时间 <30分钟 |
| Transformer模型 | 预测准确率 >53%，支持多变量输入 |
| 集成模型 | 预测准确率 >55%，夏普比率 >1.5 |
| 可视化 | 支持交互式图表，自动生成报告 |
| 回测 | 支持策略回测，生成完整性能报告 |
