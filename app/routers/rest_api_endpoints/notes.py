import logging

from fastapi import APIRouter, BackgroundTasks, status, Depends

from app.backgroung_tasks.upload_notes import run_note_ai_enrichment
from app.llms.enrichment_pipeline import NoteEnrichPipe
from app.repos.notes import NotesRepo, get_notes_repo
from app.schemas import NoteCreate, NoteOut
from app.schemas.notes import NoteUpdatePayload, NoteListResponse
from app.services.notes import NotesService, get_notes_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/notes')
async def create_note(
    note: NoteCreate,
    background_tasks: BackgroundTasks,
    service: NotesService = Depends(get_notes_service),
    ai_pipeline: NoteEnrichPipe = Depends(NoteEnrichPipe),
    notes_repo: NotesRepo = Depends(get_notes_repo),
):
    logger.info('Record received')
    result = await service.create_note(note)

    logger.info('Adding enrichment task to background tasks')
    background_tasks.add_task(run_note_ai_enrichment, result, notes_repo, ai_pipeline)

    return {
        'doc_id': result.doc_id,
        'status': 'pending',
        'message': 'Enrichment started',
        'status_code': status.HTTP_201_CREATED,
    }


@router.get('/notes', response_model=NoteListResponse)
async def get_all_notes(
    limit: int = 20, offset: int = 0, service: NotesService = Depends(get_notes_service)
):
    result = await service.get_all_notes(limit, offset)

    return {
        'count': len(result),
        'notes': result,
    }


@router.get('/notes/search', response_model=NoteListResponse)
async def hybrid_search(
    content: str,
    title: str | None = None,
    limit: int = 20,
    offset: int = 0,
    service: NotesService = Depends(get_notes_service),
):
    result = await service.hybrid_search(title, content, limit, offset)

    return {
        'count': len(result),
        'notes': result,
    }


@router.patch('/notes', response_model=NoteOut)
async def update_note(
    update_data: NoteUpdatePayload,
    background_tasks: BackgroundTasks,
    service: NotesService = Depends(get_notes_service),
    ai_pipeline: NoteEnrichPipe = Depends(NoteEnrichPipe),
    notes_repo: NotesRepo = Depends(get_notes_repo),
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
async def delete_note(note_id: str, service: NotesService = Depends(get_notes_service)):
    await service.delete_note(note_id)


@router.get('/notes/{note_id}', response_model=NoteOut)
async def get_note(note_id: str, service: NotesService = Depends(get_notes_service)):
    result = await service.get_note(note_id)

    return result
