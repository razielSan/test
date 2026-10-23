import subprocess
from typing import Set


def get_the_last_file_from_path(path: str) -> str:
    return path.replace("\\", "/").split("/")[-1]


FORBIDDEN_FILES = (".env", ".env.test")


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        check=True,
    )

    staged_files: Set[str] = set(result.stdout.splitlines())
    forbidden = sorted(
        path for path in staged_files if get_the_last_file_from_path(path=path) in FORBIDDEN_FILES
    )
    if forbidden:
        print("ERROR: Environment files must not be committed:")
        for path in forbidden:
            print(f"  - {path}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
