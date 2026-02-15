import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import dashscope
from dashscope import Generation

logger = logging.getLogger(__name__)


class TongyiAnalysisService:
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if self.api_key:
            dashscope.api_key = self.api_key
        self.model = 'qwen-turbo'
    
    def analyze_stock(
        self,
        code: str,
        name: str,
        current_price: float,
        tech_indicators: Dict,
        news_sentiment: Dict,
        historical_summary: str = None
    ) -> Dict:
        
        prompt = self._build_analysis_prompt(
            code, name, current_price, tech_indicators, news_sentiment, historical_summary
        )
        
        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=3000,
                temperature=0.7,
                top_p=0.8
            )
            
            if response.status_code == 200:
                result_text = response.output.text
                return self._parse_analysis_result(result_text, code, name, current_price)
            else:
                logger.error(f"Tongyi API error: {response.code} - {response.message}")
                return self._get_default_result(code, name, current_price)
                
        except Exception as e:
            logger.error(f"Failed to call Tongyi API: {e}")
            return self._get_default_result(code, name, current_price)
    
    def _build_analysis_prompt(
        self,
        code: str,
        name: str,
        current_price: float,
        tech_indicators: Dict,
        news_sentiment: Dict,
        historical_summary: str
    ) -> str:
        
        indicators_text = self._format_indicators(tech_indicators)
        sentiment_text = self._format_sentiment(news_sentiment)
        
        prompt = f"""你是一位专业的股票分析师，专门为投资新手提供简单易懂的分析建议。请根据以下数据分析股票{code}({name})。

## 基本信息
- 股票代码: {code}
- 股票名称: {name}
- 当前价格: {current_price}元

## 技术指标
{indicators_text}

## 新闻情绪
{sentiment_text}

## 历史走势摘要
{historical_summary or '暂无'}

请以JSON格式输出分析结果，必须包含以下字段：
{{
    "recommendation": "BUY/SELL/HOLD",
    "confidence": 0.0-1.0之间的数值,
    "risk_level": "低/中等/较高/高",
    "trend_direction": "上涨/下跌/横盘震荡",
    "reasons": ["用简单语言说明的理由1", "理由2", "理由3"],
    "technical_analysis": "用大白话解释技术面情况，不要用专业术语",
    "suggestion": "具体操作建议",
    "stop_loss": 建议止损价位（数字）,
    "target_price": 目标价位（数字）,
    "support_resistance": {{
        "support_levels": [
            {{"price": 支撑位价格1, "strength": "强/中/弱", "reason": "为什么是支撑位（大白话）"}},
            {{"price": 支撑位价格2, "strength": "强/中/弱", "reason": "原因"}}
        ],
        "resistance_levels": [
            {{"price": 阻力位价格1, "strength": "强/中/弱", "reason": "为什么是阻力位（大白话）"}},
            {{"price": 阻力位价格2, "strength": "强/中/弱", "reason": "原因"}}
        ],
        "current_position": "当前价格在支撑位和阻力位之间的位置描述",
        "breakthrough_hint": "突破阻力位或跌破支撑位的操作提示"
    }},
    "stop_profit_strategy": {{
        "tiered_profit_taking": [
            {{"trigger": "涨幅达到10%", "action": "卖出1/3仓位", "reason": "原因（大白话）"}},
            {{"trigger": "涨幅达到20%", "action": "再卖出1/3仓位", "reason": "原因"}},
            {{"trigger": "涨幅达到30%", "action": "卖出剩余仓位或继续持有", "reason": "原因"}}
        ],
        "trailing_stop": {{
            "enabled": true/false,
            "trigger": "如：盈利超过15%后启动",
            "stop_ratio": "如：回撤8%止盈",
            "explanation": "移动止损的简单解释"
        }},
        "time_based_exit": {{
            "holding_period": "建议最长持仓时间",
            "reason": "原因（大白话）"
        }}
    }},
    "stop_loss_strategy": {{
        "initial_stop_loss": {{
            "price": 止损价位,
            "ratio": "如：亏损8%",
            "reason": "为什么设在这个位置"
        }},
        "moving_stop_loss": {{
            "condition": "什么情况下调整止损位",
            "method": "如何调整（大白话）"
        }},
        "forced_exit_conditions": ["强制清仓条件1", "条件2"]
    }},
    "risk_factors": [
        {{"factor": "风险因素名称", "level": "高/中/低", "description": "具体说明（大白话）", "mitigation": "应对方法"}},
        {{"factor": "市场风险", "level": "中", "description": "大盘走势对个股的影响", "mitigation": "关注大盘，顺势操作"}},
        {{"factor": "行业风险", "level": "中", "description": "行业整体情况", "mitigation": "分散投资"}}
    ],
    "market_environment": {{
        "overall_assessment": "当前市场环境评估（牛市/熊市/震荡市）",
        "impact_on_stock": "对这只股票的影响",
        "suggested_position": "建议仓位（轻仓/半仓/重仓）"
    }},
    "operation_difficulty": {{
        "level": "简单/中等/复杂",
        "reason": "为什么是这个难度等级",
        "suitable_for": "适合什么类型的投资者（保守型/稳健型/激进型）",
        "required_skills": ["需要掌握的技能1", "技能2"]
    }},
    "batch_operation_plan": {{
        "buy_plan": [
            {{"condition": "买入条件1", "position": "建议买入仓位比例", "price_hint": "参考价格"}},
            {{"condition": "买入条件2", "position": "建议加仓比例", "price_hint": "参考价格"}}
        ],
        "sell_plan": [
            {{"condition": "卖出条件1", "position": "建议卖出比例", "price_hint": "参考价格"}},
            {{"condition": "卖出条件2", "position": "建议卖出比例", "price_hint": "参考价格"}}
        ],
        "total_position_limit": "总仓位上限",
        "execution_timeline": "执行时间建议"
    }},
    "investment_advice": {{
        "position_ratio": "建议投入总资金的百分比，如'5%-10%'",
        "max_investment": "假设用户有10万元，建议最多投入多少元买这只股票",
        "why_this_ratio": "用简单语言解释为什么建议这个比例",
        "risk_warning": "用大白话提醒风险",
        "beginner_tips": ["给新手的3条具体操作建议1", "建议2", "建议3"]
    }},
    "simple_explanation": {{
        "what_to_do": "用一句话告诉新手该怎么做",
        "key_point": "最重要的一个关注点",
        "when_to_buy": "什么情况下可以买入",
        "when_to_sell": "什么情况下应该卖出"
    }},
    "data_quality": {{
        "completeness_score": 0.0-1.0之间的数值,
        "data_used": ["使用的数据源1", "数据源2"],
        "missing_data": ["缺失的数据1", "缺失的数据2"],
        "reliability_note": "分析可靠性的简单说明"
    }}
}}

重要提示：
1. 所有解释必须用大白话，避免专业术语
2. 给出具体的数字建议，不要模棱两可
3. 新手建议单只股票投入不超过总资金的10%
4. 必须包含止损建议，新手建议亏损8-10%止损
5. 支撑位和阻力位要结合技术指标给出合理价位
6. 分档止盈策略要具体可执行
7. 风险因素至少列出3个

请只输出JSON，不要有其他内容。"""
        
        return prompt
    
    def _format_indicators(self, tech_indicators: Dict) -> str:
        if not tech_indicators:
            return "暂无技术指标数据"
        
        lines = []
        
        trend = tech_indicators.get('trend_indicators', {})
        if trend:
            lines.append("**趋势指标**:")
            for key, value in trend.items():
                if value is not None:
                    lines.append(f"  - {key}: {value:.2f}")
        
        momentum = tech_indicators.get('momentum_indicators', {})
        if momentum:
            lines.append("**动量指标**:")
            for key, value in momentum.items():
                if value is not None:
                    lines.append(f"  - {key}: {value:.2f}")
        
        signals = tech_indicators.get('signals', {})
        if signals:
            lines.append("**信号汇总**:")
            buy_signals = sum(1 for v in signals.values() if v > 0)
            sell_signals = sum(1 for v in signals.values() if v < 0)
            lines.append(f"  - 买入信号: {buy_signals}个")
            lines.append(f"  - 卖出信号: {sell_signals}个")
        
        return '\n'.join(lines)
    
    def _format_sentiment(self, news_sentiment: Dict) -> str:
        if not news_sentiment:
            return "暂无新闻情绪数据"
        
        sentiment = news_sentiment.get('sentiment', '中性')
        score = news_sentiment.get('score', 0.5)
        news_count = news_sentiment.get('news_count', 0)
        
        return f"""- 整体情绪: {sentiment}
- 情绪得分: {score:.2f}
- 分析新闻数: {news_count}条"""
    
    def _parse_analysis_result(self, result_text: str, code: str, name: str, current_price: float) -> Dict:
        try:
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                result = json.loads(json_str)
                
                return {
                    'code': code,
                    'name': name,
                    'currentPrice': current_price,
                    'recommendation': result.get('recommendation', 'HOLD'),
                    'confidence': float(result.get('confidence', 0.5)),
                    'riskLevel': result.get('risk_level', '中等'),
                    'trendDirection': result.get('trend_direction', '横盘震荡'),
                    'reasons': result.get('reasons', ['综合分析建议观望']),
                    'technicalAnalysis': result.get('technical_analysis', ''),
                    'suggestion': result.get('suggestion', ''),
                    'stopLoss': result.get('stop_loss'),
                    'targetPrice': result.get('target_price'),
                    'supportResistance': result.get('support_resistance', self._get_default_support_resistance(current_price)),
                    'stopProfitStrategy': result.get('stop_profit_strategy', self._get_default_stop_profit_strategy()),
                    'stopLossStrategy': result.get('stop_loss_strategy', self._get_default_stop_loss_strategy(current_price)),
                    'riskFactors': result.get('risk_factors', self._get_default_risk_factors()),
                    'marketEnvironment': result.get('market_environment', self._get_default_market_environment()),
                    'operationDifficulty': result.get('operation_difficulty', self._get_default_operation_difficulty()),
                    'batchOperationPlan': result.get('batch_operation_plan', self._get_default_batch_operation_plan()),
                    'investmentAdvice': result.get('investment_advice', self._get_default_investment_advice(current_price)),
                    'simpleExplanation': result.get('simple_explanation', self._get_default_simple_explanation()),
                    'dataQuality': result.get('data_quality', self._get_default_data_quality()),
                    'analysisTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'validUntil': self._get_valid_until(),
                    'source': 'tongyi_qwen'
                }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from Tongyi response: {e}")
        
        return self._get_default_result(code, name, current_price)
    
    def _get_default_investment_advice(self, current_price: float) -> Dict:
        return {
            'position_ratio': '5%-10%',
            'max_investment': '建议投入5000-10000元（假设总资金10万元）',
            'why_this_ratio': '新手应该控制风险，单只股票不超过总资金的10%',
            'risk_warning': '股市有风险，投资需谨慎。建议设置止损，亏损8-10%及时止损。',
            'beginner_tips': [
                '分批买入，不要一次性投入全部资金',
                '设置止损点，亏损8-10%果断卖出',
                '长期持有优质股票，不要频繁交易'
            ]
        }
    
    def _get_default_simple_explanation(self) -> Dict:
        return {
            'what_to_do': '建议观望，等待更好的买入时机',
            'key_point': '关注股价是否突破关键阻力位',
            'when_to_buy': '股价突破近期高点，成交量放大时可考虑买入',
            'when_to_sell': '亏损达到8-10%或达到目标价位时卖出'
        }
    
    def _get_default_support_resistance(self, current_price: float) -> Dict:
        if not current_price:
            return {
                'support_levels': [],
                'resistance_levels': [],
                'current_position': '数据不足',
                'breakthrough_hint': '请获取更多数据'
            }
        return {
            'support_levels': [
                {'price': round(current_price * 0.95, 2), 'strength': '中', 'reason': '近期回调支撑位'},
                {'price': round(current_price * 0.90, 2), 'strength': '强', 'reason': '重要心理支撑位'}
            ],
            'resistance_levels': [
                {'price': round(current_price * 1.05, 2), 'strength': '中', 'reason': '近期反弹阻力位'},
                {'price': round(current_price * 1.10, 2), 'strength': '强', 'reason': '重要心理阻力位'}
            ],
            'current_position': f'当前价格{current_price}元，处于支撑位和阻力位之间',
            'breakthrough_hint': '突破阻力位可考虑加仓，跌破支撑位应及时止损'
        }
    
    def _get_default_stop_profit_strategy(self) -> Dict:
        return {
            'tiered_profit_taking': [
                {'trigger': '涨幅达到10%', 'action': '卖出1/3仓位', 'reason': '锁定部分利润，降低风险'},
                {'trigger': '涨幅达到20%', 'action': '再卖出1/3仓位', 'reason': '继续锁定利润，保留上涨空间'},
                {'trigger': '涨幅达到30%', 'action': '卖出剩余仓位或继续持有', 'reason': '根据市场情况决定'}
            ],
            'trailing_stop': {
                'enabled': True,
                'trigger': '盈利超过15%后启动',
                'stop_ratio': '从最高点回撤8%止盈',
                'explanation': '股价上涨后，把止损位往上移，保护已有利润'
            },
            'time_based_exit': {
                'holding_period': '建议不超过3个月',
                'reason': '短线操作不宜过长，避免利润回吐'
            }
        }
    
    def _get_default_stop_loss_strategy(self, current_price: float) -> Dict:
        stop_loss_price = round(current_price * 0.92, 2) if current_price else None
        return {
            'initial_stop_loss': {
                'price': stop_loss_price,
                'ratio': '亏损8%',
                'reason': '新手建议设置8%止损，控制单笔亏损'
            },
            'moving_stop_loss': {
                'condition': '盈利超过10%后',
                'method': '将止损位上移到成本价，确保不亏损'
            },
            'forced_exit_conditions': [
                '亏损达到止损线立即卖出，不要犹豫',
                '公司出现重大利空消息',
                '大盘系统性风险，指数大跌超过3%'
            ]
        }
    
    def _get_default_risk_factors(self) -> List[Dict]:
        return [
            {
                'factor': '市场风险',
                'level': '中',
                'description': '大盘走势会影响个股表现',
                'mitigation': '关注大盘走势，顺势操作'
            },
            {
                'factor': '行业风险',
                'level': '中',
                'description': '行业政策变化可能影响股价',
                'mitigation': '分散投资，不要把鸡蛋放在一个篮子里'
            },
            {
                'factor': '个股风险',
                'level': '中',
                'description': '公司业绩、管理层变动等因素',
                'mitigation': '定期关注公司公告和财报'
            },
            {
                'factor': '流动性风险',
                'level': '低',
                'description': '成交量过小可能导致买卖困难',
                'mitigation': '选择成交量活跃的股票'
            }
        ]
    
    def _get_default_market_environment(self) -> Dict:
        return {
            'overall_assessment': '震荡市',
            'impact_on_stock': '市场整体震荡，个股表现分化',
            'suggested_position': '轻仓操作，建议不超过总资金的30%'
        }
    
    def _get_default_operation_difficulty(self) -> Dict:
        return {
            'level': '中等',
            'reason': '需要一定的技术分析能力和风险控制意识',
            'suitable_for': '稳健型投资者',
            'required_skills': [
                '看懂K线图基本形态',
                '了解支撑位和阻力位概念',
                '能够严格执行止损纪律'
            ]
        }
    
    def _get_default_batch_operation_plan(self) -> Dict:
        return {
            'buy_plan': [
                {'condition': '股价回调到支撑位附近', 'position': '先买入30%仓位', 'price_hint': '支撑位附近'},
                {'condition': '股价突破阻力位确认', 'position': '加仓30%', 'price_hint': '突破阻力位'}
            ],
            'sell_plan': [
                {'condition': '涨幅达到10%', 'position': '卖出30%', 'price_hint': '目标价附近'},
                {'condition': '触发止损线', 'position': '全部卖出', 'price_hint': '止损价位'}
            ],
            'total_position_limit': '不超过总资金的10%',
            'execution_timeline': '根据市场情况灵活调整，建议在交易日开盘后1小时或收盘前1小时操作'
        }
    
    def _get_default_data_quality(self) -> Dict:
        return {
            'completeness_score': 0.6,
            'data_used': ['技术指标', '历史价格'],
            'missing_data': ['实时新闻', '公司财报'],
            'reliability_note': '分析结果仅供参考，建议结合更多信息综合判断'
        }
    
    def _get_valid_until(self) -> str:
        from datetime import timedelta
        valid_time = datetime.now() + timedelta(hours=24)
        return valid_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_default_result(self, code: str, name: str, current_price: float) -> Dict:
        return {
            'code': code,
            'name': name,
            'currentPrice': current_price,
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'riskLevel': '中等',
            'trendDirection': '横盘震荡',
            'reasons': ['数据不足，建议观望'],
            'technicalAnalysis': '',
            'suggestion': '请获取更多数据后再做决策',
            'stopLoss': current_price * 0.92 if current_price else None,
            'targetPrice': current_price * 1.1 if current_price else None,
            'supportResistance': self._get_default_support_resistance(current_price),
            'stopProfitStrategy': self._get_default_stop_profit_strategy(),
            'stopLossStrategy': self._get_default_stop_loss_strategy(current_price),
            'riskFactors': self._get_default_risk_factors(),
            'marketEnvironment': self._get_default_market_environment(),
            'operationDifficulty': self._get_default_operation_difficulty(),
            'batchOperationPlan': self._get_default_batch_operation_plan(),
            'investmentAdvice': self._get_default_investment_advice(current_price),
            'simpleExplanation': self._get_default_simple_explanation(),
            'dataQuality': self._get_default_data_quality(),
            'analysisTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'validUntil': self._get_valid_until(),
            'source': 'default'
        }
    
    def generate_market_summary(self, market_data: Dict) -> str:
        prompt = f"""请根据以下A股市场数据，生成一段简短的市场概况分析（100字以内），用大白话解释：

市场数据：
{json.dumps(market_data, ensure_ascii=False, indent=2)}

请直接输出分析文本，用简单易懂的语言，不要有其他内容。"""
        
        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate market summary: {e}")
        
        return "今日A股市场整体表现平稳，建议关注市场热点板块。"
    
    def analyze_news_impact(self, news_title: str, news_content: str = None) -> Dict:
        prompt = f"""请分析以下财经新闻对股市的影响，用简单语言解释：

新闻标题：{news_title}
{f'新闻内容：{news_content}' if news_content else ''}

请以JSON格式输出：
{{
    "sentiment": "正面/负面/中性",
    "impact_level": "高/中/低",
    "affected_sectors": ["受影响板块1", "受影响板块2"],
    "summary": "一句话总结影响（用大白话）",
    "beginner_advice": "给新手的简单建议"
}}"""
        
        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=300,
                temperature=0.5
            )
            
            if response.status_code == 200:
                result_text = response.output.text
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    return json.loads(result_text[json_start:json_end])
        except Exception as e:
            logger.error(f"Failed to analyze news impact: {e}")
        
        return {
            'sentiment': '中性',
            'impact_level': '中',
            'affected_sectors': [],
            'summary': '无法分析',
            'beginner_advice': '建议观望，等待更多信息'
        }
    
    def chat(self, question: str, context: str = None) -> str:
        prompt = question
        if context:
            prompt = f"背景信息：\n{context}\n\n问题：{question}"
        
        prompt += "\n\n请用简单易懂的语言回答，避免专业术语，给新手也能听懂的建议。"
        
        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
        except Exception as e:
            logger.error(f"Chat failed: {e}")
        
        return "抱歉，我暂时无法回答这个问题。"
