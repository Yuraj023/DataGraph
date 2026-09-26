"""
Open Knowledge Format (OKF) vs Traditional RAG Architecture.

Notice:
DataGraph strictly follows Google's Open Knowledge Format (OKF) technique.
There is NO tokenization, word-chunking, or vector database retrieval in this project.
Instead, knowledge is represented as linked Markdown documents with structured YAML frontmatter,
and traversed deterministically via explicit graph links.
"""

def retrieve_via_rag(query: str):
    """Placeholder to indicate that RAG and tokenization are intentionally omitted in favor of OKF."""
    raise NotImplementedError(
        "Traditional RAG and text-chunk tokenization are not used in this project. "
        "Use src.graph_traverser.traverse_graph() for OKF traversal."
    )