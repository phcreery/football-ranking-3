import uvicorn
from fastapi import FastAPI
from .config import logger, uvicorn_config
from .routers import scores, client

# from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api/v3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scores.router)
app.include_router(client.router)


def main() -> int:  # pragma: no cover
    logger.info("Start ... ")
    try:
        uvicorn.run(
            app=uvicorn_config.app,
            host=uvicorn_config.host,
            port=uvicorn_config.port,
            reload=uvicorn_config.reload,
            reload_includes=(
                uvicorn_config.reload_includes if uvicorn_config.reload else None
            ),
            log_level=uvicorn_config.log_level,
        )

        return 0
    except KeyboardInterrupt:
        logger.info("Done ...")
        return 1
