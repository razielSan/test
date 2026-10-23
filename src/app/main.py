import uvicorn

from app.my_project.backend.core.startup import create_up
from app.settings.app import settings

app = create_up()


def run() -> None:
    uvicorn.run(
        reload=settings.RELOAD,
        host=settings.HOST,
        port=settings.PORT,
        app=settings.APP,
    )
