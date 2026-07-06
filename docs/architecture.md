# Architecture

## Goal

Build a Website Knowledge Extraction Engine (WKEE) that converts websites into semantic knowledge usable by an LLM-powered browser agent.

---

## High-Level Architecture

Website

↓

Browser Controller

↓

DOM Extractor

↓

Semantic Component Extractor

↓

Navigation Graph Builder

↓

Workflow Generator

↓

Knowledge Storage

↓

Embedding Engine

↓

LLM Browser Agent

---

## Major Modules

browser/

Responsible for Playwright.

---

explorer/

Exploration strategy.

---

extractor/

DOM parsing.

---

workflow/

Workflow generation.

---

forms/

Form understanding.

---

vision/

Fallback visual reasoning.

---

graph/

Navigation graph.

---

storage/

SQLite + JSON.

---

embeddings/

Semantic search.

---

scheduler/

Incremental crawling.

---

agent/

Future LangGraph execution agent.

---

## Data Flow

Website

↓

Crawler

↓

Knowledge Graph

↓

Embeddings

↓

SQLite

↓

LLM Retrieval

↓

Playwright Agent
