import logging

from app.llms.enrichment_pipeline import NoteEnrichPipe
from app.repos.notes import NotesRepo
from app.schemas import NotePreAiDTO

logger = logging.getLogger(__name__)


async def run_note_ai_enrichment(
    note: NotePreAiDTO,
    notes_repo: NotesRepo,
    ai_pipeline: NoteEnrichPipe,
):
    enriched_note = await ai_pipeline.process(note)
    logger.info(f'Enrichment completed for note with id {note.doc_id}')

    await notes_repo.save_doc(enriched_note)
