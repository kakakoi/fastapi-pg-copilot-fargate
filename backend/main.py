from typing import List
from distutils.util import strtobool

import sqlalchemy

from fastapi import FastAPI
from pydantic import BaseModel

from backend.db import metadata, database, engine, TESTING, message

app = FastAPI()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, server_default="blank"),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
)


if TESTING:
    metadata.drop_all(engine)
metadata.create_all(engine)

class NoteIn(BaseModel):
    title: str
    text: str
    completed: bool


class Note(BaseModel):
    id: int
    title: str
    text: str
    completed: bool

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/notes/", response_model=List[Note])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@app.post("/notes/", response_model=Note)
async def create_note(note: NoteIn):
    query = notes.insert().values(text=note.text, title=note.title, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

@app.get("/")
async def root():
    return {"message": message}
