"""Answer generation node for grounded responses."""

from app.core.prompts import RAG_SYSTEM_PROMPT, build_rag_user_prompt
from app.graphs.state import ResearchState, ResearchWorkflowValidationError
from app.services.gemini_service import GeminiServiceError, generate_answer


def _build_context(chunks: list[dict[str, object]]) -> str:
	parts: list[str] = []
	for index, chunk in enumerate(chunks, start=1):
		chunk_id = str(chunk.get("chunk_id") or f"chunk_{index}")
		page_number = chunk.get("page_number")
		page_label = f"page {page_number}" if page_number is not None else "page unknown"
		chunk_text = str(chunk.get("chunk_text") or "").strip()
		if chunk_text:
			parts.append(f"[Source {index} | {chunk_id} | {page_label}]\n{chunk_text}")
	return "\n\n".join(parts)


def answer_generation_node(state: ResearchState) -> dict[str, object]:
	query = str(state.get("query", "")).strip()
	retrieved_chunks = list(state.get("retrieved_chunks") or [])
	research_plan = state.get("research_plan") or {}

	if not query:
		raise ResearchWorkflowValidationError("Query cannot be empty")
	if not retrieved_chunks:
		raise ResearchWorkflowValidationError("No retrieval context available for answer generation")

	context = _build_context(retrieved_chunks)
	if not context:
		raise ResearchWorkflowValidationError("Retrieved context is empty")

	objective = str((research_plan or {}).get("objective", "")).strip()
	augmented_question = query if not objective else f"{query}\n\nResearch objective: {objective}"

	try:
		answer = generate_answer(
			system_prompt=RAG_SYSTEM_PROMPT,
			user_prompt=build_rag_user_prompt(context=context, question=augmented_question),
		)
	except GeminiServiceError as exc:
		raise ResearchWorkflowValidationError(str(exc)) from exc

	return {"generated_answer": answer}

