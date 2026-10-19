from sqlalchemy import select
from app.db.models import Chunk, Item
from app.services.ai import embed_texts

async def retrieve(session, question: str, top_k: int):
    vector = (await embed_texts([question]))[0]
    distance = Chunk.embedding.cosine_distance(vector)
    result = await session.execute(select(Chunk, Item, distance.label("distance"))
        .join(Item, Chunk.item_id == Item.id)
        .where(Item.status == "ready").order_by(distance).limit(top_k))
    matches = []
    for chunk, item, dist in result.all():
        dist = float(dist)
        if dist <= 0.78:
            matches.append({"chunk": chunk, "item": item, "score": max(0.0, min(1.0, 1.0-dist))})
    return matches
