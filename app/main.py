from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import weather, history, stats
from app.db.database import engine, Base


app = FastAPI()
app.include_router(weather.router)
app.include_router(stats.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(weather.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
