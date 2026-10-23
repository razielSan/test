import subprocess
import sys

from test_data.settings import names_test_databases


def run_tests() -> None:
    if len(sys.argv) == 1 or len(sys.argv) > 2:
        print("Incorrect input.\nThe input should be of the form\n\n" "run_test.py database_name")
        return None

    database = sys.argv[1]

    if database not in names_test_databases:
        databases_names = ", ".join(names_test_databases)
        print(f"Unknown type database: {database}.\n" f"Available databases: {databases_names}")
        return
    result = subprocess.run(["pytest", "-m", "api", "tests", f"--backend={database}"])

    if result.returncode:
        exit(result.returncode)


if __name__ == "__main__":
    run_tests()
