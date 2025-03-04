from datetime import datetime
from fastapi import Request, Response
from app.core.my_logging import logger


async def logging_middleware(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()
    logger.info(
        f'{response.status_code} {request.client.host} {request.method} '
        f'{request.url} {end_time - start_time}'
    )
    return response


async def additional_processing(request: Request, call_next):
    start_time = datetime.now()
    response: Response = await call_next(request)
    process_time = datetime.now() - start_time
    if response.status_code // 100 == 4:
        response.headers["X-ErrorHandleTime"] = str(process_time)
    return response
