import uvicorn
from beanie import init_beanie
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from motor import motor_asyncio

from app.core.config import get_settings
from app.core.logger import get_logger, setup_logger

app = FastAPI()


@app.on_event("startup")
async def startup():
    config = get_settings()
    log = setup_logger(config.LOG_LEVEL)
    uri = config.get_mongodb_uri()
    client = motor_asyncio.AsyncIOMotorClient(uri)
    await init_beanie(database=client[config.DB_NAME], document_models=[])

    log = get_logger()
    log.info(f"starting banter-bus-core-api {config.WEB_HOST}:{config.WEB_PORT}")
    app.middleware("http")(catch_exceptions_middleware)


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        log = get_logger()
        log.exception("failed to complete operation", request=request)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_message": "failed to complete operation internal server error",
                "error_code": "server_error",
            },
        )


if __name__ == "__main__":
    config = get_settings()
    uvicorn.run(app, host=config.WEB_HOST, port=config.WEB_PORT)  # type: ignore
