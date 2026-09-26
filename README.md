# DataGraph: OKF-Native Enterprise AI Copilot

A production-ready AI agent that uses the Open Knowledge Format (OKF) to traverse structured, linked Markdown documents and generate business-rule-compliant responses (SQL queries, CLI commands, or security audits).

Instead of relying on traditional Retrieval-Augmented Generation (RAG) with vector databases and embeddings, DataGraph treats knowledge as a traversable graph. The agent explicitly follows Markdown links to gather context, eliminating hallucinations and ensuring strict adherence to complex enterprise logic.

## The Problem with Traditional RAG

When building enterprise AI agents for domains like Data Analytics, DevOps, or Security, traditional RAG often fails due to:

1. Context Fragmentation: Vector search retrieves isolated text chunks, losing the relationships between concepts (e.g., a metric definition and its underlying table schema).
2. Lost Metadata: Embeddings flatten critical metadata such as data freshness SLAs, database partition keys, and specific business rules.
3. Hallucinations: Without explicit constraints, LLMs guess column names or ignore edge cases (like excluding free trials from revenue calculations).

## The OKF Solution

This project implements the Open Knowledge Format (OKF), an open, vendor-neutral specification for packaging knowledge.

* Knowledge is stored as a directory of Markdown files with YAML frontmatter.
* Concepts are explicitly linked using standard Markdown links.
* The AI agent traverses this graph deliberately, reading exactly what it needs, when it needs it.
* Conditional Traversal: If a file contains PII, the agent automatically injects security and compliance policies into the context.
* The LLM outputs strict, token-efficient JSON, allowing the frontend UI to handle all formatting and design natively.

Result: Flawless, cost-optimized responses that respect real-world enterprise constraints, with zero vector databases or embedding models required.

## Architecture and Workflow

1. User Query: The user submits a natural language question (e.g., "Calculate this month's MRR, excluding free trials" or "Our staging server is down").
2. Dynamic Routing: A keyword router selects the most relevant entry-point Markdown file and infers the correct agent persona (Data Analyst, DevOps Engineer, or Security Auditor).
3. Graph Traversal: The agent reads the file, extracts YAML metadata, and identifies Markdown links, traversing up to a defined depth.
4. Context Gathering: The agent aggregates the relevant files into a highly compressed, token-efficient context block.
5. Structured Generation: The context is sent to OpenRouter (using highly capable free-tier models like Llama 3 or Qwen), which is forced to output strict JSON.
6. UI Rendering: The Streamlit frontend parses the JSON and renders it using native, beautifully formatted components (syntax-highlighted code blocks, info boxes, etc.).

## Key Features

* Zero Vector Databases: No dependency on Pinecone, Chroma, or embedding models.
* Explicit Knowledge Graphs: Uses native Markdown links to preserve relationships between metrics, schemas, runbooks, and security policies.
* Multi-Persona Support: Dynamically adapts its output format and reasoning based on whether the query is analytical, operational, or compliance-focused.
* Transparent Agent Trace: The UI sidebar shows exactly which files the agent visited to build its context, ensuring full explainability.
* Token-Efficient & Robust: Utilizes strict JSON output mode, aggressive context compression, and a regex fallback parser to guarantee successful rendering even if the LLM truncates or hallucinates markdown.
* Graceful Rate Limit Handling: Built-in exponential backoff retry logic automatically recovers from temporary 429 API rate limits common in free-tier models.

## Project Structure

```text
datagraph/
├── knowledge_base/     # The OKF Bundle (Metrics, Tables, Runbooks, Security, Product)
├── src/                # Agent Engine (Parser, Graph Traverser, LLM Client, Optimizers)
├── app/                # Streamlit UI for interactive demos
├── scripts/             # Tooling (OKF Bundle Validator)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for API keys
└── README.md           # Project documentation
```

## Getting Started

### Prerequisites

* Python 3.9 or higher
* A free OpenRouter API Key (available at https://openrouter.ai/keys)

### Installation

1. Clone the repository and navigate to the folder:

   ```bash
   cd datagraph
   ```

2. Create and activate a virtual environment:

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API Key:

   Create a `.env` file in the root directory and add your credentials:

   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
   OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free
   ```

   *(Note: `.env` is listed in `.gitignore` and will not be uploaded to GitHub).*

5. Validate the Knowledge Base (Optional but recommended):

   ```bash
   python scripts/validate_okf.py
   ```

6. Run the Streamlit App:

   ```bash
   streamlit run app/streamlit_app.py
   ```

## Example Usage

**Prompt (Data Analyst):**

"Write a SQL query to calculate Net MRR for this month. Make sure it is optimized for BigQuery and handles any known data quality bugs."

**Agent Behavior:**

1. Reads `metrics/mrr.md` to understand the base calculation.
2. Follows the link to `runbooks/billing_logic.md` to learn that free trials (`is_trial = TRUE`) must be excluded.
3. Follows the link to `runbooks/data_quality.md` to discover the "August 2026 Stripe duplication bug".
4. Follows the link to `tables/subscriptions.md` to get the exact column names and partitioning key (`created_at`).
5. Output: A partitioned SQL query with a `DISTINCT` clause and a `WHERE is_trial = FALSE` filter, accompanied by a plain-English explanation of the business rules applied.

**Prompt (DevOps Engineer):**

"Our staging server is down and users are getting 503 errors. What are the exact diagnostic steps?"

**Agent Behavior:**

1. Routes to `runbooks/incident_response.md`.
2. Follows links to `infrastructure/aws_ec2_staging.md`.
3. Output: A clear diagnosis, a syntax-highlighted bash code block with exact AWS CLI commands to run, and an escalation warning.

## Tech Stack

* Language: Python 3.x
* UI Framework: Streamlit
* LLM Provider: OpenRouter API
* API Client: OpenAI Python SDK (used for OpenRouter compatibility)
* Knowledge Format: Markdown + YAML (Open Knowledge Format specification)
* Environment Management: `python-dotenv`

## Future Enhancements

* Semantic Router: Replace the keyword router with a lightweight LLM call to dynamically select the best starting `.md` file based on semantic intent.
* MCP Integration: Connect the agent to a Model Context Protocol (MCP) server to execute the generated SQL or CLI commands directly against live systems.
* Automated CI/CD: Add a GitHub Action to automatically run `validate_okf.py` on every pull request to prevent broken links in the knowledge base.
