import logging

from settings.paths import LOG_DIR

LOG_DIR.mkdir(exist_ok=True)


class FormatLog:
    QUANTITY: int = 50
    SEPARATOR: str = "-"
    FMT: str = (
        f"{QUANTITY * SEPARATOR}\n[%(asctime)s] - %(name)s" " - [%(levelname)s - %(message)s]"
    )
    DATE_FMT: str = "%Y-%m-%d %H:%M:%S"


def setup_loggers() -> None:
    formatter = logging.Formatter(
        fmt=FormatLog.FMT,
        datefmt=FormatLog.DATE_FMT,
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt=formatter)

    file_handler = logging.FileHandler(filename=LOG_DIR / "app.logs", encoding="utf-8")
    file_handler.setFormatter(fmt=formatter)

    logger = logging.getLogger()
    logger.setLevel(level=logging.INFO)

    if logger.handlers:
        logger.handlers.clear()

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
