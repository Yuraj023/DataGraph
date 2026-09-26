import os
from .okf_parser import parse_okf_file, extract_links

def traverse_graph(start_file: str, max_depth: int = 3) -> str:
    """
    Starts at a file, reads it, and follows its links up to max_depth.
    Returns a single formatted string to be injected into the LLM prompt.
    """
    visited = set()
    context_blocks = []

    def _walk(current_path, depth):
        if current_path in visited or depth > max_depth:
            return
        visited.add(current_path)
        
        if not os.path.exists(current_path):
            return

        parsed = parse_okf_file(current_path)
        meta = parsed["metadata"]
        
        # Format the context beautifully for the LLM
        header = f"### [{meta.get('type', 'Unknown')}] {meta.get('title', 'Untitled')}\n"
        meta_str = f"**Metadata:** {meta}\n\n"
        body_str = f"**Content:**\n{parsed['body']}\n"
        
        context_blocks.append(header + meta_str + body_str)
        
        # Recursively follow links
        links = extract_links(parsed["body"])
        for link in links:
            # Resolve relative paths based on the current file's directory
            next_path = os.path.normpath(os.path.join(os.path.dirname(current_path), link))
            _walk(next_path, depth + 1)

    _walk(start_file, 0)
    return "\n---\n".join(context_blocks)