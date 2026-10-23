from fastapi import templating

from app.my_project.backend.settings.paths import TEMPLATES_DIR


templates = templating.Jinja2Templates(directory=TEMPLATES_DIR)
