"""Planner node for constructing a simple research plan."""

import re

from app.graphs.state import ResearchState, ResearchWorkflowValidationError


_STOP_WORDS = {
	"about",
	"after",
	"also",
	"because",
	"between",
	"could",
	"does",
	"from",
	"have",
	"into",
	"limitations",
	"models",
	"paper",
	"should",
	"that",
	"their",
	"there",
	"these",
	"what",
	"when",
	"where",
	"which",
	"with",
}


def planner_node(state: ResearchState) -> dict[str, object]:
	query = str(state.get("query", "")).strip()
	if not query:
		raise ResearchWorkflowValidationError("Query cannot be empty")

	terms = [
		token
		for token in re.findall(r"[a-z0-9]+", query.lower())
		if len(token) > 2 and token not in _STOP_WORDS
	]
	key_topics = list(dict.fromkeys(terms))[:6]

	plan = {
		"objective": f"Answer the research question: {query}",
		"key_topics": key_topics,
		"steps": [
			"Retrieve the most relevant project document chunks",
			"Synthesize a grounded answer from retrieved context",
			"Critique the answer for unsupported claims",
			"Attach citations and return a final structured response",
		],
	}

	return {"research_plan": plan}

