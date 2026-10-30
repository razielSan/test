У меня уже есть README.MD в проекте


Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   .github/workflows/tests.yml
        modified:   README.MD

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        test.py

no changes added to commit (use "git add" and/or "git commit -a")

(auth-register-py3.8) D:\ProgrammingProjects\Python\Framework\Project\FAST_API\P
ROJECT\OTHER\my_project\BASE_APP>git add .

(auth-register-py3.8) D:\ProgrammingProjects\Python\Framework\Project\FAST_API\P
ROJECT\OTHER\my_project\BASE_APP>git commit -m "6"
Prevent committing environment files.....................................Passed
[main ba96e73] 6
 3 files changed, 2 insertions(+), 4 deletions(-)
 create mode 100644 test.py

(auth-register-py3.8) D:\ProgrammingProjects\Python\Framework\Project\FAST_API\P
ROJECT\OTHER\my_project\BASE_APP>git push
Enumerating objects: 11, done.
Counting objects: 100% (11/11), done.
Delta compression using up to 2 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (6/6), 475 bytes | 475.00 KiB/s, done.
Total 6 (delta 2), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
To github.com:razielSan/test.git
   5d14de8..ba96e73  main -> main



И все равно 


  - Installing ruff (0.4.1)
  - Installing trufflehog3 (3.0.***)
  - Installing vulture (2.11)

Installing the current project: auth-register (0.1.0)

Error: The current project could not be installed: Readme path `/home/runner/work/test/test/README.md` does not exist.
If you do not want to install the current project use --no-root.
If you want to use Poetry only for dependency management but not for packaging, you can disable package mode by setting package-mode = false in your pyproject.toml file.
If you did intend to install the curren

git log -n 1 --follow -- path/to/README.MD