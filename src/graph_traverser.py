import os
from typing import Tuple, List, Set
from .okf_parser import parse_okf_file, extract_links

def traverse_graph(start_file: str, max_depth: int = 3) -> Tuple[str, List[str]]:
    """
    Traverses the OKF knowledge graph starting from a given file.
    
    Features:
    - Follows explicit Markdown links in the document body.
    - CONDITIONAL: Auto-follows related_security links if document contains PII or is a security doc.
    - Follows explicit YAML relationships (tables, runbooks, infrastructure, product).
    - Prevents cycles using canonical path tracking.
    - Uses set/list comprehensions for optimized path resolution.
    
    Args:
        start_file: Path to the starting OKF markdown file.
        max_depth: Maximum recursion depth for graph links.
        
    Returns:
        tuple: (formatted_context_string, list_of_visited_file_paths)
    """
    visited_canonical: Set[str] = set()
    context_blocks: List[str] = []
    trace: List[str] = []

    def _walk(current_path: str, depth: int) -> None:
        normalized_path = os.path.normpath(current_path)
        canonical_path = os.path.abspath(normalized_path)
        
        if canonical_path in visited_canonical or depth > max_depth:
            return
        if not os.path.exists(normalized_path):
            return
            
        visited_canonical.add(canonical_path)
        trace.append(normalized_path)
        
        try:
            parsed = parse_okf_file(normalized_path)
        except Exception:
            return
            
        meta = parsed.get("metadata", {})
        body = parsed.get("body", "")
        
        # Build concise header and operational metadata using list comprehension
        relevant_keys = [
            "type", "title", "resource", "partitioning", "clustering", 
            "contains_pii", "pii_level", "compliance", "data_freshness"
        ]
        meta_lines = [
            f"**{k}:** {meta[k]}"
            for k in relevant_keys
            if k in meta and meta[k] is not None
        ]
        meta_str = " | ".join(meta_lines) if meta_lines else ""
        
        header = f"### [{meta.get('type', 'Document')}] {meta.get('title', os.path.basename(normalized_path))}"
        header_block = f"{header}\n{meta_str}\n" if meta_str else f"{header}\n"
        context_blocks.append(f"{header_block}\n{body}".strip())
        
        dir_name = os.path.dirname(normalized_path)
        
        # 1. Relative Markdown body links using set comprehension
        body_links = {
            os.path.normpath(os.path.join(dir_name, link))
            for link in extract_links(body)
        }
        
        # 2. General YAML relationship links using list/set comprehension
        general_rel_keys = [
            "related_tables",
            "related_runbooks",
            "related_infrastructure",
            "related_product",
        ]
        yaml_links = {
            os.path.normpath(os.path.join(dir_name, rel_link))
            for rel_key in general_rel_keys
            for rel_link in (meta.get(rel_key) or [])
            if rel_link
        }
        
        # 3. CONDITIONAL TRAVERSAL: Follow security policies if document touches PII or is a security doc
        has_pii = (
            bool(meta.get("contains_pii"))
            or "HIGH" in str(meta.get("pii_level", "")).upper()
            or "PII" in str(meta.get("pii_level", "")).upper()
        )
        is_sec_doc = (
            meta.get("type") == "Security Policy"
            or "security" in normalized_path.replace("\\", "/").lower()
        )
        
        security_links = {
            os.path.normpath(os.path.join(dir_name, sec_link))
            for sec_link in (meta.get("related_security") or [])
            if sec_link
        } if (has_pii or is_sec_doc) else set()
        
        # Combine all outbound links
        links_to_follow = body_links | yaml_links | security_links
        
        # Recursively visit next nodes
        for next_path in sorted(links_to_follow):
            next_canonical = os.path.abspath(next_path)
            if next_canonical not in visited_canonical:
                _walk(next_path, depth + 1)

    _walk(start_file, 0)
    
    context_str = "\n\n---\n\n".join(context_blocks)
    return context_str, trace