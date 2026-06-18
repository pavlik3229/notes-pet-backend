import logging

from fastapi import APIRouter, FastAPI

from .core.config import config
from app.routers.rest_api_endpoints.notes import router as note_router
from app.logging import setup_logging

logger = logging.getLogger(__name__)
setup_logging()
app = FastAPI(debug=config.DEBUG)


api_router = APIRouter()
api_router.include_router(note_router)
app.include_router(api_router, prefix='/ai')
