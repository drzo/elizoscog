"""
Enhanced Financial Reasoning Engine
Combines GnuCash data with OpenCog PLN reasoning for cognitive financial analysis
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from .gnucash_patterns import GnuCashDataAccess, FinancialAnalysisPatterns, Account, Transaction

logger = logging.getLogger(__name__)


class FinancialReasoningEngine:
    """PLN-based reasoning engine for financial data analysis"""
    
    def __init__(self, gnucash_file: str, atomspace_config: Dict[str, Any]):
        self.data_access = GnuCashDataAccess(gnucash_file)
        self.analysis = FinancialAnalysisPatterns(self.data_access)
        self.atomspace_config = atomspace_config
        self.financial_atoms = {}
        self.reasoning_rules = []
        
    async def initialize(self):
        """Initialize the reasoning engine"""
        await self.data_access.initialize()
        await self._load_financial_reasoning_rules()
        logger.info("Financial Reasoning Engine initialized")
        
    async def _load_financial_reasoning_rules(self):
        """Load PLN rules for financial reasoning"""
        self.reasoning_rules = [
            {
                'name': 'spending_pattern_detection',
                'pattern': 'IF account_spending > previous_month * 1.2 THEN spending_spike',
                'confidence': 0.85
            },
            {
                'name': 'budget_variance_analysis',
                'pattern': 'IF actual_spending > budget * 1.1 THEN over_budget',
                'confidence': 0.9
            },
            {
                'name': 'income_stability_assessment',
                'pattern': 'IF income_variance < 0.1 THEN stable_income',
                'confidence': 0.8
            },
            {
                'name': 'financial_trend_prediction',
                'pattern': 'IF trend_direction = increasing AND duration > 3_months THEN continuing_trend',
                'confidence': 0.75
            }
        ]
        
    async def analyze_spending_patterns(self, 
                                      start_date: date,
                                      end_date: date) -> Dict[str, Any]:
        """Analyze spending patterns using PLN reasoning"""
        
        # Get raw spending data
        spending_by_category = await self.analysis.get_spending_by_category(start_date, end_date)
        
        # Apply cognitive reasoning
        patterns = []
        insights = []
        
        for category, amount in spending_by_category.items():
            # Create financial atoms for this category
            category_atom = await self._create_category_atom(category, amount, start_date, end_date)
            
            # Apply reasoning rules
            for rule in self.reasoning_rules:
                if rule['name'] == 'spending_pattern_detection':
                    pattern_result = await self._apply_spending_pattern_rule(category, amount)
                    if pattern_result:
                        patterns.append(pattern_result)
                        
        return {
            'period': f"{start_date} to {end_date}",
            'spending_by_category': {k: float(v) for k, v in spending_by_category.items()},
            'detected_patterns': patterns,
            'cognitive_insights': insights,
            'reasoning_confidence': 0.8
        }
        
    async def _create_category_atom(self, category: str, amount: Decimal, 
                                  start_date: date, end_date: date) -> Dict[str, Any]:
        """Create AtomSpace representation of spending category"""
        atom = {
            'type': 'ConceptNode',
            'name': f"SpendingCategory-{category}",
            'properties': {
                'category': category,
                'amount': float(amount),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'created_at': datetime.now().isoformat()
            },
            'truth_value': {
                'strength': min(float(amount) / 1000.0, 1.0),  # Normalize based on amount
                'confidence': 0.9
            }
        }
        
        self.financial_atoms[f"{category}_{start_date}"] = atom
        return atom
        
    async def _apply_spending_pattern_rule(self, category: str, amount: Decimal) -> Optional[Dict[str, Any]]:
        """Apply spending pattern detection rule"""
        
        # Get historical data for comparison
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        previous_month_start = start_date - timedelta(days=30)
        
        try:
            # Get previous month spending for this category
            previous_spending = await self.analysis.get_spending_by_category(
                previous_month_start, start_date
            )
            
            previous_amount = previous_spending.get(category, Decimal('0'))
            
            if previous_amount > 0:
                ratio = amount / previous_amount
                
                if ratio > Decimal('1.2'):  # 20% increase
                    return {
                        'type': 'spending_spike',
                        'category': category,
                        'current_amount': float(amount),
                        'previous_amount': float(previous_amount),
                        'increase_ratio': float(ratio),
                        'confidence': 0.85,
                        'severity': 'high' if ratio > Decimal('1.5') else 'medium'
                    }
                elif ratio < Decimal('0.8'):  # 20% decrease
                    return {
                        'type': 'spending_reduction',
                        'category': category,
                        'current_amount': float(amount),
                        'previous_amount': float(previous_amount),
                        'reduction_ratio': float(ratio),
                        'confidence': 0.85,
                        'significance': 'high' if ratio < Decimal('0.5') else 'medium'
                    }
                    
        except Exception as e:
            logger.warning(f"Could not compare spending for {category}: {e}")
            
        return None
        
    async def predict_future_spending(self, category: str, months: int = 3) -> Dict[str, Any]:
        """Predict future spending using cognitive analysis"""
        
        # Get historical trends
        trends = await self.analysis.get_monthly_trends(category, 12)
        
        # Apply trend analysis reasoning
        prediction = {
            'category': category,
            'prediction_period_months': months,
            'predicted_amounts': [],
            'confidence': 0.7,
            'reasoning': 'Based on historical trend analysis'
        }
        
        # Simple trend-based prediction (could be enhanced with ML)
        if trends:
            # Calculate average monthly change
            recent_amounts = [t['amount'] for t in trends[-6:]]  # Last 6 months
            if len(recent_amounts) > 1:
                avg_change = sum(recent_amounts[i] - recent_amounts[i-1] 
                               for i in range(1, len(recent_amounts))) / (len(recent_amounts) - 1)
                
                last_amount = recent_amounts[-1]
                for month in range(1, months + 1):
                    predicted = last_amount + (avg_change * month)
                    prediction['predicted_amounts'].append({
                        'month': month,
                        'amount': float(max(predicted, 0))  # Don't predict negative spending
                    })
                    
        return prediction
        
    async def generate_financial_insights(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized financial insights using cognitive analysis"""
        insights = []
        
        # Analyze recent spending patterns
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        analysis = await self.analyze_spending_patterns(start_date, end_date)
        
        # Generate insights based on patterns
        for pattern in analysis['detected_patterns']:
            if pattern['type'] == 'spending_spike':
                insights.append({
                    'type': 'alert',
                    'title': f"Increased spending in {pattern['category']}",
                    'description': f"Your spending in {pattern['category']} increased by {pattern['increase_ratio']:.1%} this month",
                    'confidence': pattern['confidence'],
                    'actionable': True,
                    'suggestions': [
                        f"Review your {pattern['category']} expenses",
                        "Consider setting a budget limit",
                        "Look for cost-saving alternatives"
                    ]
                })
            elif pattern['type'] == 'spending_reduction':
                insights.append({
                    'type': 'positive',
                    'title': f"Great job reducing {pattern['category']} spending",
                    'description': f"You reduced spending in {pattern['category']} by {(1-pattern['reduction_ratio']):.1%}",
                    'confidence': pattern['confidence'],
                    'actionable': False
                })
                
        # Generate predictive insights
        top_categories = sorted(analysis['spending_by_category'].items(), 
                              key=lambda x: x[1], reverse=True)[:3]
        
        for category, amount in top_categories:
            prediction = await self.predict_future_spending(category, 3)
            if prediction['predicted_amounts']:
                next_month = prediction['predicted_amounts'][0]['amount']
                insights.append({
                    'type': 'prediction',
                    'title': f"Predicted {category} spending",
                    'description': f"Based on trends, expect to spend ${next_month:.2f} on {category} next month",
                    'confidence': prediction['confidence'],
                    'actionable': True,
                    'data': prediction
                })
                
        return insights
        
    async def answer_financial_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Answer natural language financial questions using cognitive reasoning"""
        
        question_lower = question.lower()
        
        # Pattern matching for common financial questions
        if 'spend' in question_lower and 'last month' in question_lower:
            return await self._handle_spending_question(question, context)
        elif 'budget' in question_lower:
            return await self._handle_budget_question(question, context)
        elif 'trend' in question_lower or 'pattern' in question_lower:
            return await self._handle_trend_question(question, context)
        elif 'predict' in question_lower or 'future' in question_lower:
            return await self._handle_prediction_question(question, context)
        else:
            return {
                'answer': "I can help you analyze spending patterns, budget tracking, and financial trends. Try asking about your spending last month or predicted expenses.",
                'confidence': 0.5,
                'type': 'general_help'
            }
            
    async def _handle_spending_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle questions about spending"""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        analysis = await self.analyze_spending_patterns(start_date, end_date)
        total_spending = sum(analysis['spending_by_category'].values())
        
        top_category = max(analysis['spending_by_category'].items(), key=lambda x: x[1])
        
        answer = f"Last month you spent ${total_spending:.2f} total. "
        answer += f"Your largest expense category was {top_category[0]} at ${top_category[1]:.2f}."
        
        if analysis['detected_patterns']:
            answer += f" I noticed {len(analysis['detected_patterns'])} spending pattern changes."
            
        return {
            'answer': answer,
            'confidence': 0.9,
            'type': 'spending_analysis',
            'data': analysis
        }
        
    async def _handle_budget_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle budget-related questions"""
        # This would integrate with budget data if available
        return {
            'answer': "Budget analysis requires budget targets to be configured. I can help you analyze spending patterns to establish budgets.",
            'confidence': 0.6,
            'type': 'budget_setup_needed'
        }
        
    async def _handle_trend_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trend analysis questions"""
        end_date = date.today()
        start_date = end_date - timedelta(days=90)  # 3 months
        
        analysis = await self.analyze_spending_patterns(start_date, end_date)
        
        answer = "Based on your spending trends over the last 3 months: "
        
        if analysis['detected_patterns']:
            patterns = analysis['detected_patterns']
            spikes = [p for p in patterns if p['type'] == 'spending_spike']
            reductions = [p for p in patterns if p['type'] == 'spending_reduction']
            
            if spikes:
                answer += f"Spending increased in {len(spikes)} categories. "
            if reductions:
                answer += f"Spending decreased in {len(reductions)} categories. "
        else:
            answer += "Your spending patterns have been relatively stable."
            
        return {
            'answer': answer,
            'confidence': 0.85,
            'type': 'trend_analysis',
            'data': analysis
        }
        
    async def _handle_prediction_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prediction questions"""
        # Extract category if mentioned
        category = None
        for word in question.lower().split():
            if word in ['groceries', 'food', 'gas', 'utilities', 'entertainment']:
                category = word.title()
                break
                
        if category:
            prediction = await self.predict_future_spending(category, 3)
            if prediction['predicted_amounts']:
                next_month = prediction['predicted_amounts'][0]['amount']
                answer = f"Based on your spending trends, I predict you'll spend approximately ${next_month:.2f} on {category} next month."
            else:
                answer = f"I don't have enough data to predict {category} spending."
        else:
            answer = "I can predict spending for specific categories. Try asking about groceries, utilities, or other expense categories."
            
        return {
            'answer': answer,
            'confidence': prediction.get('confidence', 0.6) if category else 0.5,
            'type': 'prediction',
            'data': prediction if category else None
        }
        
    async def close(self):
        """Close the reasoning engine"""
        await self.data_access.close()
        logger.info("Financial Reasoning Engine closed")