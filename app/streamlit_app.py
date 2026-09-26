import sys
import os
import streamlit as st
import re

# Add the parent directory to sys.path to import our src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_traverser import traverse_graph
from src.llm_agent import generate_analysis

st.set_page_config(page_title="DataGraph OKF Copilot", layout="wide", page_icon="📊")

# Header Section
st.title("DataGraph: OKF-Native Enterprise Copilot")
st.caption("No Vector DBs. No Embeddings. Pure, structured knowledge traversal powered by Gemini 3.8 Flash.")
st.divider()

def get_start_file(query: str) -> str:
    """Simple keyword router to pick the best starting OKF file."""
    query_lower = query.lower()
    if any(word in query_lower for word in ["cac", "acquisition", "marketing", "spend"]):
        return "knowledge_base/metrics/cac.md"
    elif any(word in query_lower for word in ["mrr", "revenue", "recurring", "subscription"]):
        return "knowledge_base/metrics/mrr.md"
    else:
        return "knowledge_base/index.md"

# Sidebar for Agent Trace
with st.sidebar:
    st.header("Agent Trace")
    st.caption("Knowledge graph navigation path")
    
    if "trace" in st.session_state:
        st.markdown("**Files Visited:**")
        for i, file in enumerate(st.session_state.trace, 1):
            clean_path = file.replace("knowledge_base/", "")
            st.markdown(f"{i}. `{clean_path}`")
    else:
        st.info("Run a query to see the agent's navigation path.")

# Main UI
st.markdown("### Ask a Data Question")
user_query = st.text_area(
    label="Query",
    placeholder="e.g., Write a SQL query to calculate CAC, and tell me about any data latency issues.",
    height=100,
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 5])
with col1:
    submit_button = st.button("Generate Answer", type="primary", use_container_width=True)

if submit_button:
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Agent is selecting the right knowledge entry point..."):
            start_file = get_start_file(user_query)
            
        with st.spinner(f"Traversing OKF Graph starting from: `{start_file.replace('knowledge_base/', '')}`..."):
            context, trace = traverse_graph(start_file, max_depth=3)
            st.session_state.trace = trace
            
        with st.spinner("Generating structured response via Gemini 3.8 Flash..."):
            try:
                # Get the raw JSON dictionary from the LLM
                result = generate_analysis(user_query, context)
                
                st.divider()
                
                # Handle Error State (Missing Context)
                if result.get("error"):
                    st.warning(f"Insufficient Context: {result['error']}")
                
                # Handle Success State (Render via Streamlit Native Components)
                else:
                    # 1. Business Logic
                    st.subheader("Business Logic")
                    st.write(result.get("logic", "No logic provided."))
                    
                    # 2. SQL Query (Using Streamlit's native syntax highlighter)
                    st.subheader("SQL Query")
                    
                    # Failsafe: Just in case the LLM still sneaks in ```sql tags
                    raw_sql = result.get("sql", "")
                    clean_sql = re.sub(r"^```sql\s*|```$", "", raw_sql, flags=re.MULTILINE).strip()
                    
                    st.code(clean_sql, language="sql")
                    
                    # 3. Pro-Tip (Using Streamlit's native info box)
                    if result.get("tip"):
                        st.info(result["tip"])
                
                st.divider()
                
                # Raw Context Expander
                with st.expander("View Raw OKF Context Sent to LLM"):
                    st.markdown("```markdown\n" + context + "\n```")
                    
            except Exception as e:
                st.error(f"Error generating response: {e}")
                st.write("Ensure your `.env` file has a valid `GEMINI_API_KEY` and the LLM returned valid JSON.")