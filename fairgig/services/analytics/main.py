from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers.commission import router as commission_router
from routers.complaints import router as complaints_router
from routers.income import router as income_router
from routers.vulnerability import router as vulnerability_router

app = FastAPI(title='FairGig Analytics Service', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            'detail': 'Validation failed',
            'type': 'validation_error',
            'status': 400,
            'errors': exc.errors(),
        },
    )


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'analytics'}


app.include_router(commission_router)
app.include_router(income_router)
app.include_router(vulnerability_router)
app.include_router(complaints_router)
