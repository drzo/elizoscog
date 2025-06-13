"""
ElizaOS-GnuCash Bridge Implementation
Provides direct integration between ElizaOS agents and GnuCash financial operations
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal


class FinancialAgent:
    """Base class for ElizaOS financial agents"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.config = agent_config
        self.gnucash_file = agent_config.get('gnucash_file')
        self.connection = None
        
    async def initialize(self):
        """Initialize connection to GnuCash"""
        if self.gnucash_file:
            self.connection = sqlite3.connect(self.gnucash_file)
            
    async def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Process a financial transaction"""
        # Base implementation - override in subclasses
        return {"status": "processed", "transaction_id": transaction.get("id")}
        
    async def analyze_spending(self, timeframe: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spending patterns in given timeframe"""
        # Base implementation - override in subclasses
        return {"analysis": "completed", "timeframe": timeframe}
        
    async def generate_report(self, report_type: str) -> Dict[str, Any]:
        """Generate financial report"""
        # Base implementation - override in subclasses
        return {"report_type": report_type, "status": "generated"}


class TransactionCategorizerAgent(FinancialAgent):
    """ElizaOS agent for automatic transaction categorization"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.categorization_rules = agent_config.get('rules', [])
        
    async def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically categorize transaction"""
        description = transaction.get('description', '').lower()
        amount = transaction.get('amount', 0)
        
        category = await self._determine_category(description, amount)
        
        # Update transaction in GnuCash
        if self.connection and category:
            await self._update_transaction_category(transaction['id'], category)
            
        return {
            "status": "categorized",
            "transaction_id": transaction['id'],
            "category": category,
            "confidence": await self._get_confidence(description, category)
        }
        
    async def _determine_category(self, description: str, amount: float) -> Optional[str]:
        """Determine transaction category based on description and amount"""
        description_lower = description.lower()
        
        # Specific store/merchant patterns (more specific matches first)
        specific_patterns = {
            'groceries': ['safeway', 'kroger', 'walmart', 'target', 'costco', 'trader joe', 'whole foods', 'aldi', 'publix', 'grocery', 'supermarket', 'food market'],
            'gas': ['shell', 'exxon', 'bp', 'chevron', 'texaco', 'arco', 'gas station', 'fuel'],
            'restaurants': ['mcdonalds', 'burger king', 'subway', 'starbucks', 'pizza', 'restaurant', 'cafe', 'diner', 'bistro'],
            'utilities': ['electric', 'water company', 'gas company', 'utility', 'power', 'edison'],
            'transportation': ['uber', 'lyft', 'taxi', 'bus', 'metro', 'transit', 'parking'],
            'entertainment': ['movie', 'theater', 'cinema', 'concert', 'netflix', 'spotify', 'game'],
            'healthcare': ['doctor', 'pharmacy', 'medical', 'hospital', 'cvs pharmacy', 'walgreens'],
            'shopping': ['amazon', 'mall', 'shop', 'retail', 'department store']  # More generic patterns last
        }
        
        # Check specific patterns first
        for category, patterns in specific_patterns.items():
            if any(pattern in description_lower for pattern in patterns):
                return category
                
        # Default category for unmatched transactions
        return 'uncategorized'
        
    async def _get_confidence(self, description: str, category: str) -> float:
        """Calculate confidence score for categorization"""
        # Simple confidence calculation
        if category == 'uncategorized':
            return 0.3
        return 0.8  # High confidence for pattern matches
        
    async def _update_transaction_category(self, transaction_id: str, category: str):
        """Update transaction category in GnuCash database"""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                # Update transaction with category info (stored as memo or description)
                cursor.execute("""
                    UPDATE transactions 
                    SET description = description || ' [' || ? || ']'
                    WHERE guid = ?
                """, (category, transaction_id))
                self.connection.commit()
                print(f"Updated transaction {transaction_id} with category: {category}")
            except Exception as e:
                print(f"Error updating transaction category: {e}")
        else:
            print(f"Mock update: Transaction {transaction_id} categorized as {category}")


class ExpenseAnalyzerAgent(FinancialAgent):
    """ElizaOS agent for expense analysis and insights"""
    
    async def analyze_spending(self, timeframe: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spending patterns and provide insights"""
        start_date = timeframe.get('start_date')
        end_date = timeframe.get('end_date')
        
        if not self.connection:
            return {"error": "No GnuCash connection available"}
            
        # Query spending data
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT account_name, SUM(amount) as total, COUNT(*) as count
            FROM transactions t
            JOIN splits s ON t.guid = s.tx_guid  
            WHERE t.post_date BETWEEN ? AND ?
            AND amount < 0  -- Expenses are negative
            GROUP BY account_name
            ORDER BY total ASC
        """, (start_date, end_date))
        
        spending_data = []
        total_expenses = 0
        
        for row in cursor.fetchall():
            account, amount, count = row
            amount = abs(amount)  # Convert to positive for display
            total_expenses += amount
            
            spending_data.append({
                'account': account,
                'amount': amount,
                'transaction_count': count,
                'average_transaction': amount / count if count > 0 else 0
            })
            
        # Generate insights
        insights = await self._generate_insights(spending_data, total_expenses)
        
        return {
            "timeframe": timeframe,
            "total_expenses": total_expenses,
            "spending_breakdown": spending_data,
            "insights": insights,
            "analysis_date": datetime.now().isoformat()
        }
        
    async def _generate_insights(self, spending_data: List[Dict[str, Any]], total: float) -> List[str]:
        """Generate spending insights"""
        insights = []
        
        if spending_data:
            # Top expense category
            top_expense = spending_data[0]
            insights.append(f"Your highest expense category is {top_expense['account']} "
                          f"with ${top_expense['amount']:.2f}")
            
            # Percentage of top category
            percentage = (top_expense['amount'] / total) * 100 if total > 0 else 0
            insights.append(f"This represents {percentage:.1f}% of your total expenses")
            
            # Frequent small transactions
            frequent_small = [s for s in spending_data if s['transaction_count'] > 10 and s['average_transaction'] < 20]
            if frequent_small:
                insights.append("Consider reviewing frequent small transactions - they can add up quickly")
                
        return insights
    
    async def analyze_spending_trends(self, timeframe: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spending trends over time with cognitive insights"""
        start_date = timeframe.get('start_date')
        end_date = timeframe.get('end_date')
        
        if not self.connection:
            # Return mock data for demonstration
            return await self._generate_mock_trend_analysis(timeframe)
            
        # Real implementation would query GnuCash database for trend data
        cursor = self.connection.cursor()
        
        # Query monthly spending patterns
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', t.post_date) as month,
                account_name,
                SUM(ABS(amount)) as monthly_total,
                COUNT(*) as transaction_count
            FROM transactions t
            JOIN splits s ON t.guid = s.tx_guid  
            WHERE t.post_date BETWEEN ? AND ?
            AND amount < 0  -- Expenses only
            GROUP BY month, account_name
            ORDER BY month, monthly_total DESC
        """, (start_date, end_date))
        
        monthly_data = cursor.fetchall()
        return await self._process_trend_data(monthly_data, timeframe)
    
    async def _generate_mock_trend_analysis(self, timeframe: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock trend analysis for demonstration"""
        return {
            "timeframe": timeframe,
            "trend_analysis": {
                "overall_trend": "increasing",
                "trend_percentage": 5.2,
                "seasonal_patterns": [
                    {"pattern": "holiday_spending", "months": ["November", "December"], "impact": "+15%"},
                    {"pattern": "summer_travel", "months": ["July", "August"], "impact": "+8%"}
                ],
                "category_trends": [
                    {"category": "groceries", "trend": "stable", "variance": 2.1},
                    {"category": "gas", "trend": "decreasing", "variance": -3.4},
                    {"category": "entertainment", "trend": "increasing", "variance": 12.8}
                ]
            },
            "cognitive_insights": [
                "Your spending shows seasonal patterns consistent with typical consumer behavior",
                "Entertainment spending is increasing faster than other categories - consider setting limits",
                "Gas expenses are decreasing, possibly due to changed commuting patterns"
            ],
            "recommendations": [
                "Set aside 15% extra budget for November-December holiday spending",
                "Consider entertainment budget cap to control growing expenses",
                "Redirect gas savings toward emergency fund or investments"
            ]
        }
    
    async def detect_anomalies(self, transaction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect spending anomalies using pattern analysis"""
        anomalies = []
        
        if not transaction_history:
            return {"anomalies": [], "analysis": "No transaction data available"}
        
        # Calculate statistical baselines
        amounts = [abs(float(t.get('amount', 0))) for t in transaction_history]
        if not amounts:
            return {"anomalies": [], "analysis": "No valid transaction amounts"}
        
        avg_amount = sum(amounts) / len(amounts)
        max_amount = max(amounts)
        
        # Anomaly detection rules
        for transaction in transaction_history:
            amount = abs(float(transaction.get('amount', 0)))
            description = transaction.get('description', '')
            
            # Large transaction anomaly
            if amount > avg_amount * 3:
                anomalies.append({
                    "type": "large_transaction",
                    "transaction": transaction,
                    "severity": "high" if amount > avg_amount * 5 else "medium",
                    "reason": f"Amount ${amount:.2f} is {amount/avg_amount:.1f}x larger than average",
                    "recommendation": "Review transaction details and verify legitimacy"
                })
            
            # Unusual merchant anomaly
            if any(suspicious in description.lower() for suspicious in ['unknown', 'pending', 'hold']):
                anomalies.append({
                    "type": "unusual_merchant",
                    "transaction": transaction,
                    "severity": "medium",
                    "reason": f"Unusual merchant description: {description}",
                    "recommendation": "Verify merchant and transaction purpose"
                })
        
        return {
            "anomalies": anomalies,
            "analysis": f"Analyzed {len(transaction_history)} transactions, found {len(anomalies)} anomalies",
            "baseline_stats": {
                "average_amount": avg_amount,
                "max_amount": max_amount,
                "total_transactions": len(transaction_history)
            }
        }


class BudgetPlannerAgent(FinancialAgent):
    """ElizaOS agent for budget planning and management"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.budget_goals = agent_config.get('budget_goals', {})
        
    async def generate_report(self, report_type: str) -> Dict[str, Any]:
        """Generate budget-related reports"""
        if report_type == 'budget_vs_actual':
            return await self._budget_vs_actual_report()
        elif report_type == 'budget_recommendations':
            return await self._budget_recommendations()
        else:
            return {"error": f"Unknown report type: {report_type}"}
            
    async def _budget_vs_actual_report(self) -> Dict[str, Any]:
        """Compare budget goals vs actual spending"""
        if not self.connection:
            return {"error": "No GnuCash connection available"}
            
        # Get current month spending
        current_month = datetime.now().strftime('%Y-%m')
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT account_name, SUM(ABS(amount)) as spent
            FROM transactions t
            JOIN splits s ON t.guid = s.tx_guid
            WHERE strftime('%Y-%m', t.post_date) = ?
            AND amount < 0
            GROUP BY account_name
        """, (current_month,))
        
        actual_spending = {row[0]: row[1] for row in cursor.fetchall()}
        
        budget_comparison = []
        for category, budgeted in self.budget_goals.items():
            actual = actual_spending.get(category, 0)
            variance = actual - budgeted
            percentage_used = (actual / budgeted * 100) if budgeted > 0 else 0
            
            budget_comparison.append({
                'category': category,
                'budgeted': budgeted,
                'actual': actual,
                'variance': variance,
                'percentage_used': percentage_used,
                'status': 'over' if variance > 0 else 'under'
            })
            
        return {
            "report_type": "budget_vs_actual",
            "period": current_month,
            "comparison": budget_comparison,
            "generated_at": datetime.now().isoformat()
        }
        
    async def _budget_recommendations(self) -> Dict[str, Any]:
        """Generate budget optimization recommendations"""
        # Analyze spending patterns and suggest improvements
        recommendations = [
            "Review categories where you're consistently over budget",
            "Consider setting up automatic savings transfers",
            "Track discretionary spending more closely"
        ]
        
        return {
            "report_type": "budget_recommendations", 
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }


class FinancialAlertAgent(FinancialAgent):
    """ElizaOS agent for financial alerts and notifications"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.alert_rules = agent_config.get('alert_rules', [])
        
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for financial alert conditions"""
        alerts = []
        
        # Check for unusual transactions
        unusual_transactions = await self._detect_unusual_transactions()
        for transaction in unusual_transactions:
            alerts.append({
                'type': 'unusual_transaction',
                'severity': 'medium',
                'message': f"Unusual transaction detected: ${transaction['amount']} at {transaction['description']}",
                'transaction_id': transaction['id']
            })
            
        # Check budget overruns
        budget_alerts = await self._check_budget_overruns()
        alerts.extend(budget_alerts)
        
        return alerts
        
    async def _detect_unusual_transactions(self) -> List[Dict[str, Any]]:
        """Detect transactions that are unusually large or from new merchants"""
        # TODO: Implement statistical analysis for unusual transactions
        return []
        
    async def _check_budget_overruns(self) -> List[Dict[str, Any]]:
        """Check for budget category overruns"""
        # TODO: Compare current spending vs budget limits
        return []


# Integration utility functions

async def create_financial_agent_network(config: Dict[str, Any]) -> Dict[str, FinancialAgent]:
    """Create a network of coordinated financial agents"""
    agents = {}
    
    # Initialize each agent type
    if config.get('enable_categorizer', True):
        agents['categorizer'] = TransactionCategorizerAgent(config)
        await agents['categorizer'].initialize()
        
    if config.get('enable_analyzer', True):
        agents['analyzer'] = ExpenseAnalyzerAgent(config)
        await agents['analyzer'].initialize()
        
    if config.get('enable_planner', True):
        agents['planner'] = BudgetPlannerAgent(config)
        await agents['planner'].initialize()
        
    if config.get('enable_alerts', True):
        agents['alerts'] = FinancialAlertAgent(config)
        await agents['alerts'].initialize()
        
    return agents

async def process_financial_event(agents: Dict[str, FinancialAgent], event: Dict[str, Any]) -> Dict[str, Any]:
    """Process a financial event through the agent network"""
    event_type = event.get('type')
    results = {}
    
    if event_type == 'new_transaction':
        if 'categorizer' in agents:
            results['categorization'] = await agents['categorizer'].process_transaction(event['data'])
            
    elif event_type == 'analysis_request':
        if 'analyzer' in agents:
            results['analysis'] = await agents['analyzer'].analyze_spending(event['data'])
            
    elif event_type == 'budget_check':
        if 'planner' in agents:
            results['budget_report'] = await agents['planner'].generate_report('budget_vs_actual')
            
    return results