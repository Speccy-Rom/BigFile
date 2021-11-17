import os

from . import models, config


# Get file info from DB
def get_file_from_db(db, file_id):
    return db.query(models.Image).filter(models.Image.file_id == file_id).first()


# Offset\limit
def get_files_from_db_limit_offset(db, query, limit: int = None, offset: int = None):
    if limit and not offset:
        query = query[:limit]
    elif limit and offset:
        limit += offset
        query = query[offset:limit]
    elif not limit and offset:
        query = query[offset:]
    return query


# Delete file from uploads folder
def delete_file_from_uploads(file_name):
    try:
        os.remove(config.UPLOADED_FILES_PATH + file_name)
    except Exception as e:
        print(e)


# Save file to uploads folder
async def save_file_to_uploads(file, filename):
    with open(f'{config.UPLOADED_FILES_PATH}{filename}', "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
        uploaded_file.close()
