from fastapi import Depends
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.core.config import get_config
from app.core.gemini_client import get_text_model, get_embedding_model
from app.schemas import NotePreAiDTO
from app.schemas.notes import NotePostAiDTO, SummaryResponse

logger = logging.getLogger(__name__)
config = get_config()


class NoteEnrichPipe:
    def __init__(
        self,
        text_model: ChatGoogleGenerativeAI = Depends(get_text_model),
        embedding_model: GoogleGenerativeAIEmbeddings = Depends(get_embedding_model),
    ):
        self.config = config
        self.text_model = text_model
        self.embedding_model = embedding_model

    async def process(self, note: NotePreAiDTO) -> NotePostAiDTO:
        logger.info(f'Starting enrichment for note with id {note.doc_id}')

        summary = None
        tags = None
        embedding = None

        if len(note.content) > self.config.MIN_CONTENT_LENGTH_FOR_AI_ENRICHMENT:
            summary = await self._summary(note)
            logger.info(f'Summary generated for note with id {note.doc_id}')

        embedding = await self._add_embedding(note)
        logger.info(f'Embedding generated for note with id {note.doc_id}')

        enriched_note = NotePostAiDTO(
            **note.model_dump(),
            summary=summary,
            tags=tags,
            embedding=embedding,
        )

        return enriched_note

    async def _summary(self, note: NotePreAiDTO) -> str | None:
        structured_llm = self.text_model.with_structured_output(
            SummaryResponse, method='json_schema'
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    config.SUMMARY_PROMPT,
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

    async def _add_embedding(self, note: NotePreAiDTO) -> list | None:
        try:
            result = self.embedding_model.embed_query(
                text=note.content, title=note.title
            )
            logger.info(f'Embedding generated for note with id {note.doc_id}')
            return result
        except Exception as e:
            logger.error(
                f'Failed to generate embedding for note with id {note.doc_id}. Error: {str(e)}'
            )
            return None
