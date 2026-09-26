# 📊 DataGraph: OKF-Native Enterprise AI Copilot

> **Stop relying on fragile vector search for structured enterprise knowledge.** 

DataGraph is a proof-of-concept AI agent that uses Google's **Open Knowledge Format (OKF)** to traverse structured, linked Markdown documents and generate production-ready, business-rule-compliant SQL queries. 

Instead of using traditional Retrieval-Augmented Generation (RAG) with vector databases and embeddings, DataGraph treats knowledge as a traversable graph. The agent explicitly follows Markdown links to gather context, eliminating hallucinations and ensuring strict adherence to complex business logic.

---

## 🚨 The Problem with Traditional RAG
When building enterprise AI agents (e.g., for Data Analytics, DevOps, or Customer Support), traditional RAG often fails because:
1. **Context Fragmentation:** Vector search retrieves isolated text chunks, losing the relationships between concepts (e.g., a metric definition and its underlying table schema).
2. **Lost Metadata:** Embeddings flatten critical metadata like data freshness SLAs, partition keys, and business rules.
3. **Hallucinations:** Without explicit constraints, LLMs guess column names or ignore edge cases (like excluding free trials from revenue calculations).

## 💡 The OKF Solution
This project implements the **Open Knowledge Format (OKF)**, an open, vendor-neutral specification for packaging knowledge. 
- Knowledge is stored as a directory of Markdown files with YAML frontmatter.
- Concepts are explicitly linked using standard Markdown links.
- The AI agent **traverses** this graph deliberately, reading exactly what it needs, when it needs it.

**Result:** Flawless, cost-optimized SQL queries that respect real-world enterprise constraints, with zero vector databases or embedding models required.

---

## 🏗️ Architecture & Workflow

1. **User Query:** *"Calculate this month's MRR, excluding free trials and handling the August 2026 data bug."*
2. **Entry Point:** Agent starts at `knowledge_base/metrics/mrr.md`.
3. **Graph Traversal:** Agent reads the file, extracts YAML metadata, and identifies Markdown links.
4. **Context Gathering:** Agent recursively follows links to `tables/subscriptions.md` and `runbooks/billing_logic.md` up to a defined depth.
5. **LLM Generation:** The aggregated, structured context is sent to **Google Gemini 3.8 Flash** to generate the final SQL query.

---

## ✨ Key Features

- 🚫 **No Vector Databases:** Zero dependency on Pinecone, Chroma, or embedding models.
- 🔗 **Explicit Knowledge Graphs:** Uses native Markdown links to preserve relationships between metrics, schemas, and runbooks.
- 📝 **Rich Metadata:** YAML frontmatter stores ownership, data freshness, partitioning keys, and PII levels.
- 🕵️ **Transparent Agent Trace:** The UI shows exactly which files the agent visited to build its context, ensuring full explainability.
- ⚡ **Powered by Gemini 3.8 Flash:** Utilizes Google's most intelligent Flash model, optimized for autonomous agent workflows and complex reasoning, entirely on the free tier.

---

## 📂 Project Structure

```text
datagraph-okf-copilot/
├── knowledge_base/       # The OKF Bundle (Metrics, Tables, Runbooks)
├── src/                  # Agent Engine (Parser, Graph Traverser, LLM Client)
├── app/                  # Streamlit UI for interactive demos
├── scripts/              # Tooling (OKF Bundle Validator)
├── requirements.txt      # Python dependencies
├── .env.example          # Template for API keys
└── README.md             # You are here!