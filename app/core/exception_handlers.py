from fastapi import HTTPException, status
from omnibus.log.logger import get_logger


async def log_uncaught_exceptions(request, err):
    logger = get_logger()
    logger.exception("Uncaught exception")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="failed to complete operation",
    )
