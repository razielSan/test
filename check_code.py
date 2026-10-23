from pathlib import Path
import sys


root_dir = Path(__file__).parent
folder_app = root_dir / "src"
folder_test = root_dir / "tests"
FOLDRES = [folder_app, folder_test]

files = (
    root_dir / "run_test_api.py",
    root_dir / "run_test_integration.py",
    root_dir / "run_test_unit.py",
    root_dir / "run_test_page.py",
)
separator = "-" * 5
if len(sys.argv) == 2:
    search_word = sys.argv[1]
    for folder in FOLDRES:
        print(f"{separator}start {folder.name}{separator}\n")
        for file_path in folder.rglob("*.py"):
            if file_path.is_file():
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                    if search_word in text:
                        print(f"{file_path}\n{search_word}\n")

                except Exception:
                    pass
        print(f"\n{separator}end {folder.name}{separator}\n")

    print(f"{separator}start files{separator}\n")
    for file in files:
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            if search_word in text:
                print(f"{file}\n{search_word}\n")

        except Exception:
            pass
    print(f"\n{separator}end files{separator}\n")
else:
    print("Необходимо передать 1 параметр для поиска значения")
