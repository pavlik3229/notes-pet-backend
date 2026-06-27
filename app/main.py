import logging

from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from .core.config import config
from app.routers.rest_api_endpoints.notes import router as note_router
from app.logging import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


origins = [
    config.FRONTEND_URL,
]

api_router = APIRouter()
api_router.include_router(note_router)

app = FastAPI(debug=config.DEBUG)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(api_router, prefix='/ai')
