"""Chroma vector store service."""

from functools import lru_cache
from pathlib import Path
import re
from typing import Any

import chromadb

from app.core.config import settings


class ChromaServiceError(Exception):
	"""Raised when ChromaDB operations fail."""


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
	try:
		client = get_chroma_client()
		return client.get_or_create_collection(
			name=_build_collection_name(user_id=user_id, project_id=project_id),
			metadata={"hnsw:space": "cosine"},
		)
	except Exception as exc:
		raise ChromaServiceError("Failed to create or open Chroma collection") from exc


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

	ids = [str(chunk["chunk_id"]) for chunk in chunks]
	documents = [str(chunk["chunk_text"]) for chunk in chunks]
	metadatas = [
		{
			"user_id": int(user_id),
			"project_id": int(project_id),
			"document_id": int(document_id),
			"chunk_id": str(chunk["chunk_id"]),
			"page_number": int(chunk["page_number"]),
			"chunk_index": int(chunk["chunk_index"]),
			"chunk_text": str(chunk["chunk_text"]),
		}
		for chunk in chunks
	]

	try:
		collection = get_collection(user_id=user_id, project_id=project_id)
		collection.upsert(
			ids=ids,
			documents=documents,
			embeddings=embeddings,
			metadatas=metadatas,
		)
	except Exception as exc:
		raise ChromaServiceError("Failed to store vectors in ChromaDB") from exc
	return len(chunks)


def has_document_vectors(user_id: int, project_id: int, document_id: int) -> bool:
	"""Check whether document vectors are already present in the collection."""
	try:
		collection = get_collection(user_id=user_id, project_id=project_id)
		result = collection.get(where={"document_id": int(document_id)}, limit=1)
		ids = result.get("ids") or []
		return len(ids) > 0
	except Exception as exc:
		raise ChromaServiceError("Failed to check existing vectors") from exc


def delete_document_vectors(user_id: int, project_id: int, document_id: int) -> None:
	"""Delete all vectors for one document."""
	try:
		collection = get_collection(user_id=user_id, project_id=project_id)
		collection.delete(where={"document_id": int(document_id)})
	except Exception as exc:
		raise ChromaServiceError("Failed to delete document vectors") from exc


def delete_project_vectors(user_id: int, project_id: int) -> None:
	"""Delete all vectors for one project in the user's collection."""
	try:
		client = get_chroma_client()
		collection_name = _build_collection_name(user_id=user_id, project_id=project_id)
		client.delete_collection(name=collection_name)
	except Exception as exc:
		raise ChromaServiceError("Failed to delete project vector collection") from exc


def similarity_search(
	user_id: int,
	project_id: int,
	query_embedding: list[float],
	top_k: int = 5,
	query_text: str | None = None,
) -> list[dict[str, Any]]:
	"""Run semantic similarity search and return normalized results."""
	if not query_embedding:
		raise ValueError("Query embedding cannot be empty")
	if top_k <= 0:
		raise ValueError("top_k must be greater than 0")

	try:
		collection = get_collection(user_id=user_id, project_id=project_id)
		result = collection.query(
			query_embeddings=[query_embedding],
			n_results=top_k,
			where={
				"$and": [
					{"user_id": int(user_id)},
					{"project_id": int(project_id)},
				]
			},
		)
	except Exception as exc:
		raise ChromaServiceError("Failed to run similarity search") from exc

	documents = result.get("documents", [[]])[0]
	metadatas = result.get("metadatas", [[]])[0]
	distances = result.get("distances", [[]])[0]

	items: list[dict[str, Any]] = []
	query_terms: set[str] = set()
	if query_text:
		query_terms = {
			term
			for term in re.findall(r"[a-z0-9]+", query_text.lower())
			if len(term) > 2
		}

	for index in range(len(documents)):
		distance = distances[index] if index < len(distances) else None
		semantic_score = None if distance is None else 1.0 / (1.0 + float(distance))
		metadata = metadatas[index] if index < len(metadatas) else {}
		chunk_text = str(documents[index])

		lexical_score = 0.0
		if query_terms and chunk_text:
			chunk_terms = {
				term
				for term in re.findall(r"[a-z0-9]+", chunk_text.lower())
				if len(term) > 2
			}
			if chunk_terms:
				lexical_score = len(query_terms & chunk_terms) / len(query_terms)

		if semantic_score is None:
			score = lexical_score
		else:
			# Keep semantic ranking primary, with a small lexical boost for precision.
			score = (semantic_score * 0.85) + (lexical_score * 0.15)

		items.append(
			{
				"document_id": metadata.get("document_id"),
				"chunk_id": metadata.get("chunk_id"),
				"page_number": metadata.get("page_number"),
				"chunk_index": metadata.get("chunk_index"),
				"chunk_text": chunk_text,
				"score": score,
			}
		)

	items.sort(key=lambda item: float(item.get("score") or 0.0), reverse=True)

	return items

