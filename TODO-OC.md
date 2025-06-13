## The OpenCog Project 👋
[OpenCog aims to create AGI](https://wiki.opencog.org/w/The_Open_Cognition_Project)
with a combination of exploration, engineering and basic science research.
Side quests have included robotics systems ([Hanson Robotics](https://www.hansonrobotics.com)),
financial systems (Aidiya),
genomics (MOZI and [Rejuve.bio](https://www.rejuve.bio)),
machine learning ([predicting risk from clinician notes](https://doi.org/10.1371/journal.pone.0085733)),
natural language chatbots ([virtual dog playing fetch](https://www.youtube.com/watch?v=FEmpGRLwbqE)) and more.
This project was pioneered by [Dr. Ben Goertzel](https://en.wikipedia.org/wiki/Ben_Goertzel).

🔄 **Automated Repository Discovery**: This document is automatically updated with repository information from https://github.com/orgs/opencog/repositories using GitHub Actions.

Git repos fall into four categories:

### OpenCog AtomSpace
The core of the system. As of 2025, it is active, stable and supported.

* [AtomSpace](https://github.com/opencog/atomspace) - Hypergraph database and query engine.
* [Storage](https://github.com/opencog/atomspace-storage) - Base class for saving, loading, sending and receiving Atoms and AtomSpaces
* [CogServer](https://github.com/opencog/cogserver) and [atomspace-cog](https://github.com/opencog/atomspace-cog) - Networking, json, websockets.
* [atomspace-rocks](https://github.com/opencog/atomspace-rocks) - Disk I/O storage, based on RocksDB.
* [Proxy Nodes](https://wiki.opencog.org/w/ProxyNode) - Managing Atoms flowing through large Atomspaces. 
* [Sparse Vectors/Matrix](https://github.com/opencog/matrix) - Working with graphs as (embeddings in) sparse vectors.
* [Link Grammar](https://github.com/opencog/link-grammar) - Maximal Planar Graph (MPG) parsing, natural lanuage parsing (NLP).
* [Docker containers](https://github.com/opencog/docker) - System integration and demos.
* [atomspace-pgres](https://github.com/opencog/atomspace-pgres) - Postgres StorageNode. Works, but old, deprecated.

### OpenCog Research
Git repos in which active resarch is being carried out:
* [Learn](https://github.com/opencog/learn) - Symbolic learning ("mature", batch-based processing.)
* [Agents](https://github.com/opencog/agents) - Refactoring learning for an interactive environment.
* [Sensory](https://github.com/opencog/sensory) - Dataflow of graphlets to/from external world. Agents I/O system.
* [Motor](https://github.com/opencog/motor) - Controlling the focus of sensory attention. Perception-action.
* [Atomese-SIMD](https://github.com/opencog/atomese-simd) - Flowing data to GPU's and other SIMD (OpenCL/CUDA) hardware w/the sensory API.

### OpenCog Fossils
Older, abandoned and obsolete components and experiments. These were attempts to build subsystems 
with specific goals and ideas in mind. As experiments, they provided validation for certain design
ideas. They were educational and fun, but turned out to be unworkable. Thus, development has
halted. These projects are no longer maintained. They do contain useful subsystems that could be
salvaged for future use. This includes:
* PLN, URE, Attention, Ghost, Relex, R2L, ROS, Hanson Robotics Eva/Sophia
* MOSES (but not as-moses, see below).
* Any repo that is marked "read-only" or "obsolete".

### OpenCog Hyperon
Being developed by [Singularity.net](https://singularitynet.io).

### OpenCog Incubator
These are the immature, incomplete, promising projects that haven't taken off yet.

* [SQL Bridge](https://github.com/opencog/atomspace-bridge) - Direct I/O between SQL and AtomSpace
* [AtomSpace TypeScript](https://github.com/opencog/atomspace-typescript) - TypeScript API and Browser viewer - proof of concept.
* [Prolog-on-Atomspace](https://github.com/opencog/atomspace/tree/master/opencog/persist/prolog) - proof-of-concept
* [Chemistry](https://github.com/opencog/cheminformatics) - Molecular bonds, molecular structural formulas (proof-of-concpept.)
* [agi-bio](https://github.com/opencog/agi-bio) - Genomics, proteomics system used by MOZI and rejuve.bio
* [visualization](https://github.com/opencog/visualization) - GUI for exploring AtomSpace contents.
* [as-moses](https://github.com/opencog/as-moses) - Port of MOSES to the AtomSpace.
* [Vision](https://github.com/opencog/vision) - Extracting structure from images, video (proof-of-concept.)
* [Hyperon-on-top-of-atomspace](https://github.com/opencog/atomspace-metta) - Hyperon backwards-compat layer (proof-of-concept.)
* [SpaceTime](https://github.com/opencog/spacetime) - Octree spatial bounding boxes and time intervals in Atomese.

# HELP WANTED

## 🔗 Integration Framework

This repository now includes a hybrid integration framework combining:
- **OpenCog**: Cognitive architecture and reasoning system
- **ElizaOS**: Multi-agent development and deployment framework  
- **GnuCash**: Financial management and accounting software

### 🤖 Automated Repository Discovery
Daily GitHub Actions discover and catalog repositories from:
- [OpenCog Organization](https://github.com/orgs/opencog/repositories)
- [ElizaOS Organization](https://github.com/orgs/elizaOS/repositories)

Feature checklists and integration plans are automatically generated. See [Integration Documentation](docs/integration/README.md).

## 🚀 Integration Development Priorities

### Core Infrastructure
- AtomSpace performance optimization and ElizaOS integration
- Distributed processing enhancements for multi-agent coordination
- Cross-language binding improvements (Python, JavaScript, Scheme)
- Integration testing frameworks for hybrid architectures

### Cognitive-Financial Integration
- **Fractal Architecture**: GnuCash data → OpenCog reasoning → ElizaOS agents
- **Pattern Recognition**: Financial behavior analysis using AtomSpace
- **Predictive Reasoning**: PLN-based financial forecasting
- **Intelligent Automation**: Multi-agent financial management

### Bridge Implementations
- **ElizaOS-OpenCog Bridge**: AtomSpace providers, CogServer actions, PLN reasoning
- **OpenCog-GnuCash Bridge**: Financial data representation, cognitive analysis
- **ElizaOS-GnuCash Bridge**: Financial agents, conversation interfaces, automation

### Research Areas
- Hyperon-AtomSpace compatibility layers
- Advanced reasoning algorithms for financial domains
- Multi-modal learning systems combining financial and conversational data
- Real-time cognitive architectures for financial decision-making

## 💡 Implementation Components

### Intelligent Financial Agents
- **Transaction Categorizer**: AI-powered automatic transaction classification
- **Expense Analyzer**: Pattern recognition for spending behavior analysis
- **Budget Optimizer**: Cognitive budget planning and optimization
- **Investment Advisor**: Multi-agent portfolio analysis and recommendations
- **Financial Assistant**: Natural language interface for financial queries
- **Alert Manager**: Smart notification system using cognitive reasoning

### Cognitive Architecture
```
ElizaOS Agents (User Interface)
├── Conversational Financial Agents
├── Analysis and Reporting Agents
└── Automation and Alert Agents
    ↓ Plugin Interface
OpenCog Reasoning (Cognitive Layer)  
├── AtomSpace Knowledge Representation
├── PLN Financial Pattern Recognition
└── CogServer Distributed Processing
    ↓ Data Interface
GnuCash Storage (Data Layer)
├── Account Structures and Hierarchies
├── Transaction Records and History
└── Financial Reports and Analytics
```
The above-mentioned commercial projects don't pay the bills. There are far more ideas
and possibilities than there is time or money. If you're a software developer, bored
and looking for something to do, there's a lot of great stuff here that is worthy of
attention. If you are an academic, scientist or grad student, someone who wants to do
cross-over Symbolic AI and Deep-Learning Neural Net research, and need a base toolset,
this is the place. We will work with you to make sure this stuff fits your needs and
does what you want it to do, the way you want it.
Contact [Linas Vepstas](linasvepstas@gmail.com).

### Commercial support
If you are a commercial business looking to use any of these components in your products,
we can provide full-time support, if that's what you want. We'll custom-taylor components,
systems, and API's to suit your needs. If you are an investor looking to build up a venture,
well yes, that could happen too. Talk to us. Contact [Linas Vepstas](linasvepstas@gmail.com).
