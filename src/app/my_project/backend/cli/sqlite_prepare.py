from sqlalchemy.engine import make_url

from settings.paths import ROOT_DIR
from pathlib import Path
from domain.db.constants import DatabaseName
from settings.config import settings


def cli() -> None:
    url = make_url(name_or_url=settings.DATABASE_CONNECT)
    if url.get_backend_name() != DatabaseName.sqlalchemy_sqlite.value:
        print("This command is available only for SQLite.")
        return
    database = url.database

    if not database or database == ":memory:":
        print("A file-based SQLite database was not specified.")
        return

    database_path = Path(database)
    if not database_path.is_absolute():
        database_path = ROOT_DIR / database_path

    database_path.parent.mkdir(parents=True, exist_ok=True)
    print("The required folders were successfully created")


if __name__ == "__main__":
    cli()
