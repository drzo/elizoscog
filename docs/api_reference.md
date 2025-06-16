# API Reference

## ElizaOS-OpenCog-GnuCash Integration Framework API

This document provides comprehensive API documentation for all bridge components and integration interfaces.

## Table of Contents

- [Core Bridge Components](#core-bridge-components)
- [Financial Integration API](#financial-integration-api)
- [Cognitive Processing API](#cognitive-processing-api)
- [Configuration API](#configuration-api)
- [Error Handling](#error-handling)

## Core Bridge Components

### AtomSpaceProvider

The `AtomSpaceProvider` class provides ElizaOS access to OpenCog AtomSpace operations.

#### Class Definition

```python
class AtomSpaceProvider:
    """ElizaOS provider for OpenCog AtomSpace operations"""
    
    def __init__(self, atomspace_config: Dict[str, Any])
```

#### Methods

##### `async initialize()`

Initialize connection to AtomSpace.

**Returns:** None

**Raises:** `ConnectionError` if AtomSpace is unreachable

**Example:**
```python
provider = AtomSpaceProvider({'host': 'localhost', 'port': 17001})
await provider.initialize()
```

##### `async store_knowledge(knowledge: Dict[str, Any]) -> bool`

Store knowledge in AtomSpace format.

**Parameters:**
- `knowledge` (Dict[str, Any]): Knowledge data to store

**Returns:** `bool` - True if successful

**Example:**
```python
knowledge = {
    'type': 'conversation',
    'content': 'User asked about spending',
    'context': {'user_id': 'user123'},
    'timestamp': '2025-06-16T10:00:00Z'
}
success = await provider.store_knowledge(knowledge)
```

##### `async query_knowledge(query: str) -> List[Dict[str, Any]]`

Query AtomSpace using pattern matching.

**Parameters:**
- `query` (str): Search query string

**Returns:** `List[Dict[str, Any]]` - Matching knowledge items

**Example:**
```python
results = await provider.query_knowledge("spending groceries")
for result in results:
    print(result['content'])
```

##### `async apply_reasoning(context: Dict[str, Any]) -> Dict[str, Any]`

Apply cognitive reasoning to context.

**Parameters:**
- `context` (Dict[str, Any]): Context for reasoning

**Returns:** `Dict[str, Any]` - Reasoning results

---

### CogServerAction

Interface for remote CogServer operations.

#### Class Definition

```python
class CogServerAction:
    """ElizaOS action interface for CogServer operations"""
    
    def __init__(self, cogserver_config: Dict[str, Any])
```

#### Methods

##### `async initialize()`

Initialize CogServer connection.

##### `async execute_action(action: str, params: Dict[str, Any]) -> Dict[str, Any]`

Execute action on CogServer.

**Parameters:**
- `action` (str): Action name to execute
- `params` (Dict[str, Any]): Action parameters

**Returns:** `Dict[str, Any]` - Action results

**Example:**
```python
result = await cogserver.execute_action('query', {
    'pattern': '(ConceptNode "spending")',
    'limit': 10
})
```

##### `async subscribe_events(event_types: List[str]) -> bool`

Subscribe to CogServer events.

**Parameters:**
- `event_types` (List[str]): Event types to subscribe to

**Returns:** `bool` - Success status

---

### PLNReasoner

Probabilistic Logic Networks reasoning service.

#### Class Definition

```python
class PLNReasoner:
    """ElizaOS reasoning service using PLN (Probabilistic Logic Networks)"""
    
    def __init__(self, pln_config: Dict[str, Any])
```

#### Methods

##### `async infer(premises: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

Perform PLN inference on premises.

**Parameters:**
- `premises` (List[Dict[str, Any]]): Input premises for reasoning

**Returns:** `List[Dict[str, Any]]` - Inference conclusions

**Example:**
```python
premises = [
    {'type': 'financial', 'content': 'User spent $200 on groceries', 'confidence': 0.9},
    {'type': 'historical', 'content': 'Average grocery spending is $150', 'confidence': 0.8}
]
conclusions = await reasoner.infer(premises)
```

##### `async validate_reasoning(conclusion: Dict[str, Any]) -> float`

Validate reasoning conclusion and return confidence.

**Parameters:**
- `conclusion` (Dict[str, Any]): Conclusion to validate

**Returns:** `float` - Confidence score (0.0 to 1.0)

---

### OpenCogAgentTemplate

Base template for creating OpenCog-powered ElizaOS agents.

#### Class Definition

```python
class OpenCogAgentTemplate:
    """Template for creating ElizaOS agents backed by OpenCog"""
    
    def __init__(self, agent_config: Dict[str, Any])
```

#### Configuration

```python
agent_config = {
    'atomspace': {
        'host': 'localhost',
        'port': 17001
    },
    'pln': {
        'rules_file': 'config/pln_rules.scm',
        'confidence_threshold': 0.1
    },
    'cogserver': {
        'host': 'localhost', 
        'port': 17020
    },
    'gnucash_file': '/path/to/financial_data.gnucash'  # Optional
}
```

#### Methods

##### `async initialize()`

Initialize all agent components.

##### `async process_message(message: str, context: Dict[str, Any]) -> str`

Process incoming message using cognitive pipeline.

**Parameters:**
- `message` (str): User message to process
- `context` (Dict[str, Any]): Message context

**Returns:** `str` - Generated response

**Example:**
```python
response = await agent.process_message(
    "How much did I spend last month?",
    {
        'user_id': 'user123',
        'session_id': 'session456',
        'timestamp': '2025-06-16T10:00:00Z'
    }
)
```

## Financial Integration API

### GnuCashDataAccess

Standardized data access patterns for GnuCash files.

#### Class Definition

```python
class GnuCashDataAccess:
    """Standardized data access patterns for GnuCash files"""
    
    def __init__(self, file_path: str)
```

#### Methods

##### `async initialize()`

Initialize connection to GnuCash data.

##### `async get_accounts(account_type: Optional[str] = None) -> List[Account]`

Get all accounts, optionally filtered by type.

**Parameters:**
- `account_type` (Optional[str]): Filter by account type

**Returns:** `List[Account]` - Account objects

##### `async get_transactions(start_date: Optional[date] = None, end_date: Optional[date] = None, account_guid: Optional[str] = None) -> List[Transaction]`

Get transactions with optional filters.

**Parameters:**
- `start_date` (Optional[date]): Start date filter
- `end_date` (Optional[date]): End date filter  
- `account_guid` (Optional[str]): Account GUID filter

**Returns:** `List[Transaction]` - Transaction objects

##### `async get_account_balance(account_guid: str) -> Decimal`

Get current balance for an account.

**Parameters:**
- `account_guid` (str): Account GUID

**Returns:** `Decimal` - Account balance

---

### FinancialReasoningEngine

PLN-based reasoning engine for financial data analysis.

#### Class Definition

```python
class FinancialReasoningEngine:
    """PLN-based reasoning engine for financial data analysis"""
    
    def __init__(self, gnucash_file: str, atomspace_config: Dict[str, Any])
```

#### Methods

##### `async analyze_spending_patterns(start_date: date, end_date: date) -> Dict[str, Any]`

Analyze spending patterns using PLN reasoning.

**Parameters:**
- `start_date` (date): Analysis start date
- `end_date` (date): Analysis end date

**Returns:** `Dict[str, Any]` - Analysis results

**Response Format:**
```python
{
    'period': '2025-05-16 to 2025-06-16',
    'spending_by_category': {
        'Groceries': 450.00,
        'Utilities': 200.00,
        'Entertainment': 150.00
    },
    'detected_patterns': [
        {
            'type': 'spending_spike',
            'category': 'Entertainment',
            'increase_ratio': 1.3,
            'confidence': 0.85
        }
    ],
    'cognitive_insights': [...],
    'reasoning_confidence': 0.8
}
```

##### `async predict_future_spending(category: str, months: int = 3) -> Dict[str, Any]`

Predict future spending using cognitive analysis.

**Parameters:**
- `category` (str): Spending category
- `months` (int): Prediction horizon in months

**Returns:** `Dict[str, Any]` - Prediction results

##### `async generate_financial_insights(user_context: Dict[str, Any]) -> List[Dict[str, Any]]`

Generate personalized financial insights using cognitive analysis.

**Parameters:**
- `user_context` (Dict[str, Any]): User context information

**Returns:** `List[Dict[str, Any]]` - Generated insights

##### `async answer_financial_question(question: str, context: Dict[str, Any]) -> Dict[str, Any]`

Answer natural language financial questions using cognitive reasoning.

**Parameters:**
- `question` (str): Natural language question
- `context` (Dict[str, Any]): Question context

**Returns:** `Dict[str, Any]` - Answer with metadata

**Response Format:**
```python
{
    'answer': 'Based on analysis, you spent $450 last month...',
    'confidence': 0.85,
    'type': 'spending_analysis',
    'data': {...}  # Additional analysis data
}
```

## Cognitive Processing API

### Data Models

#### Account

```python
@dataclass
class Account:
    guid: str
    name: str
    account_type: str
    parent_guid: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    commodity_guid: Optional[str] = None
```

#### Transaction

```python
@dataclass
class Transaction:
    guid: str
    currency_guid: str
    num: str
    post_date: date
    enter_date: datetime
    description: str
    splits: List[Split]
```

#### Split

```python
@dataclass
class Split:
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
```

## Configuration API

### Environment Variables

```bash
# OpenCog Configuration
ATOMSPACE_HOST=localhost
ATOMSPACE_PORT=17001
COGSERVER_HOST=localhost
COGSERVER_PORT=17020

# Financial Configuration
GNUCASH_FILE_PATH=/path/to/financial_data.gnucash
FINANCIAL_CONFIDENCE_THRESHOLD=0.7
SPENDING_ANALYSIS_LOOKBACK_DAYS=90

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/integration.log
```

### Configuration Objects

#### AtomSpace Configuration
```python
atomspace_config = {
    'host': 'localhost',
    'port': 17001,
    'timeout': 30,
    'retry_attempts': 3
}
```

#### PLN Configuration
```python
pln_config = {
    'rules_file': 'config/pln_rules.scm',
    'confidence_threshold': 0.1,
    'reasoning_steps': 100,
    'max_conclusions': 50
}
```

#### Financial Configuration
```python
financial_config = {
    'gnucash_file': '/path/to/data.gnucash',
    'analysis_lookback_days': 90,
    'confidence_threshold': 0.7,
    'prediction_horizon_months': 3
}
```

## Error Handling

### Exception Types

#### `ConnectionError`
Raised when connection to external services fails.

```python
try:
    await provider.initialize()
except ConnectionError as e:
    print(f"Failed to connect to AtomSpace: {e}")
```

#### `ValidationError`
Raised when input validation fails.

```python
from decimal import InvalidOperation

try:
    balance = await data_access.get_account_balance(account_guid)
except InvalidOperation as e:
    print(f"Invalid account data: {e}")
```

#### `ReasoningError`
Raised when PLN reasoning fails.

```python
try:
    conclusions = await reasoner.infer(premises)
except ReasoningError as e:
    print(f"Reasoning failed: {e}")
```

### Error Response Format

All API methods return errors in a consistent format:

```python
{
    'error': True,
    'error_type': 'ValidationError',
    'message': 'Invalid account GUID format',
    'details': {
        'input': 'invalid-guid',
        'expected_format': 'UUID string'
    },
    'timestamp': '2025-06-16T10:00:00Z'
}
```

### Logging

All components use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# Log levels used:
logger.debug("Detailed diagnostic information")
logger.info("General information about operation")
logger.warning("Something unexpected happened")
logger.error("Serious problem occurred")
logger.critical("Very serious error occurred")
```

## Rate Limiting

API calls are subject to rate limiting:

- **AtomSpace Operations**: 100 requests/minute
- **Financial Analysis**: 10 complex analyses/minute
- **PLN Reasoning**: 50 inference operations/minute

Rate limit headers are included in responses:

```python
{
    'X-RateLimit-Limit': '100',
    'X-RateLimit-Remaining': '95',
    'X-RateLimit-Reset': '1640995200'
}
```

## Versioning

The API uses semantic versioning. Current version: `v1.0.0`

Version is included in all responses:

```python
{
    'api_version': 'v1.0.0',
    'data': {...}
}
```

## Testing

### Unit Tests

```python
# Test AtomSpace provider
pytest tests/test_atomspace_provider.py

# Test financial reasoning
pytest tests/test_financial_reasoning.py

# Test complete integration
pytest tests/test_integration.py
```

### Integration Tests

```python
# Basic integration test
python3 test_integration_basic.py

# Phase 2 features test
python3 test_phase2_integration.py
```

### Performance Tests

```python
# Load testing
python3 tests/performance/test_load.py

# Memory usage testing  
python3 tests/performance/test_memory.py
```