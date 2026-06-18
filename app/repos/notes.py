import logging

from elasticsearch import Elasticsearch
from fastapi.params import Depends

from app.core.config import get_config, Config
from app.core.elastic_context import get_es
from app.schemas import NotePreAiDTO
from app.schemas.notes import NotePostAiDTO

logger = logging.getLogger(__name__)


class NotesRepo:
    def __init__(
        self, config: Config = Depends(get_config), db: Elasticsearch = Depends(get_es)
    ):
        self.config = config
        self.db = db

    async def save_doc(self, note: NotePreAiDTO | NotePostAiDTO) -> bool:

        note_data, doc_id = self._create_json_body(note)

        bd_response = await self.db.index(
            index=self.config.NOTES_INDEX_NAME, id=doc_id, body=note_data
        )
        logger.info(f'Record with id {note.doc_id} saved to database')

        return bd_response.body['result'] == 'created'

    async def get_doc(self, doc_id: str):

        doc = await self.db.get(index=self.config.NOTES_INDEX_NAME, id=doc_id)

        doc_json = doc.body

        return doc_json['_id'], doc_json['_source']

    async def update_doc(self, doc_id: str, note_data: dict) -> bool:

        bd_response = await self.db.update(
            index=self.config.NOTES_INDEX_NAME, id=doc_id, body={'doc': note_data}
        )
        logger.info(f'Record with id {doc_id} updated in database')

        return bd_response.body['result'] == 'updated'

    async def get_all_notes(self) -> list[dict]:
        response = await self.db.search(
            index=self.config.NOTES_INDEX_NAME,
            body={'query': {'match_all': {}}},
            size=100,
        )

        results = []
        for hit in response.body['hits']['hits']:
            doc = hit['_source']
            doc['doc_id'] = hit['_id']
            results.append(doc)
        return results

    async def delete_doc(self, doc_id: str) -> bool:
        bd_response = await self.db.delete(
            index=self.config.NOTES_INDEX_NAME, id=doc_id
        )

        logger.info(f'Record with id {doc_id} deleted from database')

        return bd_response.body['result'] == 'deleted'

    def _create_json_body(self, note: NotePreAiDTO | NotePostAiDTO):
        return note.model_dump(exclude={'doc_id'}), note.doc_id
