import logging
from app.core.gemini_client import embedding_model

logger = logging.getLogger(__name__)


async def create_embedding(search_query: str) -> list | None:
    try:
        result = embedding_model.embed_query(text=search_query)
        logger.info(f'Embedding generated for search query: {search_query}')
        return result
    except Exception as e:
        logger.error(
            f'Failed to generate embedding for search query: {search_query}. Error: {str(e)}'
        )
        return None
