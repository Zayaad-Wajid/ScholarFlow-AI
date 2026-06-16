"""Citation node for building source attribution from retrieved chunks."""

from app.graphs.state import ResearchState


def citation_node(state: ResearchState) -> dict[str, object]:
	retrieved_chunks = list(state.get("retrieved_chunks") or [])
	metadata = dict(state.get("metadata") or {})
	document_name_by_id = dict(metadata.get("document_name_by_id") or {})

	citations: list[dict[str, object]] = []
	for chunk in retrieved_chunks:
		document_id = chunk.get("document_id")
		chunk_id = chunk.get("chunk_id")
		if document_id is None or chunk_id is None:
			continue

		citation: dict[str, object] = {
			"document_id": int(document_id),
			"chunk_id": str(chunk_id),
			"page_number": int(chunk["page_number"]) if chunk.get("page_number") is not None else None,
			"similarity_score": float(chunk.get("score") or 0.0),
		}

		document_name = document_name_by_id.get(int(document_id))
		if document_name:
			citation["document_name"] = str(document_name)

		citations.append(citation)

	return {"citations": citations}

