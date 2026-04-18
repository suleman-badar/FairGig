from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import Base, engine
from routers.shifts import router as shifts_router
from routers.upload import router as upload_router
from routers.verification import router as verification_router

app = FastAPI(title="FairGig Earnings Service", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Validation failed",
            "type": "validation_error",
            "status": 400,
            "errors": exc.errors(),
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "earnings"}


app.include_router(shifts_router)
app.include_router(upload_router)
app.include_router(verification_router)
