from functools import lru_cache

from pydantic_settings import SettingsConfigDict, BaseSettings


class Config(BaseSettings):
    DEBUG: bool = True

    FRONTEND_URL: str = 'http://localhost:5173'

    GOOGLE_AI_API_KEY: str | None = None
    PROJECT_NAME: str
    PROJECT_NUMBER: str

    ELASTICSEARCH_URL: str = 'http://localhost:9200'
    NOTES_INDEX_NAME: str = 'notes'

    MIN_CONTENT_LENGTH_FOR_AI_ENRICHMENT: int = 100

    SUMMARY_PROMPT: str = (
        'Ты просто машина которая должна сделать короткое summary из данного текста. Отвечай максимально емко. '
        'Ты должен давать ответ на русском если в заметке преобладает русский и на английском если преобладает английский. '
        "Твой ответ в поле 'summary' должен быть ОКОЛО 60 символов."
    )

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache
def get_config() -> Config:
    return Config()


config = get_config()
