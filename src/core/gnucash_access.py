#!/usr/bin/env python3
"""
GnuCash Database Access Patterns for ElizaOS-OpenCog Integration
Phase 1: Foundation infrastructure for financial data integration
"""

import sqlite3
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

class GnuCashDataAccess:
    """
    Core GnuCash database access layer
    Provides foundation patterns for financial data integration
    """
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.connection = None
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize GnuCash database connection"""
        try:
            logger.info(f"Initializing GnuCash database connection: {self.database_path}")
            
            # Check if database file exists
            if not Path(self.database_path).exists():
                logger.warning(f"GnuCash database file not found: {self.database_path}")
                # Create mock database for integration testing
                await self._create_mock_database()
            
            # Connect to database
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Verify database structure
            if await self._verify_database_structure():
                self.initialized = True
                logger.info("✅ GnuCash database connection initialized successfully")
                return True
            else:
                logger.error("❌ GnuCash database structure verification failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize GnuCash database: {e}")
            return False
    
    async def _create_mock_database(self):
        """Create a mock GnuCash database for testing"""
        logger.info("Creating mock GnuCash database for integration testing...")
        
        # Create directory if needed
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with basic GnuCash schema
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create accounts table
        cursor.execute('''
            CREATE TABLE accounts (
                guid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                commodity_guid TEXT,
                commodity_scu INTEGER,
                non_std_scu INTEGER,
                parent_guid TEXT,
                code TEXT,
                description TEXT,
                hidden INTEGER,
                placeholder INTEGER
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE transactions (
                guid TEXT PRIMARY KEY,
                currency_guid TEXT,
                num TEXT,
                post_date DATE,
                enter_date TIMESTAMP,
                description TEXT
            )
        ''')
        
        # Create splits table
        cursor.execute('''
            CREATE TABLE splits (
                guid TEXT PRIMARY KEY,
                tx_guid TEXT,
                account_guid TEXT,
                memo TEXT,
                action TEXT,
                reconcile_state TEXT,
                reconcile_date TIMESTAMP,
                value_num INTEGER,
                value_denom INTEGER,
                quantity_num INTEGER,
                quantity_denom INTEGER,
                lot_guid TEXT
            )
        ''')
        
        # Create commodities table
        cursor.execute('''
            CREATE TABLE commodities (
                guid TEXT PRIMARY KEY,
                namespace TEXT,
                mnemonic TEXT,
                fullname TEXT,
                cusip TEXT,
                fraction INTEGER,
                quote_flag INTEGER,
                quote_source TEXT,
                quote_tz TEXT
            )
        ''')
        
        # Insert sample data
        await self._insert_sample_data(cursor)
        
        conn.commit()
        conn.close()
        logger.info("Mock GnuCash database created successfully")
    
    async def _insert_sample_data(self, cursor):
        """Insert sample financial data for testing"""
        # Insert USD commodity
        cursor.execute('''
            INSERT INTO commodities (guid, namespace, mnemonic, fullname, fraction)
            VALUES ('usd-guid', 'CURRENCY', 'USD', 'US Dollar', 100)
        ''')
        
        # Insert root account
        cursor.execute('''
            INSERT INTO accounts (guid, name, account_type, commodity_guid, parent_guid)
            VALUES ('root-guid', 'Root Account', 'ROOT', 'usd-guid', NULL)
        ''')
        
        # Insert asset accounts
        cursor.execute('''
            INSERT INTO accounts (guid, name, account_type, commodity_guid, parent_guid)
            VALUES ('checking-guid', 'Checking Account', 'BANK', 'usd-guid', 'root-guid')
        ''')
        
        cursor.execute('''
            INSERT INTO accounts (guid, name, account_type, commodity_guid, parent_guid)
            VALUES ('savings-guid', 'Savings Account', 'BANK', 'usd-guid', 'root-guid')
        ''')
        
        # Insert expense accounts
        cursor.execute('''
            INSERT INTO accounts (guid, name, account_type, commodity_guid, parent_guid)
            VALUES ('groceries-guid', 'Groceries', 'EXPENSE', 'usd-guid', 'root-guid')
        ''')
        
        cursor.execute('''
            INSERT INTO accounts (guid, name, account_type, commodity_guid, parent_guid)
            VALUES ('utilities-guid', 'Utilities', 'EXPENSE', 'usd-guid', 'root-guid')
        ''')
        
        # Insert sample transaction
        cursor.execute('''
            INSERT INTO transactions (guid, currency_guid, post_date, enter_date, description)
            VALUES ('tx1-guid', 'usd-guid', '2024-01-15', '2024-01-15 10:30:00', 'Grocery Shopping')
        ''')
        
        # Insert splits for the transaction
        cursor.execute('''
            INSERT INTO splits (guid, tx_guid, account_guid, memo, value_num, value_denom, quantity_num, quantity_denom)
            VALUES ('split1-guid', 'tx1-guid', 'checking-guid', 'Payment for groceries', -8550, 100, -8550, 100)
        ''')
        
        cursor.execute('''
            INSERT INTO splits (guid, tx_guid, account_guid, memo, value_num, value_denom, quantity_num, quantity_denom)
            VALUES ('split2-guid', 'tx1-guid', 'groceries-guid', 'Grocery purchase', 8550, 100, 8550, 100)
        ''')
    
    async def _verify_database_structure(self) -> bool:
        """Verify GnuCash database has required tables"""
        try:
            cursor = self.connection.cursor()
            
            # Check for required tables
            required_tables = ['accounts', 'transactions', 'splits', 'commodities']
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table not in existing_tables:
                    logger.error(f"Required table '{table}' not found in database")
                    return False
            
            logger.info("GnuCash database structure verified")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying database structure: {e}")
            return False
    
    async def get_accounts(self, account_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get accounts, optionally filtered by type"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        cursor = self.connection.cursor()
        
        if account_type:
            cursor.execute(
                "SELECT * FROM accounts WHERE account_type = ? ORDER BY name",
                (account_type,)
            )
        else:
            cursor.execute("SELECT * FROM accounts ORDER BY name")
        
        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                'guid': row['guid'],
                'name': row['name'],
                'account_type': row['account_type'],
                'commodity_guid': row['commodity_guid'],
                'parent_guid': row['parent_guid'],
                'description': row['description']
            })
        
        return accounts
    
    async def get_account_balance(self, account_guid: str) -> Decimal:
        """Get current balance for an account"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        cursor = self.connection.cursor()
        
        cursor.execute('''
            SELECT SUM(CAST(value_num AS REAL) / value_denom) as balance
            FROM splits 
            WHERE account_guid = ?
        ''', (account_guid,))
        
        result = cursor.fetchone()
        balance = result['balance'] if result['balance'] else 0.0
        
        return Decimal(str(balance))
    
    async def get_transactions(self, 
                             account_guid: Optional[str] = None,
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """Get transactions with optional filtering"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        cursor = self.connection.cursor()
        
        # Build query with optional filters
        query = '''
            SELECT t.*, s.account_guid, s.memo, s.value_num, s.value_denom,
                   a.name as account_name, a.account_type
            FROM transactions t
            JOIN splits s ON t.guid = s.tx_guid
            JOIN accounts a ON s.account_guid = a.guid
            WHERE 1=1
        '''
        
        params = []
        
        if account_guid:
            query += " AND s.account_guid = ?"
            params.append(account_guid)
        
        if start_date:
            query += " AND t.post_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND t.post_date <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY t.post_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'transaction_guid': row['guid'],
                'description': row['description'],
                'post_date': row['post_date'],
                'account_guid': row['account_guid'],
                'account_name': row['account_name'],
                'account_type': row['account_type'],
                'memo': row['memo'],
                'amount': Decimal(row['value_num']) / Decimal(row['value_denom']),
                'enter_date': row['enter_date']
            })
        
        return transactions
    
    async def get_spending_by_category(self, 
                                     start_date: date,
                                     end_date: date) -> Dict[str, Decimal]:
        """Get spending totals by expense category"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        cursor = self.connection.cursor()
        
        cursor.execute('''
            SELECT a.name as category, 
                   SUM(CAST(s.value_num AS REAL) / s.value_denom) as total
            FROM transactions t
            JOIN splits s ON t.guid = s.tx_guid
            JOIN accounts a ON s.account_guid = a.guid
            WHERE a.account_type = 'EXPENSE'
            AND t.post_date >= ?
            AND t.post_date <= ?
            AND s.value_num > 0
            GROUP BY a.name
            ORDER BY total DESC
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        spending = {}
        for row in cursor.fetchall():
            category = row['category']
            total = Decimal(str(row['total'])) if row['total'] else Decimal('0')
            spending[category] = total
        
        return spending
    
    async def get_income_by_category(self,
                                   start_date: date,
                                   end_date: date) -> Dict[str, Decimal]:
        """Get income totals by income category"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        cursor = self.connection.cursor()
        
        cursor.execute('''
            SELECT a.name as category,
                   SUM(CAST(s.value_num AS REAL) / s.value_denom) as total
            FROM transactions t
            JOIN splits s ON t.guid = s.tx_guid  
            JOIN accounts a ON s.account_guid = a.guid
            WHERE a.account_type = 'INCOME'
            AND t.post_date >= ?
            AND t.post_date <= ?
            AND s.value_num < 0
            GROUP BY a.name
            ORDER BY total DESC
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        income = {}
        for row in cursor.fetchall():
            category = row['category']
            total = abs(Decimal(str(row['total']))) if row['total'] else Decimal('0')
            income[category] = total
        
        return income
    
    async def search_transactions(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search transactions by description or memo"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        cursor = self.connection.cursor()
        
        search_pattern = f"%{search_term}%"
        
        cursor.execute('''
            SELECT t.*, s.account_guid, s.memo, s.value_num, s.value_denom,
                   a.name as account_name, a.account_type
            FROM transactions t
            JOIN splits s ON t.guid = s.tx_guid
            JOIN accounts a ON s.account_guid = a.guid
            WHERE (t.description LIKE ? OR s.memo LIKE ?)
            ORDER BY t.post_date DESC
            LIMIT ?
        ''', (search_pattern, search_pattern, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'transaction_guid': row['guid'],
                'description': row['description'],
                'post_date': row['post_date'],
                'account_name': row['account_name'],
                'memo': row['memo'],
                'amount': Decimal(row['value_num']) / Decimal(row['value_denom'])
            })
        
        return results
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.initialized = False
            logger.info("GnuCash database connection closed")


class FinancialPatternAnalyzer:
    """
    Analyzer for detecting patterns in financial data
    Provides foundation for cognitive analysis integration
    """
    
    def __init__(self, data_access: GnuCashDataAccess):
        self.data_access = data_access
    
    async def analyze_spending_trends(self, 
                                    months: int = 6) -> Dict[str, Any]:
        """Analyze spending trends over time"""
        end_date = date.today()
        start_date = date(end_date.year, end_date.month - months, 1)
        
        # Get spending data
        spending = await self.data_access.get_spending_by_category(start_date, end_date)
        
        # Calculate trends
        total_spending = sum(spending.values())
        category_percentages = {}
        
        for category, amount in spending.items():
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            category_percentages[category] = float(percentage)
        
        # Identify top categories
        top_categories = sorted(spending.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'period': f"{start_date} to {end_date}",
            'total_spending': float(total_spending),
            'category_breakdown': {k: float(v) for k, v in spending.items()},
            'category_percentages': category_percentages,
            'top_categories': [(cat, float(amt)) for cat, amt in top_categories],
            'analysis_insights': await self._generate_spending_insights(spending, total_spending)
        }
    
    async def _generate_spending_insights(self, 
                                        spending: Dict[str, Decimal],
                                        total: Decimal) -> List[str]:
        """Generate insights from spending data"""
        insights = []
        
        if total > Decimal('1000'):
            insights.append("Significant spending activity detected")
        
        # Find largest category
        if spending:
            largest_category = max(spending.items(), key=lambda x: x[1])
            percentage = (largest_category[1] / total * 100) if total > 0 else 0
            
            if percentage > 40:
                insights.append(f"High concentration of spending in {largest_category[0]} ({percentage:.1f}%)")
            
            if 'Groceries' in spending and spending['Groceries'] > total * Decimal('0.15'):
                insights.append("Grocery spending represents significant portion of expenses")
        
        if len(spending) > 5:
            insights.append("Diverse spending across multiple categories")
        elif len(spending) <= 2:
            insights.append("Concentrated spending in few categories")
        
        return insights
    
    async def detect_anomalies(self, 
                             account_guid: str,
                             days: int = 30) -> List[Dict[str, Any]]:
        """Detect unusual transactions or patterns"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        transactions = await self.data_access.get_transactions(
            account_guid=account_guid,
            start_date=start_date,
            end_date=end_date
        )
        
        if not transactions:
            return []
        
        # Calculate statistics
        amounts = [abs(float(tx['amount'])) for tx in transactions]
        mean_amount = sum(amounts) / len(amounts)
        
        # Simple anomaly detection - amounts > 2 standard deviations from mean
        import statistics
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        threshold = mean_amount + (2 * std_dev)
        
        anomalies = []
        for tx in transactions:
            amount = abs(float(tx['amount']))
            if amount > threshold:
                anomalies.append({
                    'transaction': tx,
                    'anomaly_type': 'high_amount',
                    'amount': amount,
                    'threshold': threshold,
                    'deviation': amount - mean_amount
                })
        
        return anomalies