import subprocess  # nosec B404

# I’m using subprocess locally.

from app.settings.paths import RUN_SERVER_REDIS_PATH


def run() -> None:
    subprocess.Popen([RUN_SERVER_REDIS_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)  # nosec B603
    # Local assistant; the user doesn’t insert data there.
