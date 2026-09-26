import re
import yaml
from pathlib import Path

def parse_okf_file(file_path: str) -> dict:
    """Reads an OKF file and returns metadata (YAML) and content (Markdown)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to split the YAML frontmatter from the Markdown body
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError(f"Invalid OKF format in {file_path}")
        
    metadata = yaml.safe_load(match.group(1))
    body = match.group(2).strip()
    
    return {"metadata": metadata, "body": body, "path": file_path}

def extract_links(body: str) -> list:
    """Extracts all relative markdown links from the body."""
    # Matches standard markdown links like [Text](../path/to/file.md)
    return re.findall(r'\[.*?\]\((.*?)\)', body)