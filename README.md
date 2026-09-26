# DataGraph: OKF-Native SQL Copilot

An AI agent that uses Google's Open Knowledge Format (OKF) to traverse structured Markdown knowledge graphs, replacing traditional RAG for enterprise SQL generation.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: 
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your OpenAI API key.
5. Run the UI: `streamlit run app/streamlit_app.py`
