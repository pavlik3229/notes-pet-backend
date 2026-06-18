import datetime

import strawberry
import typing

from app.schemas import NoteCreate
from app.services.notes import NotesService

notes_service = NotesService()


@strawberry.type
class NoteType:
    doc_id: str
    title: str
    content: str
    summary: str | None
    tags: list | None
    created_at: datetime.datetime


@strawberry.type
class Query:
    @strawberry.field
    async def note(self, doc_id: str) -> NoteType:
        note_data = await notes_service.get_note(doc_id)

        created_at_val = note_data.get('created_at')
        if isinstance(created_at_val, str):
            created_at_val = datetime.datetime.fromisoformat(
                created_at_val.replace('Z', '+00:00')
            )

        return NoteType(
            doc_id=note_data['doc_id'],
            title=note_data['title'],
            content=note_data['content'],
            summary=note_data.get('summary'),
            tags=note_data.get('tags'),
            created_at=created_at_val,
        )

    @strawberry.field
    async def notes(self) -> typing.List[NoteType]:
        notes_data = await notes_service.get_all_notes()

        result = []
        for note in notes_data:
            created_at_val = note.get('created_at')
            if isinstance(created_at_val, str):
                created_at_val = datetime.datetime.fromisoformat(
                    created_at_val.replace('Z', '+00:00')
                )

            result.append(
                NoteType(
                    doc_id=note['doc_id'],
                    title=note['title'],
                    content=note['content'],
                    summary=note.get('summary'),
                    tags=note.get('tags'),
                    created_at=created_at_val,
                )
            )

        return result


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_note(self, title: str | None, content: str) -> NoteType:
        note_create = NoteCreate(title=title, content=content)
        note_pre_ai = await notes_service.create_note(note_create)
        return NoteType(
            doc_id=note_pre_ai.doc_id,
            title=note_pre_ai.title,
            content=note_pre_ai.content,
            summary=None,
            tags=None,
            created_at=note_pre_ai.created_at,
        )

    @strawberry.mutation
    async def update_note(
        self, doc_id: str, title: str | None = None, content: str | None = None
    ) -> NoteType:
        updated_note = await notes_service.update_note(doc_id, title, content)
        # Note: dict is returned from service, we convert datetimes appropriately if string
        created_at_val = updated_note.get('created_at')
        if isinstance(created_at_val, str):
            created_at_val = datetime.datetime.fromisoformat(
                created_at_val.replace('Z', '+00:00')
            )

        return NoteType(
            doc_id=updated_note['doc_id'],
            title=updated_note['title'],
            content=updated_note['content'],
            summary=updated_note.get('summary'),
            tags=updated_note.get('tags'),
            created_at=created_at_val,
        )

    @strawberry.mutation
    async def delete_note(self, doc_id: str) -> bool:
        # Implement logic to delete a note from the database
        result = await notes_service.delete_note(doc_id)
        return result
