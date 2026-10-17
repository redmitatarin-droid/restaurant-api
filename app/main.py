from fastapi import FastAPI
from app.routers import (
    products,
    users,
    orders,
    auth
)
from fastapi import Request
from fastapi.responses import JSONResponse
from app.logger import logger
from app.config import FRONTEND_ORIGIN
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_ORIGIN
from app.routers.categories import router as categories_router



app = FastAPI(
    title="Restaurant API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(categories_router)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={"Access-Control-Allow-Origin": FRONTEND_ORIGIN},
    )

@app.get("/health")
def health():
    return {"status": "ok"}