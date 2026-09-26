import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any

def parse_okf_file(file_path: str) -> Dict[str, Any]:
    """Reads an OKF file and returns metadata (YAML) and content (Markdown)."""
    normalized_path = os.path.normpath(file_path)
    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"OKF file not found: {normalized_path}")

    with open(normalized_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Regex to split the YAML frontmatter from the Markdown body (cross-platform CRLF/LF)
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$", content, re.DOTALL)
    if not match:
        raise ValueError(f"Invalid OKF format in {normalized_path}")

    raw_metadata = yaml.safe_load(match.group(1))
    metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
    body = match.group(2).strip()

    return {"metadata": metadata, "body": body, "path": normalized_path}

def extract_links(body: str) -> List[str]:
    """Extracts and sanitizes relative markdown file links from the body using list comprehension."""
    raw_links = re.findall(r"\[.*?\]\((.*?)\)", body)
    
    # Strip URL anchors/queries, ignore web protocols and in-page anchors
    sanitized = [
        link.split("#")[0].split("?")[0].strip()
        for link in raw_links
        if link.strip() and not link.strip().startswith(("http://", "https://", "mailto:", "#"))
    ]
    
    # Deduplicate while preserving original appearance order
    return [l for i, l in enumerate(sanitized) if l and l not in sanitized[:i]]