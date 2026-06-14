"""Chroma vector store service."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb

from app.core.config import settings


def _build_collection_name(user_id: int, project_id: int) -> str:
    return f"user_{user_id}_project_{project_id}"


@lru_cache(maxsize=1)
def get_chroma_client() -> Any:
	"""Create and cache a persistent Chroma client."""
	persist_dir = Path(settings.chroma_persist_dir).resolve()
	persist_dir.mkdir(parents=True, exist_ok=True)
	return chromadb.PersistentClient(path=str(persist_dir))


def create_collection(user_id: int, project_id: int) -> Any:
	"""Create or return a project-scoped collection for a user."""
	client = get_chroma_client()
	return client.get_or_create_collection(
		name=_build_collection_name(user_id=user_id, project_id=project_id),
		metadata={"hnsw:space": "cosine"},
	)


def get_collection(user_id: int, project_id: int) -> Any:
	"""Get a collection for retrieval and indexing."""
	return create_collection(user_id=user_id, project_id=project_id)


def add_documents(
	user_id: int,
	project_id: int,
	document_id: int,
	chunks: list[dict[str, Any]],
	embeddings: list[list[float]],
) -> int:
	"""Store document chunks and embeddings with rich metadata."""
	if len(chunks) != len(embeddings):
		raise ValueError("Chunks and embeddings must have the same length")
	if not chunks:
		return 0

	collection = get_collection(user_id=user_id, project_id=project_id)
	ids = [chunk["chunk_id"] for chunk in chunks]
	documents = [chunk["chunk_text"] for chunk in chunks]
	metadatas = [
		{
			"user_id": user_id,
			"project_id": project_id,
			"document_id": document_id,
			"chunk_id": chunk["chunk_id"],
			"page_number": chunk["page_number"],
			"chunk_index": chunk["chunk_index"],
			"chunk_text": chunk["chunk_text"],
		}
		for chunk in chunks
	]

	collection.upsert(
		ids=ids,
		documents=documents,
		embeddings=embeddings,
		metadatas=metadatas,
	)
	return len(chunks)


def has_document_vectors(user_id: int, project_id: int, document_id: int) -> bool:
	"""Check whether document vectors are already present in the collection."""
	collection = get_collection(user_id=user_id, project_id=project_id)
	result = collection.get(where={"document_id": document_id}, limit=1)
	ids = result.get("ids") or []
	return len(ids) > 0


def delete_document_vectors(user_id: int, project_id: int, document_id: int) -> None:
	"""Delete all vectors for one document."""
	collection = get_collection(user_id=user_id, project_id=project_id)
	collection.delete(where={"document_id": document_id})


def delete_project_vectors(user_id: int, project_id: int) -> None:
	"""Delete all vectors for one project in the user's collection."""
	client = get_chroma_client()
	collection_name = _build_collection_name(user_id=user_id, project_id=project_id)
	try:
		client.delete_collection(name=collection_name)
	except Exception:
		return


def similarity_search(
	user_id: int,
	project_id: int,
	query_embedding: list[float],
	top_k: int = 5,
) -> list[dict[str, Any]]:
	"""Run semantic similarity search and return normalized results."""
	collection = get_collection(user_id=user_id, project_id=project_id)
	result = collection.query(
		query_embeddings=[query_embedding],
		n_results=top_k,
		where={"user_id": user_id, "project_id": project_id},
	)

	documents = result.get("documents", [[]])[0]
	metadatas = result.get("metadatas", [[]])[0]
	distances = result.get("distances", [[]])[0]

	items: list[dict[str, Any]] = []
	for index in range(len(documents)):
		distance = distances[index] if index < len(distances) else None
		score = None if distance is None else 1.0 / (1.0 + float(distance))
		metadata = metadatas[index] if index < len(metadatas) else {}
		items.append(
			{
				"document_id": metadata.get("document_id"),
				"chunk_id": metadata.get("chunk_id"),
				"page_number": metadata.get("page_number"),
				"chunk_index": metadata.get("chunk_index"),
				"chunk_text": documents[index],
				"score": score,
			}
		)

	return items

