from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from static_pages.router import static_pages_router

load_dotenv()

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static_pages/static"), name="static")

app.include_router(static_pages_router, tags=["pages"], prefix="")
