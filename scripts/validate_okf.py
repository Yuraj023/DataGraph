import os
import sys

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.okf_parser import parse_okf_file, extract_links

def validate_bundle(root_dir: str):
    """Checks all markdown files for valid YAML and unbroken links."""
    errors = []
    files_checked = 0
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                files_checked += 1
                
                try:
                    parsed = parse_okf_file(file_path)
                    links = extract_links(parsed["body"])
                    
                    for link in links:
                        # Resolve relative path
                        next_path = os.path.normpath(os.path.join(os.path.dirname(file_path), link))
                        if not os.path.exists(next_path):
                            errors.append(f"Broken link in {file_path}: {link} -> {next_path}")
                            
                except Exception as e:
                    errors.append(f"Parse error in {file_path}: {e}")

    print(f"✅ Checked {files_checked} files.")
    if errors:
        print(f"❌ Found {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("🎉 OKF Bundle is perfectly valid! No broken links or YAML errors.")

if __name__ == "__main__":
    validate_bundle("knowledge_base")