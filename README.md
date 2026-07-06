# Website Knowledge Extraction Engine (WKEE)

> A production-grade Website Knowledge Extraction Engine that converts web applications into a structured semantic knowledge base for LLM-powered browser automation.

---

# Overview

The Website Knowledge Extraction Engine (WKEE) is designed to bridge the gap between traditional web crawling and intelligent browser automation.

Unlike conventional crawlers that only discover pages and URLs, WKEE discovers **user workflows**, **UI components**, **forms**, **navigation graphs**, and **semantic relationships** within a website.

The generated knowledge base enables an LLM-powered browser agent to complete user tasks by retrieving previously discovered workflows instead of rediscovering the website on every request.

---

# Project Goals

The primary objectives of WKEE are:

* Crawl complex web applications.
* Support JavaScript-heavy websites.
* Understand user workflows.
* Extract semantic UI components.
* Build a navigation graph.
* Understand forms and validations.
* Detect duplicate page templates.
* Generate embeddings for semantic retrieval.
* Store crawl data for reuse.
* Support incremental weekly recrawls.
* Provide structured knowledge for an LLM-powered Playwright agent.

---

# Project Architecture

```text
                        Website

                            │

                    Browser Controller

                            │

                     DOM Extraction

                            │

                Semantic Component Extraction

                            │

                 Navigation Graph Builder

                            │

                  Workflow Identification

                            │

                  Knowledge Storage Layer

              JSON + SQLite + Embeddings

                            │

                  Retrieval & Search Layer

                            │

               LangGraph + Playwright Agent
```

---

# Project Structure

```text
website-knowledge-engine/

├── docs/
│   ├── implementation_plan.txt
│   ├── architecture.md
│   ├── roadmap.md
│   ├── coding_standards.md
│   ├── decisions.md
│   ├── testing_strategy.md
│   ├── data_schema.md
│   └── prompts/
│       ├──agent_prompt.md
│       └──crawler_prompt.md    
│
├── crawler/
│
├── agent/
│
├── shared/
│
├── config/
│
├── tests/
│
├── examples/
│
├── crawl_data/
│
├── logs/
│
├── scripts/
│
├── README.md
├── requirements.txt
├── pyproject.toml
└── .env
```

---

# Core Components

## Browser Controller

Responsible for:

* Launching Playwright
* Session management
* Authentication
* Cookies
* Downloads
* Uploads
* Multiple tabs
* Browser lifecycle

---

## Explorer

Responsible for:

* Website exploration
* Navigation strategy
* Loop detection
* Safe interaction
* State tracking

---

## Extractor

Responsible for:

* DOM parsing
* Accessibility extraction
* Semantic UI extraction
* Tables
* Forms
* Menus
* Components

---

## Workflow Engine

Responsible for:

* Workflow discovery
* State transitions
* Action graph generation
* User flow extraction

---

## Form Analyzer

Responsible for:

* Input discovery
* Validation detection
* Required fields
* Dynamic dependencies
* Submission actions

---

## Graph Builder

Responsible for:

* Navigation graph
* State graph
* Workflow graph
* Duplicate detection

---

## Embedding Engine

Responsible for:

* Semantic search
* Similar workflow retrieval
* Vector generation

---

## Storage Layer

Responsible for:

* SQLite database
* JSON exports
* Screenshots
* Crawl history
* Incremental updates

---

## Vision Engine

Fallback mechanism used only when DOM analysis cannot continue.

Responsibilities:

* Screenshot analysis
* UI understanding
* Recovery suggestions

---

## LLM Browser Agent

Uses the generated knowledge base to:

* Retrieve workflows
* Execute browser actions
* Verify state transitions
* Recover from UI changes

---

# Crawl Output

After each successful crawl, the engine generates:

```text
crawl_data/

├── graph.json
├── pages.json
├── workflows.json
├── forms.json
├── components.json
├── embeddings/
├── screenshots/
├── sqlite.db
├── crawl.log
└── errors.log
```

---

# Development Roadmap

## Phase 1

Project Initialization

* Repository
* Configuration
* Logging
* Testing framework

---

## Phase 2

Browser Controller

---

## Phase 3

DOM Extraction

---

## Phase 4

Navigation Explorer

---

## Phase 5

Workflow Discovery

---

## Phase 6

Form Understanding

---

## Phase 7

Duplicate Detection

---

## Phase 8

Embeddings

---

## Phase 9

Vision Recovery

---

## Phase 10

Incremental Crawling

---

## Phase 11

LLM Browser Agent

---

# Technology Stack

| Component          | Technology              |
| ------------------ | ----------------------- |
| Language           | Python 3.12             |
| Browser Automation | Playwright              |
| HTML Parsing       | BeautifulSoup + lxml    |
| Graph Processing   | NetworkX                |
| Database           | SQLite                  |
| ORM                | SQLAlchemy              |
| Embeddings         | FAISS + Embedding Model |
| Configuration      | YAML                    |
| Logging            | Loguru                  |
| Async Networking   | httpx                   |
| Image Processing   | Pillow                  |
| Testing            | Pytest                  |
| Agent Framework    | LangGraph               |

---

# Setup

## Clone the repository

```bash
git clone <repository-url>
cd website-knowledge-engine
```

---

## Create a virtual environment

Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

## Configure environment variables

Create a `.env` file.

Example:

```text
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

---

## Configure crawler

Edit:

```text
config/crawler.yaml
```

---

## Run the crawler

```bash
python -m crawler
```

---

# Development Principles

The project follows these engineering principles:

* Clean Architecture
* SOLID Principles
* Modular Design
* Type Safety
* Asynchronous Programming
* Comprehensive Testing
* Structured Logging
* Configuration over Hardcoding
* Incremental Development

---

# Safety Rules

The crawler must never perform irreversible actions automatically.

Examples include:

* Deleting records
* Changing passwords
* Making payments
* Cancelling applications
* Submitting official forms
* Deactivating accounts

Such actions require explicit user approval.

---

# Future Enhancements

Planned improvements include:

* Distributed crawling
* Parallel browser execution
* API discovery
* Network traffic recording
* Visual diff detection
* Self-healing workflows
* Plugin architecture
* Multi-website knowledge base
* Cloud execution support
* Fine-grained permission system

---

# Contributing

Please read the following documentation before contributing:

* `docs/coding_standards.md`
* `docs/architecture.md`
* `docs/roadmap.md`
* `docs/testing_strategy.md`
* `docs/data_schema.md`
* `docs/decisions.md`

All code contributions must:

* Follow the coding standards.
* Include tests.
* Update documentation where necessary.
* Maintain backward compatibility unless explicitly approved.

---

# License

Choose an appropriate license for your intended use (for example, MIT, Apache 2.0, or a proprietary internal license).

---

# Acknowledgements

This project combines ideas from modern browser automation, semantic knowledge extraction, workflow modeling, graph-based navigation, and LLM-driven task execution to create a reusable knowledge layer for intelligent web agents.
