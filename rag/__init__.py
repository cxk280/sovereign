"""rag — retrieval-augmented generation over internal knowledge, entirely local.

Ingests ``sample_data/`` into a vector store and answers similarity queries. Two
interchangeable implementations back each seam so the same pipeline runs with
zero setup (``HashEmbedder`` + ``InMemoryStore``) or in production
(``SentenceTransformerEmbedder`` + ``QdrantStore``). Consumed by the
``mcp_servers`` package.
"""
