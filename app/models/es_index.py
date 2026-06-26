from .note_mapping import mapping as note_mapping
from ..core.config import config
from ..core.elastic_context import es_client as es


async def create_index():
    await es.indices.create(
        index=config.NOTES_INDEX_NAME, settings=index_settings, mappings=note_mapping
    )


index_settings = {
    'number_of_shards': 1,
    'number_of_replicas': 1,
    'analysis': {
        'analyzer': {
            'ru_eng_analyzer': {
                'tokenizer': 'standard',
                'filter': ['lowercase', 'en_stemmer', 'ru_stemmer'],
            }
        },
        'filter': {
            'en_stemmer': {'type': 'stemmer', 'language': 'english'},
            'ru_stemmer': {'type': 'stemmer', 'language': 'russian'},
        },
    },
}
