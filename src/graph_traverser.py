import os
from .okf_parser import parse_okf_file, extract_links

def traverse_graph(start_file: str, max_depth: int = 3) -> tuple[str, list[str]]:
    """
    Traverses the OKF knowledge graph starting from a given file.
    
    Features:
    - Follows explicit Markdown links in the document body
    - CONDITIONAL: Auto-follows related_security links if file contains PII
    - CONDITIONAL: Auto-follows related_tables, related_runbooks, related_infrastructure from YAML
    - Prevents infinite loops via visited set
    - Returns formatted context string and trace of visited files
    
    Args:
        start_file: Path to the starting OKF markdown file
        max_depth: Maximum recursion depth for link following
        
    Returns:
        tuple: (formatted_context_string, list_of_visited_file_paths)
    """
    visited = set()
    context_blocks = []
    trace = []

    def _walk(current_path: str, depth: int):
        # Normalize path to prevent duplicates
        current_path = os.path.normpath(current_path)
        
        if current_path in visited or depth > max_depth:
            return
        visited.add(current_path)
        trace.append(current_path)
        
        if not os.path.exists(current_path):
            return

        try:
            parsed = parse_okf_file(current_path)
        except Exception as e:
            context_blocks.append(f"### ERROR: Could not parse {current_path}\n{str(e)}\n")
            return
            
        meta = parsed["metadata"]
        
        # Format context block with metadata and body
        header = f"### [{meta.get('type', 'Unknown')}] {meta.get('title', 'Untitled')}\n"
        meta_str = f"**File:** `{current_path}`\n"
        meta_str += f"**Metadata:** {meta}\n\n"
        body_str = f"**Content:**\n{parsed['body']}\n"
        
        context_blocks.append(header + meta_str + body_str)
        
        # Collect all links to follow
        links_to_follow = set()
        
        # 1. Extract links from Markdown body
        body_links = extract_links(parsed["body"])
        for link in body_links:
            next_path = os.path.normpath(os.path.join(os.path.dirname(current_path), link))
            links_to_follow.add(next_path)
        
        # 2. CONDITIONAL TRAVERSAL: Auto-follow related_* links from YAML frontmatter
        # This is the key OKF advantage: explicit relationships in metadata
        
        # If file contains PII, auto-follow security policies
        if meta.get("contains_pii") or meta.get("pii_level") == "HIGH":
            for sec_link in meta.get("related_security", []):
                next_path = os.path.normpath(os.path.join(os.path.dirname(current_path), sec_link))
                links_to_follow.add(next_path)
        
        # Always follow explicit relationships from YAML
        for rel_key in ["related_tables", "related_runbooks", "related_infrastructure", 
                        "related_product", "related_security"]:
            for rel_link in meta.get(rel_key, []):
                next_path = os.path.normpath(os.path.join(os.path.dirname(current_path), rel_link))
                links_to_follow.add(next_path)
        
        # Recursively follow all collected links
        for next_path in links_to_follow:
            _walk(next_path, depth + 1)

    _walk(start_file, 0)
    
    context_str = "\n---\n".join(context_blocks)
    return context_str, trace