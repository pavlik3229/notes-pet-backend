from elasticsearch import AsyncElasticsearch

from app.core.config import config

es_client = AsyncElasticsearch(config.ELASTICSEARCH_URL)


async def get_es():
    return es_client
