from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from os.path import isfile
from mimetypes import guess_type


app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory="site/assets"), name="assets")
app.mount("/search", StaticFiles(directory="site/search"), name="search")



@app.get('/{filename:path}')
def mkdocsite(filename: str):
    fn = './site/' + filename + 'index.html'
    if not isfile(fn):
        return Response(status_code=404)

    with open(fn) as f:
        content = f.read()

    content_type, _ = guess_type(fn)
    return Response(content, media_type=content_type)
