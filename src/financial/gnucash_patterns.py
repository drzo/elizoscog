"""
GnuCash Database Access Patterns
Standardized patterns for accessing and processing GnuCash financial data
"""

import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Account:
    """Represents a GnuCash account"""
    guid: str
    name: str
    account_type: str
    parent_guid: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    commodity_guid: Optional[str] = None


@dataclass
class Transaction:
    """Represents a GnuCash transaction"""
    guid: str
    currency_guid: str
    num: str
    post_date: date
    enter_date: datetime
    description: str
    splits: List['Split']


@dataclass
class Split:
    """Represents a GnuCash split (part of a transaction)"""
    guid: str
    tx_guid: str
    account_guid: str
    memo: Optional[str]
    action: Optional[str]
    reconcile_state: str
    reconcile_date: Optional[date]
    value_num: int
    value_denom: int
    quantity_num: int
    quantity_denom: int

    @property
    def value(self) -> Decimal:
        """Get the split value as a Decimal"""
        return Decimal(self.value_num) / Decimal(self.value_denom)

    @property
    def quantity(self) -> Decimal:
        """Get the split quantity as a Decimal"""
        return Decimal(self.quantity_num) / Decimal(self.quantity_denom)


class GnuCashDataAccess:
    """Standardized data access patterns for GnuCash files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.connection = None
        self.is_sqlite = file_path.endswith('.gnucash')
        self.is_xml = file_path.endswith('.xml') or file_path.endswith('.gnc')
        
    async def initialize(self):
        """Initialize connection to GnuCash data"""
        if self.is_sqlite:
            self.connection = sqlite3.connect(self.file_path)
            self.connection.row_factory = sqlite3.Row
        elif self.is_xml:
            logger.info("XML format detected - will parse on demand")
        else:
            raise ValueError(f"Unsupported file format: {self.file_path}")
    
    async def get_accounts(self, account_type: Optional[str] = None) -> List[Account]:
        """Get all accounts, optionally filtered by type"""
        if self.is_sqlite:
            return await self._get_accounts_sqlite(account_type)
        elif self.is_xml:
            return await self._get_accounts_xml(account_type)
        
    async def _get_accounts_sqlite(self, account_type: Optional[str] = None) -> List[Account]:
        """Get accounts from SQLite database"""
        query = """
        SELECT guid, name, account_type, parent_guid, code, description, commodity_guid
        FROM accounts
        """
        params = []
        
        if account_type:
            query += " WHERE account_type = ?"
            params.append(account_type)
            
        cursor = self.connection.execute(query, params)
        accounts = []
        
        for row in cursor.fetchall():
            accounts.append(Account(
                guid=row['guid'],
                name=row['name'],
                account_type=row['account_type'],
                parent_guid=row['parent_guid'],
                code=row['code'],
                description=row['description'],
                commodity_guid=row['commodity_guid']
            ))
            
        return accounts
    
    async def _get_accounts_xml(self, account_type: Optional[str] = None) -> List[Account]:
        """Get accounts from XML file"""
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        
        # Find namespace
        namespace = {'gnc': 'http://www.gnucash.org/XML/gnc'}
        
        accounts = []
        for account_elem in root.findall('.//gnc:account', namespace):
            account_type_elem = account_elem.find('.//act:type', {'act': 'http://www.gnucash.org/XML/act'})
            if account_type and account_type_elem is not None and account_type_elem.text != account_type:
                continue
                
            guid_elem = account_elem.find('.//act:id', {'act': 'http://www.gnucash.org/XML/act'})
            name_elem = account_elem.find('.//act:name', {'act': 'http://www.gnucash.org/XML/act'})
            
            if guid_elem is not None and name_elem is not None:
                accounts.append(Account(
                    guid=guid_elem.text,
                    name=name_elem.text,
                    account_type=account_type_elem.text if account_type_elem is not None else 'UNKNOWN'
                ))
                
        return accounts
    
    async def get_transactions(self, 
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             account_guid: Optional[str] = None) -> List[Transaction]:
        """Get transactions with optional filters"""
        if self.is_sqlite:
            return await self._get_transactions_sqlite(start_date, end_date, account_guid)
        elif self.is_xml:
            return await self._get_transactions_xml(start_date, end_date, account_guid)
    
    async def _get_transactions_sqlite(self, 
                                     start_date: Optional[date] = None,
                                     end_date: Optional[date] = None,
                                     account_guid: Optional[str] = None) -> List[Transaction]:
        """Get transactions from SQLite database"""
        query = """
        SELECT DISTINCT t.guid, t.currency_guid, t.num, t.post_date, t.enter_date, t.description
        FROM transactions t
        """
        params = []
        conditions = []
        
        if account_guid:
            query += " JOIN splits s ON t.guid = s.tx_guid"
            conditions.append("s.account_guid = ?")
            params.append(account_guid)
            
        if start_date:
            conditions.append("t.post_date >= ?")
            params.append(start_date.strftime('%Y-%m-%d'))
            
        if end_date:
            conditions.append("t.post_date <= ?")
            params.append(end_date.strftime('%Y-%m-%d'))
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY t.post_date DESC"
        
        cursor = self.connection.execute(query, params)
        transactions = []
        
        for row in cursor.fetchall():
            # Get splits for this transaction
            splits = await self._get_splits_for_transaction(row['guid'])
            
            transactions.append(Transaction(
                guid=row['guid'],
                currency_guid=row['currency_guid'],
                num=row['num'],
                post_date=datetime.strptime(row['post_date'], '%Y-%m-%d').date(),
                enter_date=datetime.strptime(row['enter_date'], '%Y-%m-%d %H:%M:%S'),
                description=row['description'],
                splits=splits
            ))
            
        return transactions
    
    async def _get_splits_for_transaction(self, tx_guid: str) -> List[Split]:
        """Get all splits for a specific transaction"""
        query = """
        SELECT guid, tx_guid, account_guid, memo, action, reconcile_state, 
               reconcile_date, value_num, value_denom, quantity_num, quantity_denom
        FROM splits
        WHERE tx_guid = ?
        """
        
        cursor = self.connection.execute(query, [tx_guid])
        splits = []
        
        for row in cursor.fetchall():
            reconcile_date = None
            if row['reconcile_date']:
                reconcile_date = datetime.strptime(row['reconcile_date'], '%Y-%m-%d').date()
                
            splits.append(Split(
                guid=row['guid'],
                tx_guid=row['tx_guid'],
                account_guid=row['account_guid'],
                memo=row['memo'],
                action=row['action'],
                reconcile_state=row['reconcile_state'],
                reconcile_date=reconcile_date,
                value_num=row['value_num'],
                value_denom=row['value_denom'],
                quantity_num=row['quantity_num'],
                quantity_denom=row['quantity_denom']
            ))
            
        return splits
    
    async def _get_transactions_xml(self, 
                                  start_date: Optional[date] = None,
                                  end_date: Optional[date] = None,
                                  account_guid: Optional[str] = None) -> List[Transaction]:
        """Get transactions from XML file - simplified implementation"""
        # XML parsing for transactions is more complex
        # This is a placeholder for the full implementation
        logger.warning("XML transaction parsing not fully implemented")
        return []
    
    async def get_account_balance(self, account_guid: str) -> Decimal:
        """Get current balance for an account"""
        query = """
        SELECT SUM(CAST(quantity_num AS REAL) / quantity_denom) as balance
        FROM splits
        WHERE account_guid = ?
        """
        
        cursor = self.connection.execute(query, [account_guid])
        result = cursor.fetchone()
        
        return Decimal(str(result['balance'] or 0))
    
    async def get_account_hierarchy(self) -> Dict[str, List[str]]:
        """Get the account hierarchy structure"""
        accounts = await self.get_accounts()
        hierarchy = {}
        
        for account in accounts:
            if account.parent_guid:
                if account.parent_guid not in hierarchy:
                    hierarchy[account.parent_guid] = []
                hierarchy[account.parent_guid].append(account.guid)
            else:
                # Root account
                if 'root' not in hierarchy:
                    hierarchy['root'] = []
                hierarchy['root'].append(account.guid)
                
        return hierarchy
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


class FinancialAnalysisPatterns:
    """Common patterns for financial analysis"""
    
    def __init__(self, data_access: GnuCashDataAccess):
        self.data_access = data_access
    
    async def get_spending_by_category(self, 
                                     start_date: date,
                                     end_date: date) -> Dict[str, Decimal]:
        """Get spending grouped by account category"""
        transactions = await self.data_access.get_transactions(start_date, end_date)
        spending = {}
        
        for transaction in transactions:
            for split in transaction.splits:
                account = await self._get_account_name(split.account_guid)
                if account not in spending:
                    spending[account] = Decimal('0')
                
                # Only count negative values as spending
                if split.value < 0:
                    spending[account] += abs(split.value)
                    
        return spending
    
    async def _get_account_name(self, account_guid: str) -> str:
        """Get account name by GUID"""
        accounts = await self.data_access.get_accounts()
        for account in accounts:
            if account.guid == account_guid:
                return account.name
        return "Unknown"
    
    async def get_monthly_trends(self, account_guid: str, months: int = 12) -> List[Dict[str, Any]]:
        """Get monthly spending trends for an account"""
        # Implementation for monthly trend analysis
        trends = []
        
        # This would calculate month-over-month changes
        # Placeholder implementation
        for month in range(months):
            trends.append({
                'month': month,
                'amount': Decimal('0'),
                'change_percent': 0.0
            })
            
        return trends