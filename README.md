# DataGraph: OKF-Native Enterprise AI Copilot

A proof-of-concept AI agent that uses Google's Open Knowledge Format (OKF) to traverse structured, linked Markdown documents and generate production-ready, business-rule-compliant SQL queries. 

Instead of relying on traditional Retrieval-Augmented Generation (RAG) with vector databases and embeddings, DataGraph treats knowledge as a traversable graph. The agent explicitly follows Markdown links to gather context, eliminating hallucinations and ensuring strict adherence to complex enterprise business logic.

## The Problem with Traditional RAG

When building enterprise AI agents for domains like Data Analytics, DevOps, or Customer Support, traditional RAG often fails due to:

1. Context Fragmentation: Vector search retrieves isolated text chunks, losing the relationships between concepts (e.g., a metric definition and its underlying table schema).
2. Lost Metadata: Embeddings flatten critical metadata such as data freshness SLAs, database partition keys, and specific business rules.
3. Hallucinations: Without explicit constraints, LLMs guess column names or ignore edge cases (like excluding free trials from revenue calculations).

## The OKF Solution

This project implements the Open Knowledge Format (OKF), an open, vendor-neutral specification for packaging knowledge. 

- Knowledge is stored as a directory of Markdown files with YAML frontmatter.
- Concepts are explicitly linked using standard Markdown links.
- The AI agent traverses this graph deliberately, reading exactly what it needs, when it needs it.
- The LLM outputs strict, token-efficient JSON, allowing the frontend UI to handle all formatting and design natively.

Result: Flawless, cost-optimized SQL queries that respect real-world enterprise constraints, with zero vector databases or embedding models required.

## Architecture and Workflow

1. User Query: The user submits a natural language question (e.g., "Calculate this month's MRR, excluding free trials").
2. Dynamic Routing: A lightweight keyword router selects the most relevant entry-point Markdown file.
3. Graph Traversal: The agent reads the file, extracts YAML metadata, and identifies Markdown links.
4. Context Gathering: The agent recursively follows links to related tables and runbooks up to a defined depth.
5. Structured Generation: The aggregated context is sent to Google Gemini 3.8 Flash, which is forced to output strict JSON (Logic, SQL, Pro-Tip).
6. UI Rendering: The Streamlit frontend parses the JSON and renders it using native, beautifully formatted components.

## Key Features

- Zero Vector Databases: No dependency on Pinecone, Chroma, or embedding models.
- Explicit Knowledge Graphs: Uses native Markdown links to preserve relationships between metrics, schemas, and runbooks.
- Rich Metadata: YAML frontmatter stores ownership, data freshness, partitioning keys, and PII levels.
- Transparent Agent Trace: The UI sidebar shows exactly which files the agent visited to build its context, ensuring full explainability.
- Token-Efficient Generation: Utilizes strict JSON output mode, reducing token usage by 20-40% and eliminating conversational filler.
- Powered by Gemini 3.8 Flash: Utilizes Google's intelligent Flash model, optimized for autonomous agent workflows and complex reasoning.

## Project Structure

datagraph-okf-copilot/
├── knowledge_base/       # The OKF Bundle (Metrics, Tables, Runbooks)
├── src/                  # Agent Engine (Parser, Graph Traverser, LLM Client)
├── app/                  # Streamlit UI for interactive demos
├── scripts/              # Tooling (OKF Bundle Validator)
├── requirements.txt      # Python dependencies
├── .env.example          # Template for API keys
└── README.md             # Project documentation

## Getting Started

### Prerequisites
- Python 3.9 or higher
- A free Google Gemini API Key (available at https://aistudio.google.com/apikey)

### Installation

1. Clone the repository and navigate to the folder:
   cd datagraph-okf-copilot

2. Create and activate a virtual environment:
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set up your API Key:
   Create a .env file in the root directory and add your key:
   GEMINI_API_KEY=your_actual_api_key_here
   
   (Note: .env is listed in .gitignore and will not be uploaded to GitHub).

5. Validate the Knowledge Base (Optional but recommended):
   python scripts/validate_okf.py

6. Run the Streamlit App:
   streamlit run app/streamlit_app.py

## Example Usage

Prompt: 
"Write a SQL query to calculate Net MRR for this month. Make sure it is optimized for BigQuery and handles any known data quality bugs."

Agent Behavior:
1. Reads metrics/mrr.md to understand the base calculation.
2. Follows the link to runbooks/billing_logic.md to learn that free trials (is_trial = TRUE) must be excluded and amounts are already normalized to USD.
3. Follows the link to runbooks/data_quality.md to discover the "August 2026 Stripe duplication bug".
4. Follows the link to tables/subscriptions.md to get the exact column names and partitioning key (created_at).
5. Output: A flawless, partitioned SQL query with a DISTINCT clause and a WHERE is_trial = FALSE filter, accompanied by a plain-English explanation of the business rules applied.

## Tech Stack

- Language: Python 3.x
- UI Framework: Streamlit
- LLM Provider: Google Gemini API (gemini-3.8-flash)
- Knowledge Format: Markdown + YAML (Open Knowledge Format v0.2 specification)
- Environment Management: python-dotenv

## Future Enhancements

- Dynamic Entry Point: Replace the keyword router with a lightweight LLM call to dynamically select the best starting .md file based on semantic intent.
- MCP Integration: Connect the agent to a Model Context Protocol (MCP) server to execute the generated SQL directly against a live database.
- Automated CI/CD: Add a GitHub Action to automatically run validate_okf.py on every pull request to prevent broken links in the knowledge base.
