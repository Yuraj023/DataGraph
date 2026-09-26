import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_traverser import traverse_graph
from src.llm_agent import generate_analysis

st.set_page_config(page_title="DataGraph OKF Copilot", layout="wide")

st.title("DataGraph: OKF-Native Enterprise Copilot")
st.caption("No Vector DBs. No Embeddings. Pure, structured knowledge traversal powered by Gemini 3.8 Flash.")
st.divider()

def get_start_file(query: str) -> str:
    """Smart router for entry point selection."""
    query_lower = query.lower()
    
    # Data Analytics
    if any(word in query_lower for word in ["cac", "acquisition", "marketing"]):
        return "knowledge_base/metrics/cac.md"
    elif any(word in query_lower for word in ["mrr", "revenue", "recurring"]):
        return "knowledge_base/metrics/mrr.md"
    elif any(word in query_lower for word in ["retention", "engagement", "churn"]):
        return "knowledge_base/metrics/user_retention.md"
    
    # DevOps
    elif any(word in query_lower for word in ["staging", "ec2", "server", "down", "incident"]):
        return "knowledge_base/runbooks/incident_response.md"
    elif any(word in query_lower for word in ["deployment", "deploy", "rollback"]):
        return "knowledge_base/infrastructure/deployment_pipeline.md"
    elif any(word in query_lower for word in ["database", "rds", "postgres"]):
        return "knowledge_base/infrastructure/aws_rds_prod.md"
    
    # Security
    elif any(word in query_lower for word in ["pii", "gdpr", "compliance", "audit"]):
        return "knowledge_base/security/pii_handling.md"
    elif any(word in query_lower for word in ["access", "permission", "role"]):
        return "knowledge_base/security/access_control.md"
    
    # Product
    elif any(word in query_lower for word in ["api", "endpoint", "rest"]):
        return "knowledge_base/product/api_contracts.md"
    elif any(word in query_lower for word in ["feature flag", "ab test", "experiment"]):
        return "knowledge_base/product/feature_flags.md"
    
    else:
        return "knowledge_base/index.md"

def get_agent_type(query: str) -> str:
    """Infer the best agent persona based on the query."""
    query_lower = query.lower()
    if any(word in query_lower for word in ["pii", "gdpr", "compliance", "audit", "security", "access"]):
        return "security_auditor"
    elif any(word in query_lower for word in ["down", "outage", "incident", "deploy", "server", "database", "rds", "ec2"]):
        return "devops_engineer"
    else:
        return "data_analyst"

# Sidebar for Agent Trace
with st.sidebar:
    st.header("Agent Trace")
    st.caption("Knowledge graph navigation path")
    
    if "trace" in st.session_state:
        st.markdown("**Files Visited:**")
        for i, file in enumerate(st.session_state.trace, 1):
            # Handle both Windows and Mac/Linux path separators
            clean_path = file.replace("knowledge_base\\", "").replace("knowledge_base/", "")
            st.markdown(f"{i}. `{clean_path}`")
    else:
        st.info("Run a query to see the agent's navigation path.")

# Main UI
st.markdown("### Ask a Question")

# Agent persona selector (optional override)
col1, col2 = st.columns([1, 4])
with col1:
    agent_override = st.selectbox(
        "Agent Persona",
        ["auto", "data_analyst", "devops_engineer", "security_auditor"],
        format_func=lambda x: "Auto-detect" if x == "auto" else x.replace("_", " ").title()
    )

user_query = st.text_area(
    label="Query",
    placeholder="Examples:\n- Calculate this month's MRR excluding trials\n- Our staging server is down, what do I do?\n- Are we GDPR compliant for EU user data?",
    height=120,
    label_visibility="collapsed"
)

submit_col1, submit_col2 = st.columns([1, 5])
with submit_col1:
    submit_button = st.button("Generate Answer", type="primary", use_container_width=True)

if submit_button:
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        # Determine starting file and agent type
        with st.spinner("Selecting knowledge entry point..."):
            start_file = get_start_file(user_query)
            agent_type = agent_override if agent_override != "auto" else get_agent_type(user_query)
            
        # Traverse the knowledge graph
        with st.spinner(f"Traversing OKF Graph from: `{start_file.replace('knowledge_base/', '').replace('knowledge_base\\', '')}`..."):
            context, trace = traverse_graph(start_file, max_depth=3)
            st.session_state.trace = trace
            
        # Generate response
        with st.spinner(f"Generating response as {agent_type.replace('_', ' ').title()}..."):
            try:
                # The LLM agent now returns a structured JSON dictionary directly
                result = generate_analysis(user_query, context, agent_type)
                
                st.divider()
                
                # Handle global API errors
                if "error" in result and result["error"] and "API Error" in str(result["error"]):
                    st.error(f"System Error: {result['error']}")
                else:
                    # Handle context warnings (e.g., missing info in OKF bundle)
                    if result.get("error"):
                        st.warning(f"Context Warning: {result['error']}")
                    
                    # Render UI natively based on the agent type and JSON keys
                    if agent_type == "data_analyst":
                        if result.get("logic"):
                            st.subheader("Business Logic")
                            st.write(result["logic"])
                        if result.get("sql"):
                            st.subheader("SQL Query")
                            # Clean any accidental markdown backticks just in case
                            clean_sql = result["sql"].replace("```sql", "").replace("```", "").strip()
                            st.code(clean_sql, language="sql")
                        if result.get("tip"):
                            st.info(result["tip"])
                            
                    elif agent_type == "devops_engineer":
                        if result.get("diagnosis"):
                            st.subheader("Diagnosis")
                            st.write(result["diagnosis"])
                        if result.get("commands"):
                            st.subheader("Commands to Run")
                            clean_cmd = result["commands"].replace("```bash", "").replace("```", "").strip()
                            st.code(clean_cmd, language="bash")
                        if result.get("escalation"):
                            st.warning(result["escalation"])
                            
                    elif agent_type == "security_auditor":
                        if result.get("risk_assessment"):
                            st.subheader("Risk Assessment")
                            st.write(result["risk_assessment"])
                        if result.get("recommendations"):
                            st.subheader("Recommendations")
                            st.markdown(result["recommendations"])
                        if result.get("compliance_gaps"):
                            st.error(result["compliance_gaps"])
                
                st.divider()
                
                # Raw Context Expander
                with st.expander("View Raw OKF Context"):
                    st.markdown("```markdown\n" + context + "\n```")
                    
            except Exception as e:
                st.error(f"Unexpected error: {e}")