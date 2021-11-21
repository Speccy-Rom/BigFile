from typing import Generator, List, Optional

from fastapi import Depends, FastAPI, File, Query, Response, UploadFile, status
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from . import actions, config, models
from .db.session import SessionLocal

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


@app.get("/", tags=["root"])
def root() -> dict:
    return {"status": "200 OK"}


@app.get("/api/get", tags=["Get files"], status_code=status.HTTP_200_OK)
async def root(
    # *,
    response: Response,
    id: Optional[List[int]] = Query(None),
    name: Optional[List[str]] = Query(None),
    tag: Optional[List[str]] = Query(None),
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db),
):
    # All records by default
    query = db.query(models.Image).all()
    files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    if id and not name and not tag:
        query = db.query(models.Image).filter(models.Image.file_id.in_(id)).all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and not tag:
        query = (
            db.query(models.Image)
            .filter(models.Image.file_id.in_(id))
            .filter(models.Image.name.in_(name))
            .all()
        )
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and tag:
        query = (
            db.query(models.Image)
            .filter(models.Image.Image.file_id.in_(id))
            .filter(models.Image.name.in_(name))
            .filter(models.Image.tag.in_(tag))
            .all()
        )
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and not name and tag:
        query = (
            db.query(models.Image)
            .filter(models.Image.file_id.in_(id))
            .filter(models.Image.tag.in_(tag))
            .all()
        )
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and tag:
        query = (
            db.query(models.Image)
            .filter(models.Image.name.in_(name))
            .filter(models.Image.tag.in_(tag))
            .all()
        )
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and not name and tag:
        query = db.query(models.Image).filter(models.Image.tag.in_(tag)).all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and not tag:
        query = db.query(models.Image).filter(models.Image.name.in_(name)).all()
        files_in_db = actions.get_files_from_db_limit_offset(db, query, limit, offset)

    if len(files_in_db) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No results =("}

    response.status_code = status.HTTP_200_OK
    return files_in_db


@app.post("/api/upload", tags=["Upload"], status_code=status.HTTP_200_OK)
async def upload_file(
    response: Response,
    file_id: int,
    name: Optional[str] = None,
    tag: Optional[str] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Format new filename
    full_name = actions.format_filename(file, file_id, name)

    # Save file
    await actions.save_file_to_uploads(file, full_name)

    # Get file size
    file_size = actions.get_file_size(full_name)

    # Get info from DB
    file_info_from_db = actions.get_file_from_db(db, file_id)

    # Add to DB
    if not file_info_from_db:
        response.status_code = status.HTTP_201_CREATED
        return actions.add_file_to_db(
            db,
            file_id=file_id,
            full_name=full_name,
            tag=tag,
            file_size=file_size,
            file=file,
        )

    # Update in DB
    if file_info_from_db:
        # Delete file from uploads
        actions.delete_file_from_uploads(file_info_from_db.name)

        response.status_code = status.HTTP_201_CREATED
        return actions.update_file_in_db(
            db,
            file_id=file_id,
            full_name=full_name,
            tag=tag,
            file_size=file_size,
            file=file,
        )


@app.get("/api/download", tags=["Download"], status_code=status.HTTP_200_OK)
async def download_file(
    response: Response, file_id: int, db: Session = Depends(get_db)
):
    file_info_from_db = actions.get_file_from_db(db, file_id)

    if file_info_from_db:
        file_resp = FileResponse(
            config.UPLOADED_FILES_PATH + file_info_from_db.name,
            media_type=file_info_from_db.mime_type,
            filename=file_info_from_db.name,
        )
        response.status_code = status.HTTP_200_OK
        return file_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"msg": "File not found"}


@app.delete("/api/delete", tags=["Delete"])
async def delete_file(response: Response, file_id: int, db: Session = Depends(get_db)):
    file_info_from_db = actions.get_file_from_db(db, file_id)

    if file_info_from_db:
        # Delete file from DB
        actions.delete_file_from_db(db, file_info_from_db)

        # Delete file from uploads
        actions.delete_file_from_uploads(file_info_from_db.name)

        response.status_code = status.HTTP_200_OK
        return {"msg": f"File {file_info_from_db.name} successfully deleted"}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"msg": f"File does not exist"}
