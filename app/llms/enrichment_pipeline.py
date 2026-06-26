from fastapi import Depends
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_config
from app.core.gemini_client import get_llm
from app.schemas import NotePreAiDTO
from app.schemas.notes import NotePostAiDTO, SummaryResponse

logger = logging.getLogger(__name__)
config = get_config()


class NoteEnrichPipe:
    def __init__(self, llm_client: ChatGoogleGenerativeAI = Depends(get_llm)):
        self.config = config
        self.llm_client = llm_client

    async def process(self, note: NotePreAiDTO) -> NotePostAiDTO:
        logger.info(f'Starting enrichment for note with id {note.doc_id}')

        summary = None
        tags = None
        embedding = None

        if len(note.content) > self.config.MIN_CONTENT_LENGTH_FOR_AI_ENRICHMENT:
            summary = await self._summary(note)
            logger.info(f'Summary generated for note with id {note.doc_id}')

        enriched_note = NotePostAiDTO(
            **note.model_dump(),
            summary=summary,
            tags=tags,
            embedding=embedding,
        )

        return enriched_note

    async def _summary(self, note: NotePreAiDTO) -> str | None:
        structured_llm = self.llm_client.with_structured_output(
            SummaryResponse, method='json_schema'
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    "Ты просто машина которая должна сделать короткое summary из данного текста. Отвечай максимально емко. Твой ответ в поле 'summary' должен быть ОКОЛО 60 символов.",
                ),
                ('human', '{content}'),
            ]
        )

        chain = prompt | structured_llm

        try:
            result = chain.invoke({'content': note.content})
            logger.info(f'Summary generated for note with id {note.doc_id}')
            return result.summary
        except Exception as e:
            logger.error(
                f'Failed to generate summary for note with id {note.doc_id}. Error: {str(e)}'
            )
            return None
