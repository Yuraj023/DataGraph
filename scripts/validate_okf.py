import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.okf_parser import parse_okf_file, extract_links

def validate_bundle(root_dir: str = "knowledge_base") -> None:
    """Checks all markdown files for valid OKF frontmatter and unbroken links using list comprehensions."""
    errors = []
    
    # Collect all markdown files using list comprehension
    all_files = [
        os.path.normpath(os.path.join(root, file))
        for root, _, files in os.walk(root_dir)
        for file in files
        if file.endswith(".md")
    ]
    
    yaml_rel_keys = [
        "related_tables",
        "related_runbooks",
        "related_infrastructure",
        "related_product",
        "related_security",
    ]

    for file_path in all_files:
        dir_name = os.path.dirname(file_path)
        try:
            parsed = parse_okf_file(file_path)
            metadata = parsed.get("metadata", {})
            body = parsed.get("body", "")
            
            # 1. Validate markdown body links using list comprehension
            body_links = [
                (link, os.path.normpath(os.path.join(dir_name, link)))
                for link in extract_links(body)
            ]
            for raw_link, resolved_path in body_links:
                if not os.path.exists(resolved_path):
                    errors.append(f"Broken Markdown link in {file_path}: '{raw_link}' -> '{resolved_path}'")

            # 2. Validate YAML frontmatter relationship links using list comprehension
            yaml_links = [
                (key, rel, os.path.normpath(os.path.join(dir_name, rel)))
                for key in yaml_rel_keys
                for rel in (metadata.get(key) or [])
                if rel
            ]
            for key, raw_link, resolved_path in yaml_links:
                if not os.path.exists(resolved_path):
                    errors.append(f"Broken YAML '{key}' link in {file_path}: '{raw_link}' -> '{resolved_path}'")

        except Exception as e:
            errors.append(f"Parse error in {file_path}: {e}")

    print(f"Checked {len(all_files)} files in '{root_dir}'.")
    if errors:
        print(f"Found {len(errors)} issues:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("OKF Bundle is fully valid! No broken links or YAML syntax errors.")

if __name__ == "__main__":
    validate_bundle("knowledge_base")