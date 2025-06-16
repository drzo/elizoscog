# Installation and Setup Guide

## ElizaOS-OpenCog-GnuCash Integration Framework

This guide provides step-by-step instructions for setting up the complete integration framework.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher (for ElizaOS components)
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+ with WSL2

### Required Software
- **OpenCog AtomSpace**: Core cognitive architecture
- **ElizaOS Framework**: Multi-agent development platform  
- **GnuCash**: Personal finance management (optional for full features)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/drzo/elizoscog.git
cd elizoscog
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv elizoscog-env
source elizoscog-env/bin/activate  # On Windows: elizoscog-env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional financial processing dependencies
pip install sqlite3 xml.etree.ElementTree decimal
```

### 3. OpenCog AtomSpace Installation

#### Option A: Using Conda (Recommended)
```bash
conda install -c conda-forge opencog-atomspace
```

#### Option B: From Source
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install build-essential cmake cxxtest libboost-all-dev

# Clone and build AtomSpace
git clone https://github.com/opencog/atomspace.git
cd atomspace
mkdir build && cd build
cmake ..
make -j4
sudo make install
cd ../..
```

### 4. ElizaOS Framework Setup

```bash
# Install Node.js dependencies (if building ElizaOS components)
npm install -g @elizaos/core @elizaos/cli

# Verify ElizaOS installation
eliza --version
```

### 5. GnuCash Setup (Optional)

#### For Full Financial Features:
```bash
# Ubuntu/Debian
sudo apt-get install gnucash

# macOS
brew install --cask gnucash

# Windows
# Download from https://gnucash.org/download.phtml
```

## Configuration

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.template .env
```

Edit `.env` with your settings:

```env
# OpenCog Configuration
ATOMSPACE_HOST=localhost
ATOMSPACE_PORT=17001
COGSERVER_HOST=localhost  
COGSERVER_PORT=17020

# ElizaOS Configuration
ELIZAOS_API_KEY=your_api_key_here
ELIZAOS_BASE_URL=http://localhost:3000

# GnuCash Configuration (optional)
GNUCASH_FILE_PATH=/path/to/your/financial_data.gnucash
GNUCASH_BACKUP_PATH=/path/to/backups/

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/integration.log
```

### 2. OpenCog Configuration

Create `config/atomspace.conf`:

```conf
# AtomSpace Configuration
ATOMSPACE_PORT = 17001
ATOMSPACE_LOG_LEVEL = INFO
ATOMSPACE_LOG_FILE = logs/atomspace.log

# PLN Configuration  
PLN_RULES_PATH = config/pln_rules.scm
PLN_REASONING_STEPS = 100
PLN_CONFIDENCE_THRESHOLD = 0.1
```

### 3. Financial Configuration

Create `config/financial.conf`:

```conf
# Financial Analysis Configuration
SPENDING_ANALYSIS_LOOKBACK_DAYS = 90
BUDGET_VARIANCE_THRESHOLD = 0.1
TREND_ANALYSIS_MIN_DATAPOINTS = 5

# Reasoning Parameters
FINANCIAL_CONFIDENCE_THRESHOLD = 0.7
PREDICTION_HORIZON_MONTHS = 3
ANOMALY_DETECTION_SENSITIVITY = 0.8
```

## Verification

### 1. Run Basic Integration Tests

```bash
# Test core integration
python3 test_integration_basic.py

# Test Phase 2 features
python3 test_phase2_integration.py

# Test complete system integration
python3 test_complete_integration.py
```

### 2. Verify Component Connectivity

```bash
# Test AtomSpace connection
python3 -c "from src.bridges.elizaos_opencog import AtomSpaceProvider; import asyncio; asyncio.run(AtomSpaceProvider({}).initialize())"

# Test financial data access (if GnuCash file available)
python3 -c "from src.financial import GnuCashDataAccess; import asyncio; data = GnuCashDataAccess('your_file.gnucash'); asyncio.run(data.initialize())"
```

## Usage Examples

### 1. Basic Cognitive Agent

```python
from src.bridges.elizaos_opencog import OpenCogAgentTemplate

# Configure agent
config = {
    'atomspace': {'host': 'localhost', 'port': 17001},
    'pln': {'rules_file': 'config/pln_rules.scm'}
}

# Create and initialize agent
agent = OpenCogAgentTemplate(config)
await agent.initialize()

# Process messages
response = await agent.process_message("Hello, how are you?", {
    'user_id': 'user123',
    'session_id': 'session456'
})
print(response)
```

### 2. Financial Analysis Agent

```python
from src.bridges.elizaos_opencog import OpenCogAgentTemplate

# Configure agent with financial capabilities
config = {
    'atomspace': {'host': 'localhost', 'port': 17001},
    'pln': {'rules_file': 'config/financial_rules.scm'},
    'gnucash_file': '/path/to/your/financial_data.gnucash'
}

# Create agent with financial reasoning
agent = OpenCogAgentTemplate(config)
await agent.initialize()

# Ask financial questions
response = await agent.process_message("How much did I spend on groceries last month?", {
    'user_id': 'user123',
    'domain': 'financial'
})
print(response)
```

### 3. Direct Financial Analysis

```python
from src.financial import FinancialReasoningEngine

# Create reasoning engine
engine = FinancialReasoningEngine('/path/to/data.gnucash', {
    'host': 'localhost', 
    'port': 17001
})

await engine.initialize()

# Analyze spending patterns
from datetime import date, timedelta
end_date = date.today()
start_date = end_date - timedelta(days=30)

analysis = await engine.analyze_spending_patterns(start_date, end_date)
print(analysis)

# Generate insights
insights = await engine.generate_financial_insights({'user_id': 'user123'})
for insight in insights:
    print(f"{insight['type']}: {insight['title']}")
```

## Troubleshooting

### Common Issues

#### 1. AtomSpace Connection Failed
```bash
# Check if AtomSpace is running
ps aux | grep atomspace

# Start CogServer if needed
cd /path/to/opencog
./scripts/cogserver
```

#### 2. GnuCash File Access Issues
```bash
# Check file permissions
ls -la /path/to/your/financial_data.gnucash

# Ensure file is not locked by GnuCash application
# Close GnuCash before running integration tests
```

#### 3. Python Import Errors
```bash
# Verify Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 4. Memory Issues with Large Financial Files
```bash
# Increase Python memory limits
export PYTHONHASHSEED=0
ulimit -v 8388608  # 8GB virtual memory limit
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run your integration code
```

### Performance Optimization

#### For Large Financial Datasets:
1. **Database Indexing**: Ensure GnuCash SQLite files have proper indexes
2. **Memory Management**: Use streaming for large transaction sets
3. **Caching**: Enable AtomSpace caching for frequently accessed atoms

#### For Real-time Processing:
1. **Connection Pooling**: Reuse database connections
2. **Batch Processing**: Process multiple queries together
3. **Async Operations**: Use async/await throughout the pipeline

## Development Environment

### IDE Setup

#### VS Code Configuration
Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./elizoscog-env/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm Configuration
1. Set interpreter to `./elizoscog-env/bin/python`
2. Mark `src/` as Sources Root
3. Enable pytest as test runner

### Git Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Production Deployment

### Docker Setup

```bash
# Build container
docker build -t elizoscog-integration .

# Run with environment variables
docker run -e ATOMSPACE_HOST=your_host -e GNUCASH_FILE_PATH=/data/financial.gnucash elizoscog-integration
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

### Monitoring

Set up monitoring with:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards  
- **ELK Stack**: Log aggregation and analysis

## Support

### Documentation
- [API Reference](docs/api/)
- [Architecture Guide](docs/architecture/)
- [Integration Examples](docs/examples/)

### Community
- [GitHub Issues](https://github.com/drzo/elizoscog/issues)
- [Discussions](https://github.com/drzo/elizoscog/discussions)

### Professional Support
For commercial deployments and custom integrations, contact [Linas Vepstas](mailto:linasvepstas@gmail.com).