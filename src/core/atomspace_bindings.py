#!/usr/bin/env python3
"""
Core OpenCog AtomSpace Python bindings integration for ElizaOS
Phase 1 implementation: Foundation infrastructure
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AtomSpaceCore:
    """
    Core AtomSpace implementation with Python bindings
    Provides foundation for OpenCog integration with ElizaOS
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.atoms = {}
        self.links = {}
        self.next_atom_id = 1
        self.next_link_id = 1
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize AtomSpace core with configuration"""
        try:
            logger.info("Initializing AtomSpace core...")
            
            # Set up basic atom types
            self.atom_types = {
                'ConceptNode': 'concept',
                'PredicateNode': 'predicate', 
                'NumberNode': 'number',
                'ListLink': 'list',
                'EvaluationLink': 'evaluation',
                'ImplicationLink': 'implication'
            }
            
            # Initialize memory structures
            self.atoms = {}
            self.links = {}
            self.truth_values = {}
            
            self.initialized = True
            logger.info("✅ AtomSpace core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AtomSpace core: {e}")
            return False
    
    def create_atom(self, atom_type: str, name: str, truth_value: Optional[Dict] = None) -> int:
        """Create an atom in the AtomSpace"""
        if not self.initialized:
            raise RuntimeError("AtomSpace not initialized")
        
        atom_id = self.next_atom_id
        self.next_atom_id += 1
        
        atom = {
            'id': atom_id,
            'type': atom_type,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'truth_value': truth_value or {'strength': 1.0, 'confidence': 1.0}
        }
        
        self.atoms[atom_id] = atom
        self.truth_values[atom_id] = atom['truth_value']
        
        logger.debug(f"Created {atom_type} atom '{name}' with ID {atom_id}")
        return atom_id
    
    def create_link(self, link_type: str, outgoing: List[int], truth_value: Optional[Dict] = None) -> int:
        """Create a link between atoms"""
        if not self.initialized:
            raise RuntimeError("AtomSpace not initialized")
        
        # Validate all outgoing atoms exist
        for atom_id in outgoing:
            if atom_id not in self.atoms and atom_id not in self.links:
                raise ValueError(f"Atom/Link {atom_id} does not exist")
        
        link_id = self.next_link_id
        self.next_link_id += 1
        
        link = {
            'id': link_id,
            'type': link_type,
            'outgoing': outgoing,
            'created_at': datetime.now().isoformat(),
            'truth_value': truth_value or {'strength': 1.0, 'confidence': 1.0}
        }
        
        self.links[link_id] = link
        self.truth_values[link_id] = link['truth_value']
        
        logger.debug(f"Created {link_type} link with ID {link_id} connecting {outgoing}")
        return link_id
    
    def get_atom(self, atom_id: int) -> Optional[Dict]:
        """Retrieve an atom by ID"""
        return self.atoms.get(atom_id)
    
    def get_link(self, link_id: int) -> Optional[Dict]:
        """Retrieve a link by ID"""
        return self.links.get(link_id)
    
    def query_by_type(self, atom_type: str) -> List[Dict]:
        """Query atoms by type"""
        results = []
        
        # Search atoms
        for atom in self.atoms.values():
            if atom['type'] == atom_type:
                results.append(atom)
        
        # Search links
        for link in self.links.values():
            if link['type'] == atom_type:
                results.append(link)
        
        return results
    
    def query_by_name(self, name: str) -> List[Dict]:
        """Query atoms by name pattern"""
        results = []
        name_lower = name.lower()
        
        for atom in self.atoms.values():
            if name_lower in atom['name'].lower():
                results.append(atom)
        
        return results
    
    def get_incoming_links(self, atom_id: int) -> List[Dict]:
        """Get all links that reference this atom"""
        incoming = []
        
        for link in self.links.values():
            if atom_id in link['outgoing']:
                incoming.append(link)
        
        return incoming
    
    def get_atom_count(self) -> int:
        """Get total number of atoms"""
        return len(self.atoms)
    
    def get_link_count(self) -> int:
        """Get total number of links"""
        return len(self.links)
    
    def export_atomspace(self) -> Dict:
        """Export entire AtomSpace as JSON"""
        return {
            'atoms': self.atoms,
            'links': self.links,
            'truth_values': self.truth_values,
            'atom_types': self.atom_types,
            'metadata': {
                'atom_count': self.get_atom_count(),
                'link_count': self.get_link_count(),
                'exported_at': datetime.now().isoformat()
            }
        }


class FinancialAtomSpace(AtomSpaceCore):
    """
    Specialized AtomSpace for financial domain
    Extends core with financial-specific patterns and structures
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.financial_concepts = {}
        self.account_atoms = {}
        self.transaction_links = {}
    
    async def initialize(self) -> bool:
        """Initialize financial AtomSpace with domain-specific setup"""
        if not await super().initialize():
            return False
        
        try:
            # Create financial domain concepts
            self.financial_concepts['account'] = self.create_atom(
                'ConceptNode', 'FinancialAccount'
            )
            self.financial_concepts['transaction'] = self.create_atom(
                'ConceptNode', 'Transaction'
            )
            self.financial_concepts['money'] = self.create_atom(
                'ConceptNode', 'Money'
            )
            self.financial_concepts['category'] = self.create_atom(
                'ConceptNode', 'ExpenseCategory'
            )
            
            logger.info("✅ Financial AtomSpace initialized with domain concepts")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize financial AtomSpace: {e}")
            return False
    
    def create_account_atom(self, account_name: str, account_type: str, balance: float = 0.0) -> int:
        """Create an atom representing a financial account"""
        account_atom = self.create_atom('ConceptNode', f"Account-{account_name}")
        
        # Create type link
        type_atom = self.create_atom('ConceptNode', account_type)
        type_link = self.create_link('EvaluationLink', [
            self.create_atom('PredicateNode', 'AccountType'),
            self.create_link('ListLink', [account_atom, type_atom])
        ])
        
        # Create balance link
        balance_atom = self.create_atom('NumberNode', str(balance))
        balance_link = self.create_link('EvaluationLink', [
            self.create_atom('PredicateNode', 'Balance'),
            self.create_link('ListLink', [account_atom, balance_atom])
        ])
        
        self.account_atoms[account_name] = {
            'atom_id': account_atom,
            'type_link': type_link,
            'balance_link': balance_link
        }
        
        logger.info(f"Created account atom for '{account_name}' ({account_type})")
        return account_atom
    
    def create_transaction_link(self, from_account: str, to_account: str, amount: float, description: str) -> int:
        """Create a link representing a financial transaction"""
        # Get or create account atoms
        if from_account not in self.account_atoms:
            self.create_account_atom(from_account, 'Unknown')
        if to_account not in self.account_atoms:
            self.create_account_atom(to_account, 'Unknown')
        
        from_atom = self.account_atoms[from_account]['atom_id']
        to_atom = self.account_atoms[to_account]['atom_id']
        amount_atom = self.create_atom('NumberNode', str(amount))
        desc_atom = self.create_atom('ConceptNode', description)
        
        # Create transaction link
        transaction_link = self.create_link('EvaluationLink', [
            self.create_atom('PredicateNode', 'Transaction'),
            self.create_link('ListLink', [from_atom, to_atom, amount_atom, desc_atom])
        ])
        
        transaction_id = f"{from_account}->{to_account}-{amount}"
        self.transaction_links[transaction_id] = transaction_link
        
        logger.info(f"Created transaction: {from_account} -> {to_account}: ${amount}")
        return transaction_link
    
    def get_account_balance(self, account_name: str) -> Optional[float]:
        """Get the current balance for an account"""
        if account_name not in self.account_atoms:
            return None
        
        balance_link_id = self.account_atoms[account_name]['balance_link']
        balance_link = self.get_link(balance_link_id)
        
        if balance_link:
            # Extract balance from link structure
            list_link_id = balance_link['outgoing'][1]
            list_link = self.get_link(list_link_id)
            balance_atom_id = list_link['outgoing'][1]
            balance_atom = self.get_atom(balance_atom_id)
            return float(balance_atom['name'])
        
        return 0.0
    
    def query_transactions_by_account(self, account_name: str) -> List[Dict]:
        """Query all transactions involving an account"""
        if account_name not in self.account_atoms:
            return []
        
        account_atom_id = self.account_atoms[account_name]['atom_id']
        transactions = []
        
        # Find transaction links that reference this account
        for link in self.links.values():
            if (link['type'] == 'EvaluationLink' and 
                len(link['outgoing']) >= 2):
                
                # Check if this is a transaction link
                predicate_id = link['outgoing'][0]
                predicate = self.get_atom(predicate_id)
                
                if predicate and predicate['name'] == 'Transaction':
                    list_link_id = link['outgoing'][1]
                    list_link = self.get_link(list_link_id)
                    
                    if (list_link and account_atom_id in list_link['outgoing']):
                        transactions.append({
                            'link_id': link['id'],
                            'link': link,
                            'created_at': link['created_at']
                        })
        
        return transactions