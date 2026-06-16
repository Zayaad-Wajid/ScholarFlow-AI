"""LangGraph orchestration for the research workflow."""

from sqlalchemy.orm import Session
from langgraph.graph import END, START, StateGraph

from app.agents.citation_node import citation_node
from app.agents.critic_node import critic_node
from app.agents.document_node import retrieval_node
from app.agents.planner_node import planner_node
from app.agents.rag_node import answer_generation_node
from app.agents.report_node import final_response_node
from app.graphs.state import (
	ResearchState,
	ResearchWorkflowExecutionError,
	ResearchWorkflowNotFoundError,
	ResearchWorkflowValidationError,
)


def build_research_graph(db: Session):
	workflow = StateGraph(ResearchState)

	workflow.add_node("planner", planner_node)
	workflow.add_node("retriever", lambda state: retrieval_node(state, db=db))
	workflow.add_node("answer_generator", answer_generation_node)
	workflow.add_node("critic", critic_node)
	workflow.add_node("citation_builder", citation_node)
	workflow.add_node("final_response", final_response_node)

	workflow.add_edge(START, "planner")
	workflow.add_edge("planner", "retriever")
	workflow.add_edge("retriever", "answer_generator")
	workflow.add_edge("answer_generator", "critic")
	workflow.add_edge("critic", "citation_builder")
	workflow.add_edge("citation_builder", "final_response")
	workflow.add_edge("final_response", END)

	return workflow.compile()


def run_research_workflow(
	db: Session,
	user_id: int,
	project_id: int,
	query: str,
	top_k: int = 5,
) -> dict[str, object]:
	graph = build_research_graph(db=db)
	initial_state: ResearchState = {
		"user_id": user_id,
		"project_id": project_id,
		"query": query,
		"metadata": {"top_k": top_k},
	}

	try:
		final_state = graph.invoke(initial_state)
	except (ResearchWorkflowNotFoundError, ResearchWorkflowValidationError):
		raise
	except Exception as exc:
		raise ResearchWorkflowExecutionError("LangGraph execution failed") from exc

	final_response = final_state.get("final_response")
	if not isinstance(final_response, dict):
		raise ResearchWorkflowExecutionError("Workflow did not produce a final response")

	return final_response

