#!/usr/bin/env python3
"""
Update documentation files with integration information and cross-references
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any

def update_todo_oc(categorized_repos: Dict[str, List[Dict[str, Any]]]) -> str:
    """Update TODO-OC.md with detailed repository information"""
    
    content = """## The OpenCog Project 👋
[OpenCog aims to create AGI](https://wiki.opencog.org/w/The_Open_Cognition_Project)
with a combination of exploration, engineering and basic science research.
Side quests have included robotics systems ([Hanson Robotics](https://www.hansonrobotics.com)),
financial systems (Aidiya),
genomics (MOZI and [Rejuve.bio](https://www.rejuve.bio)),
machine learning ([predicting risk from clinician notes](https://doi.org/10.1371/journal.pone.0085733)),
natural language chatbots ([virtual dog playing fetch](https://www.youtube.com/watch?v=FEmpGRLwbqE)) and more.
This project was pioneered by [Dr. Ben Goertzel](https://en.wikipedia.org/wiki/Ben_Goertzel).

https://github.com/orgs/opencog/repositories?type=all

Git repos fall into four categories:

"""
    
    category_descriptions = {
        'atomspace': ("### OpenCog AtomSpace\n"
                     "The core of the system. As of 2025, it is active, stable and supported.\n\n"),
        'research': ("### OpenCog Research\n"
                    "Git repos in which active research is being carried out:\n"),
        'fossils': ("### OpenCog Fossils\n"
                   "Older, abandoned and obsolete components and experiments. These were attempts to build subsystems \n"
                   "with specific goals and ideas in mind. As experiments, they provided validation for certain design\n"
                   "ideas. They were educational and fun, but turned out to be unworkable. Thus, development has\n"
                   "halted. These projects are no longer maintained. They do contain useful subsystems that could be\n"
                   "salvaged for future use. This includes:\n"),
        'hyperon': ("### OpenCog Hyperon\n"
                   "Being developed by [Singularity.net](https://singularitynet.io).\n\n"),
        'incubator': ("### OpenCog Incubator\n"
                     "These are the immature, incomplete, promising projects that haven't taken off yet.\n\n")
    }
    
    # Add each category
    for category, repos in categorized_repos.items():
        if repos:
            content += category_descriptions.get(category, f"### {category.title()}\n\n")
            
            for repo in repos:
                desc = repo['description'] or 'No description available'
                # Truncate very long descriptions
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                
                content += f"* [{repo['name']}]({repo['html_url']}) - {desc}\n"
            
            content += "\n"
    
    # Add integration section
    content += """
## Integration with ElizaOS

### Cross-Ecosystem Components
OpenCog components can be integrated into ElizaOS as plugins and subsystems:

#### AtomSpace Integration
- **atomspace-python**: Python bindings for AtomSpace integration into ElizaOS agents
- **atomspace-js**: JavaScript/TypeScript bindings for web-based ElizaOS clients
- **cogserver-connector**: ElizaOS plugin for CogServer communication

#### Reasoning Integration  
- **pln-agent**: ElizaOS agent wrapper for PLN reasoning
- **pattern-matcher**: ElizaOS action for AtomSpace pattern matching
- **query-engine**: ElizaOS service for Atomese queries

#### Language Processing
- **link-grammar-plugin**: ElizaOS plugin for syntactic parsing
- **nlp-pipeline**: ElizaOS action chain for OpenCog NLP processing

### Implementation Roadmap
- [ ] Create Python binding layer for core AtomSpace in ElizaOS
- [ ] Implement CogServer connector plugin
- [ ] Design distributed reasoning coordination
- [ ] Build Atomese query interface for ElizaOS
- [ ] Create OpenCog agent templates for ElizaOS
- [ ] Implement hypergraph visualization for ElizaOS dashboard

## GnuCash Integration

### Hybrid Fractal Financial Structure
Integrating GnuCash financial management with cognitive architectures:

#### OpenCog Financial Reasoning
- **financial-atomspace**: Represent financial data as Atoms and Links
- **accounting-rules**: PLN rules for financial pattern recognition
- **transaction-analysis**: Cognitive analysis of spending patterns
- **budget-prediction**: AI-driven budget forecasting

#### ElizaOS Financial Agents
- **expense-tracker**: ElizaOS agent for automatic expense categorization
- **investment-advisor**: AI agent for investment recommendations
- **financial-alerts**: Smart notification system for financial events
- **budget-assistant**: Conversational budget planning agent

### Fractal Architecture
```
GnuCash (Financial Data)
├── OpenCog Layer (Cognitive Reasoning)
│   ├── AtomSpace (Knowledge Representation)
│   ├── PLN (Logical Reasoning)
│   └── Pattern Recognition
└── ElizaOS Layer (Agent Interactions)
    ├── Financial Agents
    ├── User Interfaces
    └── Multi-Agent Coordination
```

"""
    
    # Add help wanted section
    content += """
# HELP WANTED

## Development Priorities

### Core Infrastructure
- AtomSpace performance optimization
- Distributed processing enhancements  
- Cross-language binding improvements
- Integration testing frameworks

### Research Areas
- Hyperon-AtomSpace compatibility layers
- Advanced reasoning algorithms
- Multi-modal learning systems
- Real-time cognitive architectures

### Integration Projects
- ElizaOS-OpenCog bridge development
- GnuCash cognitive enhancement
- Financial reasoning frameworks
- Hybrid agent architectures

### Commercial support
If you are a commercial business looking to use any of these components in your products,
we can provide full-time support, if that's what you want. We'll custom-taylor components,
systems, and API's to suit your needs. If you are an investor looking to build up a venture,
well yes, that could happen too. Talk to us. Contact [Linas Vepstas](linasvepstas@gmail.com).

"""
    
    return content

def update_todo_es(categorized_repos: Dict[str, List[Dict[str, Any]]]) -> str:
    """Update TODO-ES.md with ElizaOS integration information"""
    
    # Read current TODO-ES.md content
    todo_es_path = 'TODO-ES.md'
    if os.path.exists(todo_es_path):
        with open(todo_es_path, 'r') as f:
            current_content = f.read()
    else:
        current_content = "# Eliza\n\nA framework for multi-agent development and deployment\n\n"
    
    # Find insertion point for integration section
    integration_section = """

## 🧠 OpenCog Integration

### Cognitive Architecture Components
ElizaOS integrates with OpenCog to provide advanced reasoning capabilities:

#### Repository Ecosystem
"""
    
    for category, repos in categorized_repos.items():
        if repos:
            integration_section += f"\n**{category.title()} ({len(repos)} repositories)**\n"
            for repo in repos[:5]:  # Show top 5 per category
                desc = repo['description'] or 'No description available'
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                integration_section += f"- [{repo['name']}]({repo['html_url']}) - {desc}\n"
            if len(repos) > 5:
                integration_section += f"- ... and {len(repos) - 5} more repositories\n"
    
    integration_section += """

### Integration Patterns

#### Agent-Cognitive Bridges
- **AtomSpace Agents**: ElizaOS agents backed by OpenCog AtomSpace knowledge
- **Reasoning Actions**: ElizaOS actions that invoke PLN reasoning
- **Pattern Matching**: AtomSpace pattern matching as ElizaOS evaluators
- **Distributed Cognition**: Multi-agent cognitive processing coordination

#### Implementation Architecture
```
ElizaOS Framework
├── Core Engine
│   ├── Agent Management
│   ├── Action Processing  
│   └── Memory Systems
├── OpenCog Integration Layer
│   ├── AtomSpace Connector
│   ├── CogServer Bridge
│   ├── PLN Reasoning Interface
│   └── Scheme Interpreter
└── Hybrid Applications
    ├── Cognitive Chatbots
    ├── Reasoning Agents
    └── Knowledge Management
```

### Development Roadmap
- [ ] Implement AtomSpace storage provider for ElizaOS
- [ ] Create OpenCog reasoning action templates
- [ ] Build CogServer communication plugin
- [ ] Design cognitive agent architecture patterns
- [ ] Implement distributed reasoning coordination
- [ ] Create OpenCog-aware ElizaOS dashboard components

## 💰 GnuCash Financial Integration

### Intelligent Financial Management
Combining ElizaOS agents with GnuCash for smart financial management:

#### Financial Agent Ecosystem
- **Transaction Categorizer**: AI agent for automatic transaction classification
- **Expense Analyzer**: Pattern recognition for spending behavior analysis
- **Budget Optimizer**: Intelligent budget planning and optimization
- **Investment Tracker**: Multi-asset portfolio monitoring and analysis
- **Financial Assistant**: Conversational interface for financial queries
- **Alert Manager**: Smart notification system for financial events

#### Fractal Integration Architecture
```
ElizaOS Agents (User Interface)
├── Financial Conversation Agents
├── Analysis and Reporting Agents
└── Automation and Alert Agents
    ↓
OpenCog Reasoning (Cognitive Layer)  
├── Financial Pattern Recognition
├── Predictive Analysis
└── Decision Support
    ↓
GnuCash Data (Storage Layer)
├── Account Structures
├── Transaction Records
└── Financial Reports
```

### Implementation Features
- **Natural Language Queries**: Ask questions about finances in plain English
- **Predictive Analytics**: AI-powered forecasting and trend analysis
- **Automated Categorization**: Smart transaction classification
- **Behavioral Insights**: Understanding spending patterns and habits
- **Goal Tracking**: Intelligent progress monitoring for financial goals
- **Risk Assessment**: Cognitive evaluation of financial decisions

"""
    
    # Insert integration section, replacing existing if it exists
    if "## 🧠 OpenCog Integration" in current_content:
        # Replace existing OpenCog integration section to prevent duplication
        start_marker = "## 🧠 OpenCog Integration"
        start_idx = current_content.find(start_marker)
        
        # Find the end of this section (next ## header or end of file)
        remaining = current_content[start_idx + len(start_marker):]
        next_section_match = re.search(r'\n## ', remaining)
        
        if next_section_match:
            end_idx = start_idx + len(start_marker) + next_section_match.start()
            updated_content = current_content[:start_idx] + integration_section + current_content[end_idx:]
        else:
            updated_content = current_content[:start_idx] + integration_section
    elif "## 📂 Repository Structure" in current_content:
        parts = current_content.split("## 📂 Repository Structure", 1)
        updated_content = parts[0] + integration_section + "\n## 📂 Repository Structure" + parts[1]
    else:
        updated_content = current_content + integration_section
    
    return updated_content

def create_integration_overview():
    """Create a comprehensive integration overview document"""
    
    content = f"""# ElizaOS-OpenCog-GnuCash Integration Framework

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*

## Overview

This document describes the hybrid integration framework that combines:
- **ElizaOS**: Multi-agent development and deployment framework
- **OpenCog**: Cognitive architecture and reasoning system  
- **GnuCash**: Financial management and accounting software

## Architecture

### Three-Layer Hybrid System

```
┌─────────────────────────────────────────────────┐
│                ElizaOS Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Agents    │ │   Actions   │ │   Clients   ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────┬───────────────────────────┘
                      │ API/Plugin Interface
┌─────────────────────▼───────────────────────────┐
│              OpenCog Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ AtomSpace   │ │     PLN     │ │ CogServer   ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────┬───────────────────────────┘
                      │ Data/Knowledge Interface  
┌─────────────────────▼───────────────────────────┐
│               GnuCash Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │  Accounts   │ │Transactions │ │   Reports   ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
```

### Integration Patterns

#### 1. Data Flow Integration
- **Bottom-Up**: GnuCash data → AtomSpace representation → ElizaOS agent access
- **Top-Down**: ElizaOS commands → OpenCog reasoning → GnuCash operations

#### 2. Cognitive Enhancement
- **Pattern Recognition**: OpenCog analyzes financial patterns from GnuCash data
- **Predictive Reasoning**: PLN provides forecasting capabilities
- **Intelligent Automation**: ElizaOS agents execute smart financial operations

#### 3. User Interaction
- **Natural Language Interface**: Chat with financial data through ElizaOS
- **Multi-Modal Access**: Web, mobile, CLI, and API interfaces
- **Collaborative Agents**: Multiple specialized financial agents working together

## Implementation Components

### Core Bridges

#### ElizaOS-OpenCog Bridge
```python
class AtomSpaceProvider:
    \"\"\"ElizaOS provider for OpenCog AtomSpace operations\"\"\"
    
class CogServerAction:
    \"\"\"ElizaOS action for CogServer communication\"\"\"
    
class PLNReasoner:
    \"\"\"ElizaOS reasoning service using PLN\"\"\"
```

#### OpenCog-GnuCash Bridge  
```scheme
; Scheme functions for financial data representation
(define (transaction->atom tx)
  ; Convert GnuCash transaction to AtomSpace representation
  )

(define (account->concept acc)
  ; Map GnuCash account to conceptual node
  )
```

#### ElizaOS-GnuCash Bridge
```typescript
interface FinancialAgent {{
  processTransaction(transaction: Transaction): Promise<void>;
  analyzeSpending(timeframe: TimeRange): Promise<Analysis>;
  generateReport(type: ReportType): Promise<Report>;
}}
```

### Specialized Agents

#### Financial Conversation Agent
- Natural language queries about financial data
- Contextual financial advice and insights
- Interactive budget planning and goal setting

#### Transaction Analysis Agent  
- Automatic categorization of transactions
- Anomaly detection and fraud alerts
- Spending pattern recognition and reporting

#### Investment Advisory Agent
- Portfolio analysis and optimization
- Market trend analysis and recommendations
- Risk assessment and mitigation strategies

#### Budget Planning Agent
- Intelligent budget creation and management
- Goal tracking and progress monitoring
- Predictive cash flow analysis

## Fractal Structure Principles

### Self-Similarity Across Scales
- **Micro**: Individual transactions as atomic financial events
- **Meso**: Account structures as financial categories and relationships
- **Macro**: Entire financial portfolios as complex adaptive systems

### Recursive Cognitive Processing
- **Level 1**: Basic transaction processing and categorization
- **Level 2**: Pattern recognition and trend analysis  
- **Level 3**: Strategic financial planning and optimization
- **Level 4**: Meta-cognitive analysis of financial behavior

### Emergent Intelligence
- **Individual Agent Intelligence**: Each agent specializes in specific financial domains
- **Collective Intelligence**: Agents collaborate to provide comprehensive financial insights
- **System Intelligence**: The entire framework learns and adapts to user behavior

## Development Phases

### Phase 1: Foundation (Current)
- [x] Repository structure and documentation
- [x] Basic GitHub Actions for integration
- [ ] Core bridge implementations
- [ ] Basic AtomSpace-GnuCash data mapping

### Phase 2: Core Integration
- [ ] ElizaOS-OpenCog communication layer
- [ ] GnuCash data ingestion into AtomSpace
- [ ] Basic financial reasoning with PLN
- [ ] Simple conversation agents for financial queries

### Phase 3: Advanced Features
- [ ] Predictive financial modeling
- [ ] Advanced pattern recognition
- [ ] Multi-agent financial coordination
- [ ] Comprehensive dashboard and reporting

### Phase 4: Optimization and Scaling
- [ ] Performance optimization
- [ ] Distributed processing capabilities
- [ ] Advanced security and privacy features
- [ ] Commercial deployment readiness

## Getting Started

### Prerequisites
- ElizaOS framework installed
- OpenCog AtomSpace environment
- GnuCash with accessible data files
- Python 3.8+ and Node.js 16+

### Quick Start
```bash
# Clone the integration repository
git clone https://github.com/drzo/elizoscog

# Install dependencies
cd elizoscog
pip install -r requirements.txt
npm install

# Run repository discovery
python scripts/discover_repos.py opencog
python scripts/discover_repos.py elizaOS

# Generate integration documentation
python scripts/generate_checklists.py
python scripts/update_docs.py

# Start the integrated system
npm run start:integrated
```

## Contributing

We welcome contributions to this integration framework! Please see:
- [OpenCog Feature Checklist](docs/integration/opencog_features.md)
- [ElizaOS Feature Checklist](docs/integration/elizaos_features.md)
- [Integration Roadmap](docs/integration/roadmap.md)

## License

This integration framework respects the licenses of all component projects:
- ElizaOS: MIT License
- OpenCog: AGPL and Apache 2.0 (varies by component)
- GnuCash: GPL v2+

"""
    
    return content

def main():
    """Update all documentation files with integration information"""
    
    data_dir = 'data/repositories'
    
    # Create docs directory structure
    os.makedirs('docs/integration', exist_ok=True)
    
    # Update TODO-OC.md if OpenCog data exists
    opencog_file = os.path.join(data_dir, 'opencog_repos.json')
    if os.path.exists(opencog_file):
        with open(opencog_file, 'r') as f:
            opencog_data = json.load(f)
        
        updated_oc = update_todo_oc(opencog_data['categories'])
        with open('TODO-OC.md', 'w') as f:
            f.write(updated_oc)
        print("Updated TODO-OC.md")
    
    # Update TODO-ES.md if ElizaOS data exists  
    elizaos_file = os.path.join(data_dir, 'elizaos_repos.json')
    if os.path.exists(elizaos_file):
        with open(elizaos_file, 'r') as f:
            elizaos_data = json.load(f)
        
        updated_es = update_todo_es(elizaos_data['categories'])
        with open('TODO-ES.md', 'w') as f:
            f.write(updated_es)
        print("Updated TODO-ES.md")
    
    # Create comprehensive integration overview
    integration_overview = create_integration_overview()
    with open('docs/integration/README.md', 'w') as f:
        f.write(integration_overview)
    print("Created integration overview: docs/integration/README.md")

if __name__ == '__main__':
    main()