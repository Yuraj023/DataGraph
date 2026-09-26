import os
from .okf_parser import parse_okf_file, extract_links

def traverse_graph(start_file: str, max_depth: int = 1) -> tuple[str, list[str]]:
    """
    Optimized traverser that:
    - Strips YAML frontmatter (saves ~30% tokens)
    - Removes verbose sections (saves ~20% tokens)
    - Limits depth to reduce file count
    """
    visited = set()
    context_blocks = []
    trace = []

    def _compress_content(body: str) -> str:
        """Remove verbose sections that waste tokens."""
        lines = body.split('\n')
        compressed = []
        skip_section = False
        
        for line in lines:
            # Skip verbose sections that don't help SQL generation
            if line.startswith('## Data Quality Notes'):
                skip_section = True
                continue
            if line.startswith('## Common Query Patterns'):
                skip_section = True
                continue
            if line.startswith('## Join Patterns'):
                skip_section = True
                continue
                
            # Stop skipping at next section
            if line.startswith('## ') and skip_section:
                skip_section = False
            
            if not skip_section:
                # Remove excessive blank lines
                if line.strip() or (compressed and compressed[-1].strip()):
                    compressed.append(line)
        
        return '\n'.join(compressed).strip()

    def _walk(current_path: str, depth: int):
        current_path = os.path.normpath(current_path)
        
        if current_path in visited or depth > max_depth:
            return
        if not os.path.exists(current_path):
            return
            
        visited.add(current_path)
        trace.append(current_path)
        
        try:
            parsed = parse_okf_file(current_path)
        except Exception:
            return
            
        meta = parsed["metadata"]
        body = parsed['body']
        
        # OPTIMIZATION: Only include essential metadata (type + title)
        # Skip owner, tags, timestamps, etc. - they waste tokens
        essential_meta = f"[{meta.get('type', 'Unknown')}] {meta.get('title', 'Untitled')}"
        
        # OPTIMIZATION: Compress the body content
        compressed_body = _compress_content(body)
        
        # Build compact context block
        context_blocks.append(f"### {essential_meta}\n{compressed_body}")
        
        # Collect links to follow
        links_to_follow = set()
        
        for link in extract_links(parsed["body"]):
            next_path = os.path.normpath(os.path.join(os.path.dirname(current_path), link))
            links_to_follow.add(next_path)
        
        # Conditional traversal for PII
        if meta.get("contains_pii") or meta.get("pii_level") == "HIGH":
            for sec_link in meta.get("related_security", []):
                next_path = os.path.normpath(os.path.join(os.path.dirname(current_path), sec_link))
                links_to_follow.add(next_path)
        
        for rel_key in ["related_tables", "related_runbooks", "related_infrastructure"]:
            for rel_link in meta.get(rel_key, []):
                next_path = os.path.normpath(os.path.join(os.path.dirname(current_path), rel_link))
                links_to_follow.add(next_path)
        
        # Follow links (only unvisited ones)
        for next_path in links_to_follow:
            if next_path not in visited:
                _walk(next_path, depth + 1)

    _walk(start_file, 0)
    
    # OPTIMIZATION: Join with minimal separator
    context_str = "\n\n---\n\n".join(context_blocks)
    return context_str, trace