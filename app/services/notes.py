import datetime
import logging
import uuid
from fastapi import Depends

from app.core.config import get_config
from app.repos.notes import NotesRepo, get_notes_repo
from app.schemas import NoteCreate, NotePreAiDTO
from app.schemas.notes import NotePostAiDTO
from app.llms.search_embedding import create_embedding

logger = logging.getLogger(__name__)
config = get_config()


def get_notes_service(
    repo: NotesRepo = Depends(get_notes_repo),
):
    return NotesService(repo=repo)


class NotesService:
    def __init__(self, repo: NotesRepo):
        self.config = config
        self.repo = repo

    async def create_note(self, note: NoteCreate) -> NotePreAiDTO | None:
        note = NotePreAiDTO(
            **note.model_dump(),
            doc_id=self._create_id(),
            created_at=datetime.datetime.now(datetime.UTC),
        )

        logger.info(f'Creating note with id {note.doc_id}')

        if not note.title:
            note.title = note.content[:30] + '...'

        try:
            await self.repo.save_doc(note)
            logger.info(f'Document with id: {note.doc_id} saved successfully')
        except Exception:
            logger.error(f'Failed saving for id: {note.doc_id}')

        return note

    async def get_note(self, note_id: str) -> dict:
        doc_id, doc = await self.repo.get_doc(note_id)

        doc['doc_id'] = doc_id

        return doc

    async def get_all_notes(
        self, limit: int = 20, offset: int = 0
    ) -> list[NotePostAiDTO]:
        return [
            NotePostAiDTO(**doc) for doc in await self.repo.get_all_notes(limit, offset)
        ]

    async def update_note(
        self, note_id: str, title: str | None, content: str | None
    ) -> NotePreAiDTO:
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if content is not None:
            update_data['content'] = content

        await self.repo.update_doc(note_id, update_data)
        note = await self.get_note(note_id)
        note.pop('summary', None)

        return NotePreAiDTO(**note)

    async def delete_note(self, note_id: str) -> bool:
        return await self.repo.delete_doc(note_id)

    async def hybrid_search(
        self, title: str | None, content: str, limit: int = 20, offset: int = 0
    ) -> list[NotePostAiDTO]:
        search_query = title + '. ' + content if title else content
        search_embedding = None
        for i in range(3):
            search_embedding = await create_embedding(search_query)

            logger.info('Performing hybrid search with embedding attempt %d', i + 1)
            if search_embedding is not None:
                logger.info(
                    'Hybrid search embedding created successfully on attempt %d', i + 1
                )
                break

        if search_embedding is None:
            logger.error('Failed to create embedding for search')
            return []

        try:
            docs = await self.repo.hybrid_search(
                search_query=search_query,
                search_embedding=search_embedding,
                limit=limit,
                offset=offset,
            )
        except Exception as e:
            logger.error(f'Hybrid search failed: {e}')
            return []

        return [NotePostAiDTO(**doc) for doc in docs]

    @staticmethod
    def _create_id():
        return str(uuid.uuid7())
