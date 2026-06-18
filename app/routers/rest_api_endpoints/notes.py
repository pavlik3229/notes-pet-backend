import logging

from fastapi import APIRouter, BackgroundTasks, status, Depends

from app.backgroung_tasks.upload_notes import run_note_ai_enrichment
from app.llms.enrichment_pipeline import NoteEnrichPipe
from app.repos.notes import NotesRepo
from app.schemas import NoteCreate, NoteOut
from app.schemas.notes import NoteUpdatePayload
from app.services.notes import NotesService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/notes', status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    background_tasks: BackgroundTasks,
    service: NotesService = Depends(),
    ai_pipeline: NoteEnrichPipe = Depends(),
    notes_repo: NotesRepo = Depends(),
):
    logger.info('Record received')
    result = await service.create_note(note)

    logger.info('Adding enrichment task to background tasks')
    background_tasks.add_task(run_note_ai_enrichment, result, notes_repo, ai_pipeline)
    return {
        'doc_id': result.doc_id,
        'status': 'pending',
        'message': 'Enrichment started',
    }


@router.get('/notes', response_model=NoteOut)
async def get_note(note_id: str, service: NotesService = Depends()):
    result = await service.get_note(note_id)

    return result


@router.patch('/notes', response_model=NoteOut)
async def update_note(
    update_data: NoteUpdatePayload,
    background_tasks: BackgroundTasks,
    service: NotesService = Depends(),
    ai_pipeline: NoteEnrichPipe = Depends(),
    notes_repo: NotesRepo = Depends(),
):
    logger.debug(f'Update data received for note with id {update_data.note_id}')

    result = await service.update_note(
        note_id=update_data.note_id,
        title=update_data.title,
        content=update_data.content,
    )

    logger.info('Adding enrichment task to background tasks')

    background_tasks.add_task(run_note_ai_enrichment, result, notes_repo, ai_pipeline)
    return {
        'doc_id': result.doc_id,
        'status': 'pending',
        'message': 'Enrichment started',
    }



@router.delete('/notes', status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str, service: NotesService = Depends()):
    await service.delete_note(note_id)
