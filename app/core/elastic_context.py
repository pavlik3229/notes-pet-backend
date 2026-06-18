from typing import AsyncGenerator

from elasticsearch import AsyncElasticsearch
from app.core.config import config


async def get_es() -> AsyncGenerator[AsyncElasticsearch, None]:
    """
    Dependency function to provide an instance of AsyncElasticsearch for interacting with Elasticsearch.
    """
    es = AsyncElasticsearch(config.ELASTICSEARCH_URL)
    try:
        yield es
    finally:
        await es.close()
