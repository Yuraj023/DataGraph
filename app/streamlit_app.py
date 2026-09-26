import sys
import os
import streamlit as st
import re

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

def format_response(response_text: str, query: str) -> None:
    """
    Parse and format the LLM response based on content type.
    All formatting logic lives here, not in the LLM prompt.
    """
    query_lower = query.lower()
    
    # Detect response type and format accordingly
    if any(word in query_lower for word in ["sql", "query", "calculate", "metric"]):
        format_sql_response(response_text)
    elif any(word in query_lower for word in ["down", "incident", "troubleshoot", "command"]):
        format_devops_response(response_text)
    elif any(word in query_lower for word in ["pii", "gdpr", "compliance", "security"]):
        format_security_response(response_text)
    else:
        # Generic response
        st.write(response_text)

def format_sql_response(response_text: str) -> None:
    """Extract and format SQL queries from response."""
    # Look for SQL code blocks
    sql_match = re.search(r'```sql\s*(.*?)\s*```', response_text, re.DOTALL)
    
    if sql_match:
        sql_code = sql_match.group(1).strip()
        
        # Split response into parts
        parts = response_text.split('```sql')
        before_sql = parts[0].strip()
        after_sql = parts[1].split('```')[-1].strip() if len(parts) > 1 else ""
        
        # Render business logic
        if before_sql:
            st.subheader("Business Logic")
            st.write(before_sql)
        
        # Render SQL
        st.subheader("SQL Query")
        st.code(sql_code, language="sql")
        
        # Render pro-tip
        if after_sql and len(after_sql) > 10:
            st.info(after_sql)
    else:
        # No SQL found, just render as-is
        st.write(response_text)

def format_devops_response(response_text: str) -> None:
    """Extract and format CLI commands from response."""
    # Look for bash/code blocks
    cmd_match = re.search(r'```(?:bash|shell)?\s*(.*?)\s*```', response_text, re.DOTALL)
    
    if cmd_match:
        cmd_code = cmd_match.group(1).strip()
        
        parts = response_text.split('```')
        before_cmd = parts[0].strip()
        after_cmd = parts[-1].strip() if len(parts) > 1 else ""
        
        # Render diagnosis
        if before_cmd:
            st.subheader("Diagnosis")
            st.write(before_cmd)
        
        # Render commands
        st.subheader("Commands to Run")
        st.code(cmd_code, language="bash")
        
        # Render escalation
        if after_cmd and len(after_cmd) > 10:
            st.warning(after_cmd)
    else:
        st.write(response_text)

def format_security_response(response_text: str) -> None:
    """Format security/compliance responses."""
    lines = response_text.split('\n')
    
    risk_section = []
    rec_section = []
    current_section = None
    
    for line in lines:
        line_lower = line.lower()
        if 'risk' in line_lower or 'assessment' in line_lower:
            current_section = 'risk'
        elif 'recommendation' in line_lower or 'action' in line_lower:
            current_section = 'rec'
        elif current_section == 'risk':
            risk_section.append(line)
        elif current_section == 'rec':
            rec_section.append(line)
    
    # Render risk assessment
    if risk_section:
        st.subheader("Risk Assessment")
        st.write('\n'.join(risk_section).strip())
    
    # Render recommendations
    if rec_section:
        st.subheader("Recommendations")
        for line in rec_section:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                # Clean up bullet points
                line = re.sub(r'^[-*]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)
                st.markdown(f"- {line}")
            elif line:
                st.write(line)
    
    # If no sections detected, render as-is
    if not risk_section and not rec_section:
        st.write(response_text)

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
st.markdown("### Ask a Question")

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
        # Determine starting file
        with st.spinner("Selecting knowledge entry point..."):
            start_file = get_start_file(user_query)
            
        # Traverse the knowledge graph
        with st.spinner(f"Traversing OKF Graph from: `{start_file.replace('knowledge_base/', '')}`..."):
            context, trace = traverse_graph(start_file, max_depth=3)
            st.session_state.trace = trace
            
        # Generate response
        with st.spinner("Generating response..."):
            try:
                result = generate_analysis(user_query, context)
                
                st.divider()
                
                # Handle error
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    # Format and render response
                    format_response(result["response"], user_query)
                
                st.divider()
                
                # Raw Context Expander
                with st.expander("View Raw OKF Context"):
                    st.markdown("```markdown\n" + context + "\n```")
                    
            except Exception as e:
                st.error(f"Unexpected error: {e}")