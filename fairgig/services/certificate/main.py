from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.certificate import router as certificate_router

app = FastAPI(title='FairGig Certificate Service', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'certificate'}


app.include_router(certificate_router)
