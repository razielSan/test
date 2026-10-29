from logging import Logger

from typing import Dict
from fastapi import FastAPI, APIRouter


def inculde_routers(
    app: FastAPI,
    routers: Dict[str, APIRouter],
    logger: Logger,
) -> None:
    for router_name, router in routers.items():
        app.include_router(router)
        logger.info(
            f"[INCLUDE ROUTER SUCCESS] The root router - {FastAPI.__name__}."
            f" Child router - {router_name}"
        )
