import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
import json

logger = logging.getLogger(__name__)

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logger.warning("Plotly not installed. Visualization will not be available.")


class StockVisualizationEngine:
    
    def __init__(self, theme: str = 'plotly_dark'):
        self.theme = theme
        self.default_colors = {
            'up': '#ef5350',
            'down': '#26a69a',
            'volume': '#5c6bc0',
            'ma5': '#ffd54f',
            'ma10': '#4fc3f7',
            'ma20': '#ba68c8',
            'ma60': '#ff8a65',
            'prediction': '#ff7043',
            'confidence': 'rgba(255, 112, 67, 0.3)'
        }
    
    def create_candlestick_chart(
        self,
        df: pd.DataFrame,
        title: str = "Stock Price Chart",
        show_volume: bool = True,
        show_ma: bool = True,
        show_macd: bool = True,
        show_rsi: bool = True,
        height: int = 800
    ) -> Dict:
        
        if not HAS_PLOTLY:
            return {'error': 'Plotly not installed'}
        
        n_rows = 1
        row_heights = [0.5]
        
        if show_volume:
            n_rows += 1
            row_heights.append(0.15)
        if show_macd:
            n_rows += 1
            row_heights.append(0.15)
        if show_rsi:
            n_rows += 1
            row_heights.append(0.2)
        
        fig = make_subplots(
            rows=n_rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights
        )
        
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='K线',
                increasing_line_color=self.default_colors['up'],
                decreasing_line_color=self.default_colors['down']
            ),
            row=1, col=1
        )
        
        if show_ma:
            ma_configs = [
                ('MA5', self.default_colors['ma5']),
                ('MA10', self.default_colors['ma10']),
                ('MA20', self.default_colors['ma20']),
                ('MA60', self.default_colors['ma60'])
            ]
            
            for ma_name, color in ma_configs:
                if ma_name in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[ma_name],
                            name=ma_name,
                            line=dict(color=color, width=1)
                        ),
                        row=1, col=1
                    )
        
        current_row = 2
        
        if show_volume:
            colors = np.where(
                df['close'] >= df['open'],
                self.default_colors['up'],
                self.default_colors['down']
            )
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['volume'],
                    name='成交量',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=current_row, col=1
            )
            current_row += 1
        
        if show_macd and 'MACD' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD'],
                    name='MACD',
                    line=dict(color='#2196f3', width=1)
                ),
                row=current_row, col=1
            )
            
            if 'MACD_SIGNAL' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['MACD_SIGNAL'],
                        name='Signal',
                        line=dict(color='#ff9800', width=1)
                    ),
                    row=current_row, col=1
                )
            
            if 'MACD_HISTOGRAM' in df.columns:
                colors = np.where(
                    df['MACD_HISTOGRAM'] >= 0,
                    self.default_colors['up'],
                    self.default_colors['down']
                )
                fig.add_trace(
                    go.Bar(
                        x=df.index,
                        y=df['MACD_HISTOGRAM'],
                        name='Histogram',
                        marker_color=colors,
                        opacity=0.5
                    ),
                    row=current_row, col=1
                )
            current_row += 1
        
        if show_rsi and 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    name='RSI',
                    line=dict(color='#9c27b0', width=1)
                ),
                row=current_row, col=1
            )
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="超买", row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green",
                         annotation_text="超卖", row=current_row, col=1)
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=height,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(title_text="日期", row=n_rows, col=1)
        fig.update_yaxes(title_text="价格", row=1, col=1)
        
        return fig.to_dict()
    
    def create_prediction_chart(
        self,
        historical: pd.DataFrame,
        predictions: List[float],
        confidence_interval: Dict = None,
        title: str = "Price Prediction"
    ) -> Dict:
        
        if not HAS_PLOTLY:
            return {'error': 'Plotly not installed'}
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=historical.index,
                y=historical['close'],
                mode='lines',
                name='历史价格',
                line=dict(color='#2196f3', width=2)
            )
        )
        
        last_date = historical.index[-1]
        prediction_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=len(predictions),
            freq='D'
        )
        
        fig.add_trace(
            go.Scatter(
                x=prediction_dates,
                y=predictions,
                mode='lines+markers',
                name='预测价格',
                line=dict(color=self.default_colors['prediction'], width=2, dash='dash'),
                marker=dict(size=8)
            )
        )
        
        if confidence_interval:
            upper = confidence_interval.get('upper', [])
            lower = confidence_interval.get('lower', [])
            
            if len(upper) == len(predictions) and len(lower) == len(predictions):
                fig.add_trace(
                    go.Scatter(
                        x=prediction_dates,
                        y=upper,
                        mode='lines',
                        line=dict(color='rgba(255, 112, 67, 0.2)'),
                        showlegend=False
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=prediction_dates,
                        y=lower,
                        mode='lines',
                        fill='tonexty',
                        fillcolor=self.default_colors['confidence'],
                        line=dict(color='rgba(255, 112, 67, 0.2)'),
                        name='95%置信区间'
                    )
                )
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=500,
            xaxis_title="日期",
            yaxis_title="价格",
            showlegend=True
        )
        
        return fig.to_dict()
    
    def create_technical_indicator_chart(
        self,
        df: pd.DataFrame,
        indicators: List[str] = None,
        title: str = "Technical Indicators"
    ) -> Dict:
        
        if not HAS_PLOTLY:
            return {'error': 'Plotly not installed'}
        
        if indicators is None:
            indicators = ['RSI', 'MACD', 'K', 'D']
        
        available_indicators = [ind for ind in indicators if ind in df.columns]
        
        if not available_indicators:
            return {'error': 'No valid indicators found'}
        
        fig = make_subplots(
            rows=len(available_indicators),
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=available_indicators
        )
        
        colors = ['#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3']
        
        for i, indicator in enumerate(available_indicators):
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[indicator],
                    name=indicator,
                    line=dict(color=colors[i % len(colors)], width=1.5)
                ),
                row=i+1, col=1
            )
            
            if indicator == 'RSI':
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=i+1, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=i+1, col=1)
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=300 * len(available_indicators),
            showlegend=True
        )
        
        return fig.to_dict()
    
    def create_volume_analysis_chart(
        self,
        df: pd.DataFrame,
        title: str = "Volume Analysis"
    ) -> Dict:
        
        if not HAS_PLOTLY:
            return {'error': 'Plotly not installed'}
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.6, 0.4]
        )
        
        colors = np.where(
            df['close'] >= df['open'],
            self.default_colors['up'],
            self.default_colors['down']
        )
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='成交量',
                marker_color=colors,
                opacity=0.7
            ),
            row=1, col=1
        )
        
        if 'VOLUME_MA_5' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['VOLUME_MA_5'],
                    name='5日均线',
                    line=dict(color='#ffd54f', width=1.5)
                ),
                row=1, col=1
            )
        
        if 'VOLUME_MA_20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['VOLUME_MA_20'],
                    name='20日均线',
                    line=dict(color='#4fc3f7', width=1.5)
                ),
                row=1, col=1
            )
        
        if 'OBV' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['OBV'],
                    name='OBV',
                    line=dict(color='#ba68c8', width=1.5)
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=500,
            showlegend=True
        )
        
        return fig.to_dict()
    
    def create_feature_importance_chart(
        self,
        feature_importance: Dict[str, float],
        title: str = "Feature Importance",
        top_n: int = 20
    ) -> Dict:
        
        if not HAS_PLOTLY:
            return {'error': 'Plotly not installed'}
        
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        features = [f[0] for f in sorted_features]
        importance = [f[1] for f in sorted_features]
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=importance,
                y=features,
                orientation='h',
                marker_color='#3f51b5',
                opacity=0.8
            )
        )
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=500,
            xaxis_title="重要性",
            yaxis_title="特征",
            yaxis=dict(autorange="reversed")
        )
        
        return fig.to_dict()
    
    def create_model_comparison_chart(
        self,
        model_metrics: Dict[str, Dict[str, float]],
        metric_name: str = 'accuracy',
        title: str = "Model Comparison"
    ) -> Dict:
        
        if not HAS_PLOTLY:
            return {'error': 'Plotly not installed'}
        
        models = list(model_metrics.keys())
        values = [model_metrics[m].get(metric_name, 0) for m in models]
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=models,
                y=values,
                marker_color=['#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3'][:len(models)],
                text=[f'{v:.3f}' for v in values],
                textposition='auto'
            )
        )
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=400,
            xaxis_title="模型",
            yaxis_title=metric_name
        )
        
        return fig.to_dict()
    
    def create_dashboard_html(
        self,
        charts: Dict[str, Dict],
        title: str = "Stock Analysis Dashboard"
    ) -> str:
        
        if not HAS_PLOTLY:
            return '<html><body><h1>Plotly not installed</h1></body></html>'
        
        chart_htmls = []
        for name, chart_data in charts.items():
            if 'error' not in chart_data:
                fig = go.Figure(chart_data)
                chart_htmls.append(f'''
                    <div class="chart-container">
                        <h2>{name}</h2>
                        {fig.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                ''')
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #1e1e1e;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }}
                h1 {{
                    text-align: center;
                    color: #64b5f6;
                }}
                .dashboard {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                .chart-container {{
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                }}
                .chart-container h2 {{
                    margin-top: 0;
                    color: #90caf9;
                    border-bottom: 2px solid #3f51b5;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h1>{title}</h1>
                {''.join(chart_htmls)}
            </div>
        </body>
        </html>
        '''
        
        return html
