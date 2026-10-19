from app.core.config import get_settings
from app.services.retrieval import retrieve
from app.services.ai import generate_answer

async def answer_question(session, question: str, top_k: int | None = None):
    settings = get_settings()
    matches = await retrieve(session, question, top_k or settings.top_k)
    if not matches:
        return {"answer":"I couldn't find relevant information in your saved knowledge to answer that question.",
                "sources":[], "retrieval_count":0}
    answer = await generate_answer(question, [m["chunk"].content for m in matches])
    sources = []
    for m in matches:
        chunk, item = m["chunk"], m["item"]
        sources.append({"item_id":item.id, "title":item.title, "source_type":item.source_type,
            "source_url":item.source_url, "chunk_id":chunk.id, "snippet":chunk.content[:500],
            "score":round(m["score"],4)})
    return {"answer":answer, "sources":sources, "retrieval_count":len(sources)}
