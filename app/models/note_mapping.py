mapping = {
    'properties': {
        'doc_id': {'type': 'keyword'},
        'title': {'type': 'text', 'analyzer': 'ru_eng_analyzer'},
        'content': {'type': 'text', 'analyzer': 'ru_eng_analyzer'},
        'summary': {'type': 'text', 'analyzer': 'ru_eng_analyzer'},
        'tags': {'type': 'keyword'},
        'embedding': {
            'type': 'dense_vector',
            'dims': 1536,
            'index': True,
            'similarity': 'cosine',
        },
        'created_at': {
            'type': 'date',
            'format': 'yyyy-MM-dd HH:mm:ss||strict_date_optional_time',
        },
    }
}
