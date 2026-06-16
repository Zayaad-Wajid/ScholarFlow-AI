"""Final response node for assembling structured research output."""

from app.graphs.state import ResearchState


def final_response_node(state: ResearchState) -> dict[str, object]:
	research_plan = dict(state.get("research_plan") or {})
	generated_answer = str(state.get("generated_answer") or "")
	critique = str(state.get("critique") or "")
	citations = list(state.get("citations") or [])

	final_response = {
		"research_plan": research_plan,
		"answer": generated_answer,
		"critique": critique,
		"citations": citations,
		"sources_used": len(citations),
	}

	return {"final_response": final_response}

