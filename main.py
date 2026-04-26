from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.routers import upload, analyze

settings = get_settings()

app = FastAPI(
    title="AI Resume Analyzer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analyze.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "AI Resume Analyzer"}


@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}