from error import *
from git import Repo
from constants import *
from pathlib import Path
from functools import lru_cache


class Git:
    @staticmethod
    @lru_cache
    def get_repo() -> Repo:
        repo = Repo()
        if len(repo.branches) == 0:
            print(f"> git commit --allow-empty -m \"{INITIAL_COMMIT_MSG}\"")
            repo.git.commit("--allow-empty", "-m", INITIAL_COMMIT_MSG)
        return Repo()

    @staticmethod
    def get_head():
        return Git.get_repo().active_branch

    @staticmethod
    def get_branches():
        return Git.get_repo().branches

    @staticmethod
    def get_commits(branch: str):
        return Git.get_repo().iter_commits(branch)

    @staticmethod
    def create_branch(name: str):
        repo = Git.get_repo()
        print(f"> git branch {name} {MAIN_BRANCH}")
        return repo.create_head(name, MAIN_BRANCH)

    @staticmethod
    def checkout_branch(branch):
        if Git.get_repo().active_branch.name == branch.name:
            return
        print(f"> git checkout {branch.name}")
        branch.checkout()

    @staticmethod
    def checkout_main():
        main_br = Git.get_branches()[MAIN_BRANCH]
        Git.checkout_branch(main_br)

    @staticmethod
    def create_temp_commit(src: str, commit_msg=TEMP_COMMIT_MSG):
        repo = Git.get_repo()
        if len(repo.untracked_files) > 0:
            raise LeetCodeError(ERR_DIRTY_TREE)
        if not repo.is_dirty():
            return
        if src is None:
            raise LeetCodeError(ERR_DIRTY_TREE)
        diff = repo.index.diff(None)
        if len(diff) != 1 or diff[0].a_path != src or diff[0].change_type != "M":
            raise LeetCodeError(ERR_DIRTY_TREE)
        Git.create_commit(src, commit_msg)

    @staticmethod
    def create_commit(src: str, msg: str):
        repo = Git.get_repo()
        print(f"> git add {src}")
        repo.index.add(src)
        print(f"> git commit -m \"{msg}\"")
        repo.index.commit(msg)

    @staticmethod
    def rebase(src: str, msg: str):
        repo = Git.get_repo()
        branch = repo.active_branch
        if branch.name == MAIN_BRANCH:
            raise LeetCodeError(ERR_COMMIT_ON_MAIN)
        Git.create_temp_commit(src, REBASE_COMMIT_MSG)
        with open(src, "r") as f:
            content = f.read()
        Git.checkout_main()
        print(f"Copying solution file \"{src}\" to main branch...")
        src_dir = "/".join(Path(src).parts[:-1])
        Path(src_dir).mkdir(parents=True, exist_ok=True)
        with open(src, "w") as f:
            f.write(content)
        Git.create_commit(src, msg)
        print(f"> git branch -D {branch.name}")
        repo.delete_head(branch, "-D")
