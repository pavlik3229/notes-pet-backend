import logging

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from app.core.config import get_config
from app.core.elastic_context import get_es
from app.schemas import NotePreAiDTO
from app.schemas.notes import NotePostAiDTO

logger = logging.getLogger(__name__)
config = get_config()


def get_notes_repo(db: AsyncElasticsearch = Depends(get_es)):
    return NotesRepo(db=db)


class NotesRepo:
    def __init__(self, db: AsyncElasticsearch):
        self.config = config
        self.db = db

    async def save_doc(self, note: NotePreAiDTO | NotePostAiDTO) -> bool:
        """Saves a note document to the Elasticsearch index.
        Returns True if the document was created successfully, False otherwise.
        """

        note_data, doc_id = self._create_json_body(note)
        try:
            bd_response = await self.db.index(
                index=self.config.NOTES_INDEX_NAME, id=doc_id, document=note_data
            )
        except Exception as e:
            logger.error(f'Error saving record with id {doc_id} to database: {e}')
            return False

        logger.info(f'Record with id {note.doc_id} saved to database')

        return bd_response.body['result'] in ('created', 'updated')

    async def get_doc(self, doc_id: str) -> tuple[str, dict] | None:
        """Retrieves a note document from the Elasticsearch index by its ID.
        Returns a tuple containing the document ID and the document data if found, or None if not found or an error occurs.
        """

        try:
            doc = await self.db.get(index=self.config.NOTES_INDEX_NAME, id=doc_id)

            doc_json = doc.body
        except NotFoundError:
            logger.warning(f'Record with id {doc_id} not found in database')
            return None

        except Exception as e:
            logger.error(f'Error retrieving record with id {doc_id} from database: {e}')
            return None

        return doc_json['_id'], doc_json['_source']

    async def update_doc(self, doc_id: str, note_data: dict) -> bool:
        """
        Updates a note document in the Elasticsearch index by its ID.
        Returns True if the document was updated successfully,
        False if the document was not found or an error occurs.
        """
        try:
            bd_response = await self.db.update(
                index=self.config.NOTES_INDEX_NAME, id=doc_id, doc=note_data
            )

            logger.info(f'Record with id {doc_id} updated in database')
            return bd_response.body['result'] == 'updated'

        except NotFoundError:
            logger.warning(f'Record with id {doc_id} not found in database for update')
            return False

        except Exception as e:
            logger.error(f'Error updating record with id {doc_id} in database: {e}')
            return False

    async def get_all_notes(self) -> list[dict]:
        """
        Retrieves all note documents from the Elasticsearch index.
        Returns a list of dicts, each containing the document data and its ID under the key 'doc_id'.
        """
        results = []

        try:
            response = await self.db.search(
                index=self.config.NOTES_INDEX_NAME,
                query={'match_all': {}},
                size=100,
            )
            logger.info('All notes retrieved from database successfully')

            for hit in response.body['hits']['hits']:
                doc = hit['_source']
                doc['doc_id'] = hit['_id']
                results.append(doc)
            return results

        except Exception as e:
            logger.error(f'Error retrieving all notes from database: {e}')
            return results

    async def delete_doc(self, doc_id: str) -> bool:
        """
        Deletes a note document from the Elasticsearch index by its ID.
        Returns True if the document was deleted successfully,
        False if the document was not found or an error occurs.
        """
        try:
            bd_response = await self.db.delete(
                index=self.config.NOTES_INDEX_NAME, id=doc_id
            )

            logger.info(f'Record with id {doc_id} deleted from database')
            return bd_response.body['result'] == 'deleted'

        except NotFoundError as e:
            logger.warning(
                f'Record with id {doc_id} not found in database for deletion: {e}'
            )
            return False

        except Exception as e:
            logger.error(f'Error deleting record with id {doc_id} from database: {e}')
            return False

    def _create_json_body(self, note: NotePreAiDTO | NotePostAiDTO) -> tuple[dict, str]:
        """
        Converts a NotePreAiDTO or NotePostAiDTO instance into a JSON-serializable dict for Elasticsearch indexing.
        Returns a tuple containing the dict and the document ID.
        """
        return note.model_dump(exclude={'doc_id'}), note.doc_id
