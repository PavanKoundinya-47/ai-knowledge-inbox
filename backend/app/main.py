import logging, json, time, uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.db.database import engine, init_db, get_session, SessionLocal
from app.db.models import Item
from app.schemas import IngestRequest, IngestResponse, ItemsResponse, ItemResponse, QueryRequest, QueryResponse
from app.services.ingestion import create_item, process_item
from app.services.rag import answer_question

logging.basicConfig(level=get_settings().log_level.upper(), format="%(message)s")
logger = logging.getLogger("api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()

app = FastAPI(title="Turium AI Knowledge Inbox", version="1.0.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False,
                   allow_methods=["GET","POST","OPTIONS"], allow_headers=["*"])

@app.middleware("http")
async def request_log(request: Request, call_next):
    started = time.perf_counter()
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({"event":"http_request","request_id":request_id,"method":request.method,
        "path":request.url.path,"status_code":response.status_code,
        "duration_ms":round((time.perf_counter()-started)*1000,2)}))
    return response

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.post("/ingest", response_model=IngestResponse, status_code=202)
async def ingest(payload: IngestRequest, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    try:
        payload.validate_payload()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if payload.type == "note":
        item = await create_item(session, "note", content=payload.content or "")
    else:
        item = await create_item(session, "url", url=str(payload.url))
    background_tasks.add_task(process_item, item.id, SessionLocal)
    return IngestResponse(item_id=item.id, status="processing", message="Content accepted for ingestion")

@app.get("/items", response_model=ItemsResponse)
async def list_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item).order_by(Item.created_at.desc()).limit(200))
    return ItemsResponse(items=[ItemResponse.model_validate(i) for i in result.scalars().all()])

@app.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest, session: AsyncSession = Depends(get_session)):
    try:
        return QueryResponse(**(await answer_question(session, payload.question.strip(), payload.top_k)))
    except RuntimeError as exc:
        if "OPENAI_API_KEY" in str(exc) or "OpenAI is not configured" in str(exc):
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        logger.exception("query_configuration_error")
        raise HTTPException(status_code=502, detail="AI provider is unavailable") from exc
    except Exception as exc:
        logger.exception("query_failed")
        raise HTTPException(status_code=502, detail="Unable to answer the question right now. Please try again.") from exc
