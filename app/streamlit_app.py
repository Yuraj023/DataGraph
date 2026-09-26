import sys
import os
import streamlit as st

# Add the parent directory to sys.path to import our src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_traverser import traverse_graph
from src.llm_agent import generate_sql

st.set_page_config(page_title="DataGraph OKF Copilot", layout="wide")

st.title("📊 DataGraph: OKF-Native Enterprise Copilot")
st.caption("No Vector DBs. No Embeddings. Pure, structured knowledge traversal powered by Gemini 3.8 Flash ⚡")

def get_start_file(query: str) -> str:
    """Simple keyword router to pick the best starting OKF file."""
    query_lower = query.lower()
    if any(word in query_lower for word in ["cac", "acquisition", "marketing", "spend"]):
        return "knowledge_base/metrics/cac.md"
    elif any(word in query_lower for word in ["mrr", "revenue", "recurring", "subscription"]):
        return "knowledge_base/metrics/mrr.md"
    else:
        return "knowledge_base/index.md" # Fallback to index

# Sidebar for Agent Trace
with st.sidebar:
    st.header("🕵️ Agent Trace")
    st.info("Watch how the agent navigates the knowledge graph.")
    
    if "trace" in st.session_state:
        st.subheader("Files Visited:")
        for i, file in enumerate(st.session_state.trace, 1):
            clean_path = file.replace("knowledge_base/", "")
            st.code(f"{i}. {clean_path}", language="markdown")
    else:
        st.write("No query run yet.")

# Main UI
st.markdown("### 💬 Ask a Data Question")
user_query = st.text_area(
    "Try: 'Calculate this month MRR excluding trials' OR 'How do we calculate CAC?'",
    placeholder="e.g., Write a SQL query to calculate CAC, and tell me about any data latency issues.",
    height=100
)

if st.button("Generate Answer 🚀", type="primary"):
    if not user_query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("🧠 Agent is selecting the right knowledge entry point..."):
            start_file = get_start_file(user_query)
            
        with st.spinner(f"🕸️ Traversing OKF Graph starting from: `{start_file.replace('knowledge_base/', '')}`..."):
            context, trace = traverse_graph(start_file, max_depth=3)
            st.session_state.trace = trace
            
        with st.spinner("✨ Generating response via Gemini 3.8 Flash..."):
            try:
                response_text = generate_sql(user_query, context)
                
                # Render the clean markdown response
                st.markdown(response_text)
                
                # Optional: Let advanced users see the raw context
                with st.expander("🔍 View Raw OKF Context Sent to LLM"):
                    st.markdown(context)
                    
            except Exception as e:
                st.error(f"Error generating response: {e}")
                st.write("Make sure your `.env` file has a valid `GEMINI_API_KEY`.")