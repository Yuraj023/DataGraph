import sys
import os
import re
from typing import Any, List, Tuple
import streamlit as st

# Add workspace root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph_traverser import traverse_graph
from src.llm_agent import generate_analysis

st.set_page_config(
    page_title="DataGraph OKF Copilot",
    page_icon="☢️",
    layout="wide"
)

# Enterprise Header
st.title("DataGraph: OKF-Native Enterprise Copilot")
st.caption("Deterministic Knowledge Graph Traversal | Zero Tokenization | No Vector DBs | Powered by Open Knowledge Format")
st.divider()

# ============================================================
# Smart Router Rules (Data-Driven with List Comprehensions)
# ============================================================

ROUTING_RULES: List[Tuple[List[str], str]] = [
    (["cac", "acquisition", "marketing spend"], "knowledge_base/metrics/cac.md"),
    (["mrr", "revenue", "recurring"], "knowledge_base/metrics/mrr.md"),
    (["retention", "engagement", "churn", "dau"], "knowledge_base/metrics/user_retention.md"),
    (["subscription", "billing cycle", "plan"], "knowledge_base/tables/subscriptions.md"),
    (["transaction", "payment", "refund", "charge"], "knowledge_base/tables/transactions.md"),
    (["user", "customer dimension", "signup"], "knowledge_base/tables/users.md"),
    (["event", "page view", "behavior"], "knowledge_base/tables/user_events.md"),
    (["billing logic", "proration", "dunning"], "knowledge_base/runbooks/billing_logic.md"),
    (["staging", "ec2", "server", "outage", "down", "incident"], "knowledge_base/runbooks/incident_response.md"),
    (["deployment", "deploy", "rollback", "ci/cd", "pipeline"], "knowledge_base/infrastructure/deployment_pipeline.md"),
    (["database", "rds", "postgres", "replica"], "knowledge_base/infrastructure/aws_rds_prod.md"),
    (["gdpr", "right to be forgotten", "erasure"], "knowledge_base/security/gdpr_compliance.md"),
    (["pii", "compliance", "masking", "anonymization"], "knowledge_base/security/pii_handling.md"),
    (["access", "permission", "role", "rbac", "iam"], "knowledge_base/security/access_control.md"),
    (["audit", "log retention", "soc2"], "knowledge_base/security/audit_requirements.md"),
    (["api", "endpoint", "rest", "schema", "contract"], "knowledge_base/product/api_contracts.md"),
    (["feature flag", "ab test", "experiment", "rollout"], "knowledge_base/product/feature_flags.md"),
]

PERSONA_RULES: List[Tuple[List[str], str]] = [
    (["pii", "gdpr", "compliance", "audit", "security", "access", "role", "rbac"], "security_auditor"),
    (["down", "outage", "incident", "deploy", "server", "database", "rds", "ec2", "pipeline", "staging"], "devops_engineer"),
]

def get_start_file(query: str) -> str:
    """Smart router selecting entry point using list comprehension."""
    query_lower = query.lower()
    matches = [
        target_file
        for keywords, target_file in ROUTING_RULES
        if any(kw in query_lower for kw in keywords)
    ]
    return matches[0] if matches else "knowledge_base/index.md"

def get_agent_type(query: str) -> str:
    """Infer optimal agent persona based on query using list comprehension."""
    query_lower = query.lower()
    matches = [
        persona
        for keywords, persona in PERSONA_RULES
        if any(kw in query_lower for kw in keywords)
    ]
    return matches[0] if matches else "data_analyst"

def clean_code_block(content: Any) -> str:
    """Safely cleans and extracts raw code blocks."""
    if isinstance(content, list):
        content = "\n".join(str(item) for item in content)
    elif not isinstance(content, str):
        content = str(content)
    
    cleaned = re.sub(r"^```(?:bash|sql|sh|json)?\s*", "", content.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()

# ============================================================
# Sidebar: Navigation Trace & Graph Settings
# ============================================================

with st.sidebar:
    st.header("Graph Traversal Control")
    st.caption("Explicit OKF link traversal settings")
    max_depth = st.slider("Traversal Max Depth", min_value=1, max_value=4, value=3, help="Maximum recursion depth when following OKF links.")
    
    st.divider()
    st.header("Agent Trace")
    
    if "trace" in st.session_state and st.session_state.trace:
        st.success(f"Visited {len(st.session_state.trace)} Knowledge Nodes")
        for i, file_path in enumerate(st.session_state.trace, 1):
            clean_path = file_path.replace("knowledge_base\\", "").replace("knowledge_base/", "")
            st.markdown(f"**{i}.** `{clean_path}`")
    else:
        st.info("Execute a query to inspect the traversal trace.")

# ============================================================
# Query Input Area
# ============================================================

st.markdown("### Ask a Question")

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

submit_col1, _ = st.columns([1, 5])
with submit_col1:
    submit_button = st.button("Generate Answer", type="primary", use_container_width=True)

# ============================================================
# Execution Flow
# ============================================================

if submit_button:
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Selecting knowledge entry point..."):
            start_file = get_start_file(user_query)
            agent_type = agent_override if agent_override != "auto" else get_agent_type(user_query)
            
        with st.spinner(f"Traversing OKF Graph starting from: `{start_file}` (depth={max_depth})..."):
            context, trace = traverse_graph(start_file, max_depth=max_depth)
            st.session_state.trace = trace
            
        with st.spinner(f"Synthesizing structured response as {agent_type.replace('_', ' ').title()}..."):
            try:
                result = generate_analysis(user_query, context, agent_type)
                
                st.divider()
                
                # Check for fatal errors
                error_msg = str(result.get("error", ""))
                if "API Error" in error_msg or "Failed to parse" in error_msg or "empty response" in error_msg.lower():
                    st.error(f"System Error: {result['error']}")
                    if "raw_response" in result:
                        with st.expander("View Raw LLM Output (Debugging)"):
                            st.code(result["raw_response"])
                else:
                    if result.get("error"):
                        st.warning(f"Context Note: {result['error']}")

                    # Summary metric pills
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Active Persona", agent_type.replace("_", " ").title())
                    m2.metric("Nodes Visited", len(trace))
                    m3.metric("Entry Point", os.path.basename(start_file))
                    
                    # Persona Native Rendering
                    if agent_type == "data_analyst":
                        if result.get("logic"):
                            st.subheader("Business Logic")
                            st.markdown(result["logic"])
                        if result.get("sql"):
                            st.subheader("SQL Query")
                            st.code(clean_code_block(result["sql"]), language="sql")
                        if result.get("tip"):
                            st.info(f"**Data Quality Pro-Tip:** {result['tip']}")
                            
                    elif agent_type == "devops_engineer":
                        if result.get("diagnosis"):
                            st.subheader("Incident Diagnosis")
                            st.markdown(result["diagnosis"])
                        if result.get("commands"):
                            st.subheader("Runbook CLI Commands")
                            st.code(clean_code_block(result["commands"]), language="bash")
                        if result.get("escalation"):
                            st.warning(f"**Escalation Path:** {result['escalation']}")
                            
                    elif agent_type == "security_auditor":
                        if result.get("risk_assessment"):
                            st.subheader("Risk Assessment")
                            st.markdown(result["risk_assessment"])
                        if result.get("recommendations"):
                            st.subheader("Security Recommendations")
                            st.markdown(result["recommendations"])
                        if result.get("compliance_gaps"):
                            st.error(f"**Compliance Gaps:** {result['compliance_gaps']}")
                
                st.divider()
                
                # Assembled Knowledge Context Inspector
                with st.expander("View Assembled OKF Context (Deterministic Graph Traversal)"):
                    st.markdown("```markdown\n" + context + "\n```")
                    
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.exception(e)