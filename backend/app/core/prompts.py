"""Prompt templates for research assistant agents."""

RAG_SYSTEM_PROMPT = """
You are a research assistant.

Rules:
1. Answer ONLY using the provided context.
2. Do NOT invent facts, numbers, or claims.
3. If the context does not contain the answer, say that the information is not available in the provided documents.
4. Keep the answer concise and accurate.
5. Cite supporting chunk IDs in square brackets when possible, like [doc_1_chunk_4].
""".strip()

REPORT_SYSTEM_PROMPT = """
You are ScholarFlow AI's report writer.

Rules:
1. Use only the provided project context.
2. Do not invent claims, citations, or references.
3. When evidence is limited or mixed, explicitly say so.
4. Organize the response into clear section headings.
5. Keep the writing practical, grounded, and suitable for students or researchers.
6. Refer only to the supplied source references and context.
""".strip()

_REPORT_SECTION_GUIDANCE = {
    "summary": [
        "Title",
        "Topic",
        "Executive Summary",
        "Main Points",
        "Sources Used",
        "Conclusion",
    ],
    "literature_review": [
        "Title",
        "Topic",
        "Introduction",
        "Existing Research",
        "Key Findings",
        "Limitations",
        "Conclusion",
        "References",
    ],
    "key_findings": [
        "Title",
        "Topic",
        "Findings List",
        "Supporting Evidence",
        "Conclusion",
    ],
}


def build_rag_user_prompt(context: str, question: str) -> str:
    return (
        "Context:\n"
        f"{context}\n\n"
        "Question:\n"
        f"{question}\n\n"
        "Answer using only the context above."
    )


def build_report_user_prompt(
    report_type: str,
    project_title: str,
    topic: str,
    context: str,
    sources: list[str],
) -> str:
    sections = _REPORT_SECTION_GUIDANCE.get(report_type, _REPORT_SECTION_GUIDANCE["summary"])
    sections_text = "\n".join(f"- {section}" for section in sections)
    sources_text = "\n".join(f"- {source}" for source in sources) if sources else "- No explicit source metadata available"
    report_label = report_type.replace("_", " ")

    return (
        f"Project Title:\n{project_title}\n\n"
        f"Requested Report Type:\n{report_label}\n\n"
        f"Requested Topic:\n{topic}\n\n"
        "Required Sections:\n"
        f"{sections_text}\n\n"
        "Available Source References:\n"
        f"{sources_text}\n\n"
        "Grounding Context:\n"
        f"{context}\n\n"
        "Instructions:\n"
        "- Write a complete report using only the grounding context above.\n"
        "- Keep all claims tied to the supplied material.\n"
        "- If evidence is weak, partial, or absent, state that plainly.\n"
        "- Do not fabricate references or external knowledge.\n"
        "- Make section headings explicit and readable.\n"
    )
