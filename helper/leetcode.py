import os
import sys
from error import *
from my_git import Git
from constants import *
from pathlib import Path
from problem import Problem, ProblemList


class LeetCode:
    def __init__(self, args: list[str]):
        self.args = args

    def run(self):
        try:
            if len(self.args) < 2:
                raise LeetCodeInvalidArg()
            if self.args[1] in ["help", "h", "--help", "-h"]:
                self.show_usage()
            elif self.args[1] in ["checkout", "ck"]:
                self.checkout(" ".join(self.args[2:]))
            elif self.args[1] in ["commit", "cm"]:
                self.commit(" ".join(self.args[2:]))
            elif self.args[1] in ["main", "master"]:
                if len(self.args) != 2:
                    raise LeetCodeInvalidArg()
                self.main()
            elif self.args[1] in ["list", "ls"]:
                if len(self.args) not in (2, 3):
                    raise LeetCodeInvalidArg()
                category = self.args[2] if len(self.args) == 3 else ""
                self.list(category)
            elif self.args[1] in ["statistics", "stat", "st"]:
                if len(self.args) != 2:
                    raise LeetCodeInvalidArg()
                self.statistics()
            elif self.args[1] in ["peek", "pk"]:
                self.peek(" ".join(self.args[2:]))
            elif self.args[1] in ["test", "t"]:
                if len(self.args) != 2:
                    raise LeetCodeInvalidArg()
                self.test()
            else:
                raise LeetCodeInvalidArg()
        except LeetCodeInvalidArg as err:
            self.show_usage()
        except LeetCodeError as err:
            print(f"Error: {err.msg}")

    def show_usage(self):
        print("leetcode usage:")
        print("    leetcode help                show this help message")
        print("    leetcode checkout <Problem>  start or continue a problem")
        print("    leetcode commit [Message]    commit a problem")
        print("    leetcode main                checkout main branch")
        print("    leetcode list [category]     list problems by difficulty or status")
        print("    leetcode statistics          show statistics")
        print("    leetcode peek <Problem>      open a committed problem on main branch")
        print("    leetcode test                build and run all committed problems")

    def checkout(self, text: str):
        problem_list = ProblemList.get_instance()
        problem = problem_list.smart_search(text)
        # Create branch if not exists
        br_name = problem.get_branch_name()
        for br in Git.get_branches():
            if br.name == br_name:
                break
        else:
            Git.create_branch(br_name)
        # Checkout the branch, change solution.hpp
        self.switch_to_problem(problem)
        # Create file and commit if not exists
        src_path = problem.get_src_path()
        if not Path(src_path).exists():
            content = problem.get_src_content()
            print(f"Creating solution file \"{src_path}\" from template...")
            src_dir = "/".join(Path(src_path).parts[:-1])
            Path(src_dir).mkdir(parents=True, exist_ok=True)
            with open(src_path, "w") as f:
                f.write(content)
            commit_msg = problem.get_commit_msg()
            Git.create_commit(src_path, commit_msg)
        # Open the file
        self.open_file(src_path)

    def commit(self, message: str):
        if Git.get_head().name == MAIN_BRANCH:
            raise LeetCodeError(ERR_COMMIT_ON_MAIN)
        problem_list = ProblemList.get_instance()
        problem = problem_list.search_by_branch(Git.get_head().name)
        if problem is None:
            err_msg = ERR_INVALID_BRANCH.format(branch=Git.get_head().name)
            raise LeetCodeError(err_msg)
        src = problem.get_src_path()
        commit_msg = problem.get_commit_msg()
        if message != "":
            commit_msg += " " + message
        Git.rebase(src, commit_msg)

    def main(self):
        if Git.get_head().name == MAIN_BRANCH:
            return
        self.save_temp()
        main_br = Git.get_branches()[MAIN_BRANCH]
        Git.checkout_branch(main_br)

    def list(self, category: str):
        ProblemList.get_instance().print_table(category)

    def statistics(self):
        ProblemList.get_instance().print_statistics()

    def peek(self, text: str):
        problem_list = ProblemList.get_instance()
        problem = problem_list.smart_search(text)
        committed = problem_list.get_list_in_category("committed")
        if problem not in committed:
            err_msg = ERR_PROBLEM_NOT_COMMITTED.format(id=problem.id_str, slug=problem.slug)
            raise LeetCodeError(err_msg)
        self.change_solution_file(problem)
        self.open_file(problem.get_src_path())

    def test(self):
        self.main()
        problem_list = ProblemList.get_instance()
        committed = problem_list.get_list_in_category("committed")
        for p in committed:
            print(TEST_RUN_MSG.format(id=p.id_str, slug=p.slug))
            self.change_solution_file(p)
            print(">", TEST_BUILD_CMD)
            if os.system(TEST_BUILD_CMD) != 0:
                print(TEST_FAIL_BUILD_MSG.format(id=p.id_str, slug=p.slug))
                return
            print(">", TEST_RUN_CMD)
            if os.system(TEST_RUN_CMD) != 0:
                print(TEST_FAIL_RUN_MSG.format(id=p.id_str, slug=p.slug))
                return
        print(TEST_SUCCESS_MSG)

    def save_temp(self):
        problem_list = ProblemList.get_instance()
        problem = problem_list.search_by_branch(Git.get_head().name)
        src = problem.get_src_path() if problem is not None else None
        Git.create_temp_commit(src)

    def change_solution_file(self, problem: Problem):
        if Path(SOLUTION_HPP_PATH).exists():
            action = "Changing"
            with open(SOLUTION_HPP_PATH, "r") as f:
                old_content = f.read()
        else:
            action = "Creating"
            old_content = ""
        src_path = problem.get_src_path()
        new_content = SOLUTION_HPP_TPL.format(src=src_path)
        if old_content != new_content:
            print(f"{action} \"{SOLUTION_HPP_PATH}\" to include \"{src_path}\"...")
            with open(SOLUTION_HPP_PATH, "w") as f:
                f.write(new_content)

    def switch_to_problem(self, problem: Problem):
        br = Git.get_branches()[problem.get_branch_name()]
        if br.name != Git.get_head().name:
            self.save_temp()
            Git.checkout_branch(br)
        self.change_solution_file(problem)

    def open_file(self, src: str):
        if os.system("type code > /dev/null") != 0:
            return
        cmd = f"code {src}"
        print(">", cmd)
        os.system(cmd)


if __name__ == "__main__":
    lc = LeetCode(sys.argv)
    lc.run()
