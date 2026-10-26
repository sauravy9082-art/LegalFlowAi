import os
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Local RAG ChromaDB Store (Rule 22 & Rule 47).
    Embeddings and document chunks stored locally. Zero cloud API calls.
    """

    def __init__(self):
        self.chroma_path = settings.CHROMA_PATH
        self.client = None
        self.collection = None

    def _init_chroma(self):
        if self.client is not None:
            return
        try:
            import chromadb
            os.makedirs(self.chroma_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.chroma_path)
            self.collection = self.client.get_or_create_collection(
                name="legalflow_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.error(f"ChromaDB initialization error: {e}")
            self.client = None
            self.collection = None

    async def add_document_chunks(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]]
    ) -> bool:
        self._init_chroma()
        if not self.collection:
            logger.warning("ChromaDB unavailable. Skipping vector index addition.")
            return False

        try:
            ids = [f"{document_id}_chunk_{c['chunk_index']}" for c in chunks]
            documents = [c["text_content"] for c in chunks]
            metadatas = [{
                "document_id": document_id,
                "start_page": c["start_page"],
                "end_page": c["end_page"],
                "chunk_index": c["chunk_index"]
            } for c in chunks]

            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upsert chunks into ChromaDB: {e}")
            return False

    async def search_relevant_context(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        self._init_chroma()
        if not self.collection:
            return []

        try:
            where_clause = {"document_id": document_id} if document_id else None
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_clause
            )

            retrieved = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

                for doc, meta, dist in zip(docs, metas, distances):
                    retrieved.append({
                        "text": doc,
                        "metadata": meta,
                        "similarity_score": round(1.0 - float(dist), 4) if dist is not None else 1.0
                    })
            return retrieved
        except Exception as e:
            logger.error(f"ChromaDB similarity search error: {e}")
            return []
