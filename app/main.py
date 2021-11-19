from fastapi import FastAPI, Response, status, Depends, Query, File, UploadFile
from typing import Optional, List, Generator
from starlette.responses import FileResponse

from . import actions
from . import models
from .db.session import SessionLocal
from sqlalchemy.orm import Session

# Create all tables in database.
# Comment this out if you using migrations.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get DB session.
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/", tags=['root'])
def root() -> dict:
    return {'status': '200 OK'}


@app.get("/api/get", tags=["Get files"], status_code=status.HTTP_200_OK)
async def root(
        # *,
        response: Response,
        id: Optional[List[int]] = Query(None),
        name: Optional[List[str]] = Query(None),
        tag: Optional[List[str]] = Query(None),
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        db: Session = Depends(get_db)
):
    # All records by default
    query = db.query(models.Image).all()
    files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    if id and not name and not tag:
        query = db.query(models.Image).filter(models.Image.file_id.in_(id)).all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and not tag:
        query = db.query(models.Image).filter(models.Image.file_id.in_(id)) \
            .filter(models.Image.name.in_(name)) \
            .all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and tag:
        query = db.query(models.Image).filter(models.Image.Image.file_id.in_(id)) \
            .filter(models.Image.name.in_(name)) \
            .filter(models.Image.tag.in_(tag)) \
            .all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and not name and tag:
        query = db.query(models.Image).filter(models.Image.file_id.in_(id)) \
            .filter(models.Image.tag.in_(tag)) \
            .all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and tag:
        query = db.query(models.Image).filter(models.Image.name.in_(name)) \
            .filter(models.Image.tag.in_(tag)) \
            .all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and not name and tag:
        query = db.query(models.Image).filter(models.Image.tag.in_(tag)).all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and not tag:
        query = db.query(models.Image).filter(models.Image.name.in_(name)).all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    if len(files_in_db) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'No results =('}

    response.status_code = status.HTTP_200_OK
    return files_in_db
