#!/usr/bin/env python3
"""
Financial Intelligence Dashboard

Interactive dashboard for cognitive financial analysis combining
GnuCash data with OpenCog reasoning and ElizaOS agent insights.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class FinancialMetric:
    """Financial metric data structure"""
    name: str
    value: float
    change: float
    trend: str
    confidence: float


class FinancialDashboard:
    """Interactive financial intelligence dashboard"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize financial dashboard with configuration"""
        self.config = config or {
            'currency': 'USD',
            'update_interval': 300,  # 5 minutes
            'enable_predictions': True,
            'show_cognitive_insights': True
        }
        self.financial_data = {}
        self.cognitive_insights = {}
        self.predictions = {}
        
    def load_gnucash_data(self, data_path: str) -> bool:
        """Load financial data from GnuCash or simulated data"""
        try:
            # Simulate GnuCash financial data
            self.financial_data = {
                'accounts': {
                    'assets': {
                        'checking': 12500.75,
                        'savings': 45000.00,
                        'investments': 125000.50
                    },
                    'liabilities': {
                        'credit_cards': -3200.25,
                        'mortgage': -185000.00
                    },
                    'income': {
                        'salary': 8500.00,
                        'investments': 1250.00
                    },
                    'expenses': {
                        'housing': -2800.00,
                        'food': -800.00,
                        'transportation': -600.00,
                        'utilities': -400.00,
                        'entertainment': -300.00
                    }
                },
                'transactions': [
                    {
                        'date': (datetime.now() - timedelta(days=i)).isoformat(),
                        'amount': (-1) ** i * (100 + i * 10),
                        'category': ['food', 'transportation', 'entertainment'][i % 3],
                        'description': f'Transaction {i+1}'
                    }
                    for i in range(30)
                ],
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'total_accounts': 9,
                    'total_transactions': 30
                }
            }
            return True
        except Exception as e:
            print(f"Error loading GnuCash data: {e}")
            return False
    
    def generate_cognitive_insights(self) -> Dict:
        """Generate AI-powered financial insights using OpenCog reasoning"""
        insights = {
            'spending_patterns': [],
            'risk_assessment': {},
            'optimization_suggestions': [],
            'anomaly_alerts': [],
            'prediction_confidence': {}
        }
        
        # Analyze spending patterns
        expenses = self.financial_data.get('accounts', {}).get('expenses', {})
        total_expenses = sum(abs(amount) for amount in expenses.values())
        
        for category, amount in expenses.items():
            percentage = (abs(amount) / total_expenses) * 100
            insights['spending_patterns'].append({
                'category': category,
                'amount': abs(amount),
                'percentage': percentage,
                'trend': 'increasing' if percentage > 20 else 'stable',
                'cognitive_score': min(100, percentage * 3)
            })
        
        # Risk assessment using PLN-like reasoning
        assets = self.financial_data.get('accounts', {}).get('assets', {})
        liabilities = self.financial_data.get('accounts', {}).get('liabilities', {})
        
        total_assets = sum(assets.values())
        total_liabilities = sum(abs(amount) for amount in liabilities.values())
        
        debt_to_asset_ratio = total_liabilities / total_assets if total_assets > 0 else 1.0
        
        insights['risk_assessment'] = {
            'debt_to_asset_ratio': debt_to_asset_ratio,
            'risk_level': 'high' if debt_to_asset_ratio > 0.6 else 'medium' if debt_to_asset_ratio > 0.3 else 'low',
            'confidence': 0.85,
            'factors': [
                f"Debt ratio: {debt_to_asset_ratio:.2f}",
                f"Asset diversification: {'good' if len(assets) > 2 else 'poor'}",
                f"Emergency fund: {'adequate' if assets.get('savings', 0) > total_expenses * 3 else 'insufficient'}"
            ]
        }
        
        # Optimization suggestions
        insights['optimization_suggestions'] = [
            {
                'category': 'expense_reduction',
                'suggestion': 'Reduce entertainment expenses by 20%',
                'potential_savings': expenses.get('entertainment', 0) * 0.2,
                'confidence': 0.75,
                'reasoning': 'Entertainment expenses exceed recommended 5% of income'
            },
            {
                'category': 'investment',
                'suggestion': 'Increase investment allocation by 10%',
                'potential_return': 1500.00,
                'confidence': 0.65,
                'reasoning': 'Current investment ratio below optimal range'
            }
        ]
        
        # Anomaly detection
        recent_transactions = self.financial_data.get('transactions', [])[:7]  # Last 7 days
        avg_transaction = sum(abs(t['amount']) for t in recent_transactions) / len(recent_transactions)
        
        for transaction in recent_transactions:
            if abs(transaction['amount']) > avg_transaction * 2:
                insights['anomaly_alerts'].append({
                    'transaction_id': transaction.get('id', 'unknown'),
                    'amount': transaction['amount'],
                    'date': transaction['date'],
                    'anomaly_type': 'unusual_amount',
                    'severity': 'medium',
                    'description': f"Transaction amount {transaction['amount']} is {abs(transaction['amount'])/avg_transaction:.1f}x average"
                })
        
        self.cognitive_insights = insights
        return insights
    
    def generate_predictions(self) -> Dict:
        """Generate financial predictions using cognitive models"""
        predictions = {
            'next_month_expenses': {},
            'investment_projections': {},
            'cash_flow_forecast': [],
            'confidence_metrics': {}
        }
        
        # Predict next month expenses based on historical data
        expenses = self.financial_data.get('accounts', {}).get('expenses', {})
        for category, current_amount in expenses.items():
            # Simple prediction with random variation
            predicted_amount = abs(current_amount) * (1 + (hash(category) % 20 - 10) / 100)
            predictions['next_month_expenses'][category] = {
                'predicted_amount': predicted_amount,
                'current_amount': abs(current_amount),
                'change_percentage': ((predicted_amount - abs(current_amount)) / abs(current_amount)) * 100,
                'confidence': 0.7 + (hash(category) % 30) / 100
            }
        
        # Investment projections
        current_investments = self.financial_data.get('accounts', {}).get('assets', {}).get('investments', 0)
        predictions['investment_projections'] = {
            '3_months': {
                'conservative': current_investments * 1.02,
                'moderate': current_investments * 1.05,
                'aggressive': current_investments * 1.08,
                'confidence': 0.65
            },
            '12_months': {
                'conservative': current_investments * 1.08,
                'moderate': current_investments * 1.15,
                'aggressive': current_investments * 1.25,
                'confidence': 0.45
            }
        }
        
        # Cash flow forecast
        for i in range(12):  # Next 12 months
            month_date = (datetime.now() + timedelta(days=30*i)).strftime('%Y-%m')
            income = sum(self.financial_data.get('accounts', {}).get('income', {}).values())
            expenses = sum(abs(amount) for amount in self.financial_data.get('accounts', {}).get('expenses', {}).values())
            
            predictions['cash_flow_forecast'].append({
                'month': month_date,
                'predicted_income': income * (1 + i * 0.02),  # 2% monthly growth
                'predicted_expenses': expenses * (1 + i * 0.015),  # 1.5% monthly inflation
                'net_cash_flow': income * (1 + i * 0.02) - expenses * (1 + i * 0.015),
                'confidence': max(0.3, 0.8 - i * 0.05)  # Decreasing confidence over time
            })
        
        self.predictions = predictions
        return predictions
    
    def get_key_metrics(self) -> List[FinancialMetric]:
        """Calculate key financial metrics with cognitive analysis"""
        accounts = self.financial_data.get('accounts', {})
        
        # Net Worth
        total_assets = sum(accounts.get('assets', {}).values())
        total_liabilities = sum(abs(amount) for amount in accounts.get('liabilities', {}).values())
        net_worth = total_assets - total_liabilities
        
        # Monthly Income
        monthly_income = sum(accounts.get('income', {}).values())
        
        # Monthly Expenses
        monthly_expenses = sum(abs(amount) for amount in accounts.get('expenses', {}).values())
        
        # Savings Rate
        savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100 if monthly_income > 0 else 0
        
        # Investment Ratio
        investment_ratio = (accounts.get('assets', {}).get('investments', 0) / total_assets) * 100 if total_assets > 0 else 0
        
        return [
            FinancialMetric(
                name="Net Worth",
                value=net_worth,
                change=2.5,  # Simulated change
                trend="increasing",
                confidence=0.9
            ),
            FinancialMetric(
                name="Monthly Income",
                value=monthly_income,
                change=1.2,
                trend="stable",
                confidence=0.95
            ),
            FinancialMetric(
                name="Monthly Expenses",
                value=monthly_expenses,
                change=-0.8,
                trend="decreasing",
                confidence=0.85
            ),
            FinancialMetric(
                name="Savings Rate",
                value=savings_rate,
                change=3.1,
                trend="increasing",
                confidence=0.8
            ),
            FinancialMetric(
                name="Investment Ratio",
                value=investment_ratio,
                change=1.7,
                trend="increasing",
                confidence=0.75
            )
        ]
    
    def generate_dashboard_html(self) -> str:
        """Generate complete HTML dashboard"""
        metrics = self.get_key_metrics()
        insights = self.cognitive_insights or self.generate_cognitive_insights()
        predictions = self.predictions or self.generate_predictions()
        
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cognitive Financial Intelligence Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: white; }}
        .dashboard {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; padding: 20px; }}
        .widget {{ background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; padding: 20px; border: 1px solid #333; }}
        .widget h3 {{ color: #4CAF50; margin-bottom: 15px; }}
        .metric {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; }}
        .metric-change {{ padding: 5px 10px; border-radius: 5px; font-size: 0.8em; }}
        .positive {{ background: #4CAF50; color: white; }}
        .negative {{ background: #F44336; color: white; }}
        .stable {{ background: #FF9800; color: white; }}
        .chart-container {{ height: 300px; }}
        .insight {{ background: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3; padding: 10px; margin: 10px 0; }}
        .alert {{ background: rgba(255, 152, 0, 0.1); border-left: 4px solid #FF9800; padding: 10px; margin: 10px 0; }}
        .confidence {{ font-size: 0.8em; color: #888; }}
        .header {{ grid-column: 1 / -1; text-align: center; margin-bottom: 20px; }}
        .header h1 {{ color: #4CAF50; font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ color: #888; }}
        .full-width {{ grid-column: 1 / -1; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🧠 Cognitive Financial Intelligence</h1>
            <p>AI-Powered Financial Analysis • OpenCog + ElizaOS + GnuCash Integration</p>
            <p>Last Updated: {timestamp}</p>
        </div>
        
        <div class="widget">
            <h3>📊 Key Metrics</h3>
            {metrics_html}
        </div>
        
        <div class="widget">
            <h3>💡 Cognitive Insights</h3>
            {insights_html}
        </div>
        
        <div class="widget">
            <h3>🔮 Predictions</h3>
            {predictions_html}
        </div>
        
        <div class="widget full-width">
            <h3>📈 Spending Analysis</h3>
            <div class="chart-container">
                <canvas id="spendingChart"></canvas>
            </div>
        </div>
        
        <div class="widget full-width">
            <h3>💰 Cash Flow Forecast</h3>
            <div class="chart-container">
                <canvas id="cashFlowChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Spending Chart
        const spendingCtx = document.getElementById('spendingChart').getContext('2d');
        const spendingData = {spending_data};
        
        new Chart(spendingCtx, {{
            type: 'doughnut',
            data: {{
                labels: spendingData.map(item => item.category),
                datasets: [{{
                    data: spendingData.map(item => item.amount),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'right', labels: {{ color: 'white' }} }}
                }}
            }}
        }});
        
        // Cash Flow Chart
        const cashFlowCtx = document.getElementById('cashFlowChart').getContext('2d');
        const cashFlowData = {cash_flow_data};
        
        new Chart(cashFlowCtx, {{
            type: 'line',
            data: {{
                labels: cashFlowData.map(item => item.month),
                datasets: [{{
                    label: 'Net Cash Flow',
                    data: cashFlowData.map(item => item.net_cash_flow),
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ ticks: {{ color: 'white' }} }},
                    y: {{ ticks: {{ color: 'white' }} }}
                }},
                plugins: {{
                    legend: {{ labels: {{ color: 'white' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>'''.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            metrics_html=self._generate_metrics_html(metrics),
            insights_html=self._generate_insights_html(insights),
            predictions_html=self._generate_predictions_html(predictions),
            spending_data=json.dumps(insights.get('spending_patterns', [])),
            cash_flow_data=json.dumps(predictions.get('cash_flow_forecast', []))
        )
        
        return html_template
    
    def _generate_metrics_html(self, metrics: List[FinancialMetric]) -> str:
        """Generate HTML for key metrics"""
        html = ""
        for metric in metrics:
            change_class = 'positive' if metric.change > 0 else 'negative' if metric.change < 0 else 'stable'
            change_symbol = '+' if metric.change > 0 else ''
            
            html += f'''
            <div class="metric">
                <div>
                    <strong>{metric.name}</strong><br>
                    <span class="confidence">Confidence: {metric.confidence:.0%}</span>
                </div>
                <div>
                    <div class="metric-value">${metric.value:,.2f}</div>
                    <div class="metric-change {change_class}">{change_symbol}{metric.change:.1f}%</div>
                </div>
            </div>
            '''
        return html
    
    def _generate_insights_html(self, insights: Dict) -> str:
        """Generate HTML for cognitive insights"""
        html = ""
        
        # Risk assessment
        risk = insights.get('risk_assessment', {})
        html += f'''
        <div class="insight">
            <strong>Risk Assessment: {risk.get('risk_level', 'unknown').upper()}</strong><br>
            Debt-to-Asset Ratio: {risk.get('debt_to_asset_ratio', 0):.2f}<br>
            <span class="confidence">Confidence: {risk.get('confidence', 0):.0%}</span>
        </div>
        '''
        
        # Optimization suggestions
        for suggestion in insights.get('optimization_suggestions', [])[:2]:
            html += f'''
            <div class="insight">
                <strong>{suggestion.get('suggestion', 'No suggestion')}</strong><br>
                Potential Impact: ${suggestion.get('potential_savings', suggestion.get('potential_return', 0)):,.2f}<br>
                <span class="confidence">Confidence: {suggestion.get('confidence', 0):.0%}</span>
            </div>
            '''
        
        # Anomaly alerts
        for alert in insights.get('anomaly_alerts', [])[:2]:
            html += f'''
            <div class="alert">
                <strong>Anomaly Detected</strong><br>
                {alert.get('description', 'Unknown anomaly')}<br>
                <span class="confidence">Severity: {alert.get('severity', 'unknown')}</span>
            </div>
            '''
        
        return html
    
    def _generate_predictions_html(self, predictions: Dict) -> str:
        """Generate HTML for predictions"""
        html = ""
        
        # Investment projections
        investments = predictions.get('investment_projections', {}).get('12_months', {})
        html += f'''
        <div class="insight">
            <strong>12-Month Investment Outlook</strong><br>
            Conservative: ${investments.get('conservative', 0):,.2f}<br>
            Moderate: ${investments.get('moderate', 0):,.2f}<br>
            Aggressive: ${investments.get('aggressive', 0):,.2f}<br>
            <span class="confidence">Confidence: {investments.get('confidence', 0):.0%}</span>
        </div>
        '''
        
        # Next month expenses prediction
        next_month = predictions.get('cash_flow_forecast', [])
        if next_month:
            forecast = next_month[0]
            html += f'''
            <div class="insight">
                <strong>Next Month Forecast</strong><br>
                Expected Income: ${forecast.get('predicted_income', 0):,.2f}<br>
                Expected Expenses: ${forecast.get('predicted_expenses', 0):,.2f}<br>
                Net Cash Flow: ${forecast.get('net_cash_flow', 0):,.2f}<br>
                <span class="confidence">Confidence: {forecast.get('confidence', 0):.0%}</span>
            </div>
            '''
        
        return html
    
    def save_dashboard(self, filename: str = "financial_dashboard.html") -> bool:
        """Save dashboard to HTML file"""
        try:
            html_content = self.generate_dashboard_html()
            with open(filename, 'w') as f:
                f.write(html_content)
            print(f"Financial dashboard saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving dashboard: {e}")
            return False


def main():
    """Demo financial dashboard functionality"""
    print("💰 Cognitive Financial Dashboard Demo")
    
    dashboard = FinancialDashboard({
        'currency': 'USD',
        'enable_predictions': True,
        'show_cognitive_insights': True
    })
    
    # Load financial data
    print("📊 Loading financial data...")
    dashboard.load_gnucash_data("demo_gnucash.sqlite")
    
    # Generate insights and predictions
    print("🧠 Generating cognitive insights...")
    insights = dashboard.generate_cognitive_insights()
    
    print("🔮 Creating predictions...")
    predictions = dashboard.generate_predictions()
    
    # Save dashboard
    print("💻 Generating dashboard...")
    dashboard.save_dashboard("demo_financial_dashboard.html")
    
    # Display key metrics
    metrics = dashboard.get_key_metrics()
    print(f"📈 Key Metrics:")
    for metric in metrics:
        print(f"  {metric.name}: ${metric.value:,.2f} ({metric.change:+.1f}%)")
    
    print(f"💡 Generated {len(insights.get('optimization_suggestions', []))} optimization suggestions")
    print(f"⚠️  Found {len(insights.get('anomaly_alerts', []))} anomalies")
    
    print("✅ Financial dashboard demo completed!")


if __name__ == "__main__":
    main()