import sys
import os
import streamlit as st

# Add the parent directory to sys.path to import our src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_traverser import traverse_graph
from src.llm_agent import generate_sql

st.set_page_config(page_title="DataGraph OKF Copilot", layout="wide")

st.title("📊 DataGraph: OKF-Native SQL Copilot")
st.caption("No Vector DBs. No Embeddings. Just pure, structured knowledge traversal. Powered by Gemini Flash ⚡")

# Sidebar for Agent Trace
with st.sidebar:
    st.header("🕵️ Agent Trace")
    st.info("Ask a question to see the agent's thought process here.")
    
    if "trace" in st.session_state:
        st.subheader("Files Visited:")
        for i, file in enumerate(st.session_state.trace, 1):
            clean_path = file.replace("knowledge_base/", "")
            st.code(f"{i}. {clean_path}", language="markdown")
    else:
        st.write("No query run yet.")

# Main UI
user_query = st.text_area(
    "What data do you need?",
    placeholder="e.g., Write a SQL query to calculate MRR, but make sure to exclude free trials.",
    height=100
)

if st.button("Generate SQL 🚀"):
    if not user_query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Traversing OKF Knowledge Graph..."):
            start_file = "knowledge_base/metrics/mrr.md"
            context, trace = traverse_graph(start_file, max_depth=3)
            st.session_state.trace = trace
            
        with st.spinner("Generating SQL via Gemini Flash..."):
            try:
                sql_query = generate_sql(user_query, context)
                
                st.subheader("Generated SQL:")
                st.code(sql_query, language="sql")
                
                st.subheader("Agent Context Used:")
                with st.expander("View raw OKF context sent to LLM"):
                    st.markdown(context)
                    
            except Exception as e:
                st.error(f"Error generating SQL: {e}")
                st.write("Make sure your `.env` file has a valid `GEMINI_API_KEY`.")