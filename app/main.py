from fastapi import FastAPI


app = FastAPI()


@app.get("/", tags=['root'])
def root() -> dict:
    return {'status': '200 OK'}
