import logging, uuid
from app.core.config import get_settings
from app.db.models import Item, Chunk
from app.services.chunking import chunk_text
from app.services.ai import embed_texts
from app.services.url_fetch import fetch_url_text

logger = logging.getLogger("ingestion")

async def create_item(session, source_type: str, content: str = "", url: str | None = None):
    item = Item(id=str(uuid.uuid4()), source_type=source_type,
        title=(" ".join(content.split())[:72] if source_type == "note" else (url or "Web page")) or "Untitled note",
        source_url=url, raw_content=content if source_type == "note" else "", status="processing")
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def process_item(item_id: str, session_factory):
    settings = get_settings()
    async with session_factory() as session:
        item = await session.get(Item, item_id)
        if item is None:
            return
        try:
            if item.source_type == "url":
                title, content = await fetch_url_text(item.source_url or "")
                item.title, item.raw_content = title, content
            else:
                content = item.raw_content
            pieces = chunk_text(content, settings.chunk_size, settings.chunk_overlap)
            if not pieces:
                raise ValueError("No usable text was found to index")
            vectors = await embed_texts(pieces)
            for idx, (piece, vector) in enumerate(zip(pieces, vectors)):
                session.add(Chunk(id=str(uuid.uuid4()), item_id=item.id, chunk_index=idx, content=piece, embedding=vector))
            item.status, item.error_message = "ready", None
            await session.commit()
            logger.info("ingestion_complete item_id=%s chunks=%s", item.id, len(pieces))
        except Exception as exc:
            await session.rollback()
            item = await session.get(Item, item_id)
            if item:
                item.status, item.error_message = "failed", str(exc)[:500]
                await session.commit()
            logger.exception("ingestion_failed item_id=%s", item_id)
