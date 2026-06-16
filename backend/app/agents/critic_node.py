"""Critic node for evaluating groundedness and support quality."""

from app.graphs.state import ResearchState, ResearchWorkflowValidationError
from app.services.gemini_service import GeminiServiceError, generate_answer


_CRITIC_SYSTEM_PROMPT = """
You are a strict research answer critic.

Rules:
1. Evaluate whether the answer is supported by the provided context only.
2. Flag unsupported or weakly supported claims.
3. Keep critique concise.
4. Return plain text with: Verdict, Strengths, Risks.
""".strip()


def critic_node(state: ResearchState) -> dict[str, object]:
	query = str(state.get("query", "")).strip()
	answer = str(state.get("generated_answer", "")).strip()
	retrieved_chunks = list(state.get("retrieved_chunks") or [])

	if not answer:
		raise ResearchWorkflowValidationError("No generated answer available for critique")
	if not retrieved_chunks:
		raise ResearchWorkflowValidationError("No retrieved chunks available for critique")

	context_lines: list[str] = []
	for index, chunk in enumerate(retrieved_chunks, start=1):
		chunk_id = str(chunk.get("chunk_id") or f"chunk_{index}")
		chunk_text = str(chunk.get("chunk_text") or "").strip()
		if chunk_text:
			context_lines.append(f"[{chunk_id}] {chunk_text}")

	context = "\n\n".join(context_lines)
	critic_prompt = (
		f"Question:\n{query}\n\n"
		f"Answer:\n{answer}\n\n"
		f"Context:\n{context}\n\n"
		"Review the answer against context only."
	)

	try:
		critique = generate_answer(
			system_prompt=_CRITIC_SYSTEM_PROMPT,
			user_prompt=critic_prompt,
			temperature=0.0,
		)
	except GeminiServiceError as exc:
		raise ResearchWorkflowValidationError(str(exc)) from exc

	return {"critique": critique}

