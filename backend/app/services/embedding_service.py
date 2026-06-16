"""Embedding generation and text chunking service."""

from functools import lru_cache
import re

from sentence_transformers import SentenceTransformer

from app.core.config import settings


def _normalize_text(text: str) -> str:
	return " ".join(text.split()).strip()


def chunk_text(
	text: str,
	chunk_size: int | None = None,
	chunk_overlap: int | None = None,
) -> list[str]:
	"""Split text into overlapping chunks suitable for vector storage."""
	size = chunk_size or settings.text_chunk_size
	overlap = settings.text_chunk_overlap if chunk_overlap is None else chunk_overlap

	if size <= 0:
		raise ValueError("chunk_size must be greater than 0")
	if overlap < 0:
		raise ValueError("chunk_overlap cannot be negative")
	if overlap >= size:
		raise ValueError("chunk_overlap must be smaller than chunk_size")

	normalized = _normalize_text(text)
	if not normalized:
		return []

	sentences = [
		sentence.strip()
		for sentence in re.split(r"(?<=[.!?])\s+", normalized)
		if sentence.strip()
	]
	if not sentences:
		return []

	chunks: list[str] = []
	current_chunk_sentences: list[str] = []
	current_length = 0

	for sentence in sentences:
		sentence_length = len(sentence)

		# If one sentence is too long, hard-wrap it by words.
		if sentence_length > size:
			words = sentence.split(" ")
			for word in words:
				candidate = f"{(' '.join(current_chunk_sentences)).strip()} {word}".strip()
				if len(candidate) > size and current_chunk_sentences:
					chunks.append(" ".join(current_chunk_sentences).strip())
					current_chunk_sentences = [word]
					current_length = len(word)
				else:
					current_chunk_sentences.append(word)
					current_length = len(" ".join(current_chunk_sentences))
			continue

		candidate_length = sentence_length if not current_chunk_sentences else current_length + 1 + sentence_length
		if candidate_length <= size:
			current_chunk_sentences.append(sentence)
			current_length = candidate_length
			continue

		chunks.append(" ".join(current_chunk_sentences).strip())

		# Keep trailing sentences up to overlap budget.
		overlap_sentences: list[str] = []
		overlap_length = 0
		for previous_sentence in reversed(current_chunk_sentences):
			added_length = len(previous_sentence) if overlap_length == 0 else overlap_length + 1 + len(previous_sentence)
			if added_length > overlap:
				break
			overlap_sentences.insert(0, previous_sentence)
			overlap_length = added_length

		current_chunk_sentences = overlap_sentences + [sentence]
		current_length = len(" ".join(current_chunk_sentences))

	if current_chunk_sentences:
		chunks.append(" ".join(current_chunk_sentences).strip())

	# Ensure no empty chunks are returned.
	return [chunk for chunk in chunks if chunk]


def build_document_chunks(
	pages: list[dict[str, str | int]],
	document_id: int,
	chunk_size: int | None = None,
	chunk_overlap: int | None = None,
) -> list[dict[str, str | int]]:
	"""Build structured chunk objects with page-aware metadata."""
	chunks: list[dict[str, str | int]] = []
	chunk_index = 0

	for page in pages:
		page_number = int(page["page_number"])
		page_text = str(page["text"])
		for chunk_text_value in chunk_text(
			text=page_text,
			chunk_size=chunk_size,
			chunk_overlap=chunk_overlap,
		):
			chunk_id = f"doc_{document_id}_chunk_{chunk_index}"
			chunks.append(
				{
					"chunk_id": chunk_id,
					"chunk_index": chunk_index,
					"page_number": page_number,
					"chunk_text": chunk_text_value,
				}
			)
			chunk_index += 1

	return chunks


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
	"""Load and cache the embedding model once per process."""
	return SentenceTransformer(settings.embedding_model_name)


def embed_text(text: str) -> list[float]:
	"""Generate an embedding vector for a single text input."""
	normalized = _normalize_text(text)
	if not normalized:
		raise ValueError("Text to embed cannot be empty")

	model = get_embedding_model()
	vector = model.encode(normalized, convert_to_numpy=True)
	return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
	"""Generate embedding vectors for a batch of text inputs."""
	normalized_texts: list[str] = []
	for text in texts:
		normalized = _normalize_text(text)
		if normalized:
			normalized_texts.append(normalized)
	if not normalized_texts:
		return []

	model = get_embedding_model()
	vectors = model.encode(normalized_texts, convert_to_numpy=True)
	return vectors.tolist()

