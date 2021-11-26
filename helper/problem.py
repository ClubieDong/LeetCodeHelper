import re
import time
import json
import pickle
import requests
from error import *
from my_git import Git
from constants import *
from pathlib import Path
from functools import lru_cache
from prettytable import PrettyTable


class ProblemDetail:
    def __init__(self, slug: str):
        print(f"Downloading detailed problem info of \"{slug}\"...")
        req = CURL_REQUEST
        req["variables"]["titleSlug"] = slug
        resp = requests.post(CURL_URL, headers=CURL_HEADER, json=req)
        obj = json.loads(resp.text)
        obj = obj["data"]["question"]
        self.title: str = obj["translatedTitle"]
        self.code: str = ""
        if obj["codeSnippets"] is not None:
            for i in obj["codeSnippets"]:
                if i["lang"] == "C++":
                    self.code: str = i["code"]
                    break


class Problem:
    def __init__(self, obj):
        stat = obj["stat"]
        self.id: int = stat["question_id"]
        self.id_str: str = stat["frontend_question_id"]
        self.slug: str = stat["question__title_slug"]
        self.passed: int = stat["total_acs"]
        self.submitted: int = stat["total_submitted"]
        self.article_cnt: int = stat["total_column_articles"]
        difficulty = obj["difficulty"]["level"]
        if difficulty not in DIFFICULTY_DIR:
            err_msg = ERR_UNKNOWN_DIFFICULTY.format(
                diff=difficulty, id=self.id, slug=self.slug)
            raise LeetCodeError(err_msg)
        self.difficulty = DIFFICULTY_DIR[difficulty]

    @lru_cache
    def get_detail(self) -> ProblemDetail:
        return ProblemDetail(self.slug)

    @lru_cache
    def get_branch_name(self) -> str:
        return f"{self.id}-{self.slug}"

    @lru_cache
    def get_commit_msg(self) -> str:
        return f"{self.id_str}. {self.get_detail().title}"

    @lru_cache
    def get_src_path(self) -> str:
        if re.match("^\d+$", self.id_str) is not None:
            id100 = int(self.id_str) // 100
            sub_dir = f"{id100}00-{id100}99"
        else:
            for dir, prefix in SPECIAL_ID_DIR:
                if self.id_str.startswith(prefix):
                    sub_dir = dir
                    break
            else:
                msg = ERR_UNKNOWN_FRONTEND_ID.format(
                    id_str=self.id_str, id=self.id, slug=self.slug)
                return LeetCodeError(msg)
        return f"problems/{self.difficulty}/{sub_dir}/{self.id}-{self.slug}.hpp"

    @lru_cache
    def get_src_content(self) -> str:
        return self.get_detail().code

    @lru_cache
    def get_sort_key(self):
        if re.match("^\d+$", self.id_str) is not None:
            return ("", int(self.id_str))
        return (self.id_str, 0)

    @lru_cache
    def get_table_row(self):
        return (self.id_str, self.slug, self.difficulty, self.passed,
                self.submitted, f"{self.passed / self.submitted * 100:.1f}%",
                self.article_cnt)


class ProblemList:
    def __init__(self, obj):
        self.problems: list[Problem] = []
        for p in obj["stat_status_pairs"]:
            self.problems.append(Problem(p))

    @staticmethod
    @lru_cache
    def get_instance():
        # First call get_instance()
        if Path(CACHE_PATH).exists() and time.time() - Path(CACHE_PATH).stat().st_mtime < CACHE_TTL:
            # Cache exists and hasn't expired
            with open(CACHE_PATH, "rb") as f:
                return pickle.load(f)
        # Download from LeetCode API, and add to cache
        print("Downloading problem list...")
        resp = requests.get(API_URL)
        assert(resp.status_code == requests.codes.ok)
        obj = json.loads(resp.text)
        problem_list = ProblemList(obj)
        Path(CACHE_PATH).parent.mkdir(exist_ok=True)
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(problem_list, f)
        return problem_list

    def smart_search(self, text: str) -> Problem:
        valid_problems: list[Problem] = []
        for prob in self.problems:
            for tpl in SMART_SEARCH_TPL:
                expected = tpl.format(
                    id=prob.id, id_str=prob.id_str, slug=prob.slug)
                if text == expected:
                    valid_problems.append(prob)
                    break
        if len(valid_problems) == 0:
            err_msg = ERR_PROBLEM_NOT_FOUND.format(text=text)
            raise LeetCodeError(err_msg)
        if len(valid_problems) > 1:
            names = [f"\t{i.id_str}. {i.slug}" for i in valid_problems]
            names = "\n".join(names)
            err_msg = ERR_MORE_THAN_ONE_PROBLEM_FOUND.format(
                text=text, names=names)
            raise LeetCodeError(err_msg)
        return valid_problems[0]

    def search_by_branch(self, branch: str) -> Problem:
        for p in self.problems:
            if p.get_branch_name() == branch:
                return p
        return None

    def get_list_in_category(self, category: str):
        category = category.lower()
        if category == "":
            return self.problems
        if category in ["easy", "medium", "hard"]:
            return [p for p in self.problems if p.difficulty == category]
        br_set = set(Git.get_branches())
        started_list = [p for p in self.problems
                        if p.get_branch_name() in br_set]
        if category == "started":
            return started_list
        cm_set = {c.message[:c.message.find(". ")]
                  for c in Git.get_commits(MAIN_BRANCH)}
        committed_list = [p for p in self.problems if p.id_str in cm_set]
        if category == "committed":
            return committed_list
        if category == "todo":
            return [p for p in self.problems
                    if p not in started_list and p not in committed_list]
        err_msg = ERR_INVALID_CATEGORY.format(category=category)
        raise LeetCodeError(err_msg)

    def get_problem_status(self):
        br_set = set(Git.get_branches())
        cm_set = {c.message[:c.message.find(". ")]
                  for c in Git.get_commits(MAIN_BRANCH)}
        status = {}
        for p in self.problems:
            if p.get_branch_name() in br_set:
                status[p] = "started"
            elif p.id_str in cm_set:
                status[p] = "committed"
            else:
                status[p] = "todo"
        return status

    def print_table(self, category: str):
        problem_list = self.get_list_in_category(category)
        problem_list.sort(key=Problem.get_sort_key)
        table = PrettyTable()
        table.field_names = ("ID", "Name", "Difficulty",
                             "Passed", "Submitted", "Pass rate", "Articles")
        for p in problem_list:
            table.add_row(p.get_table_row())
        status = self.get_problem_status()
        status = [status[p] for p in problem_list]
        table.add_column("Status", status)
        print(table)

    def print_statistics(self):
        all = set(self.problems)
        easy = set(self.get_list_in_category("easy"))
        medium = set(self.get_list_in_category("medium"))
        hard = set(self.get_list_in_category("hard"))
        todo = set(self.get_list_in_category("todo"))
        started = set(self.get_list_in_category("started"))
        committed = set(self.get_list_in_category("committed"))
        data = [
            [len(easy & todo), len(easy & started),
             len(easy & committed), len(easy)],
            [len(medium & todo), len(medium & started),
             len(medium & committed), len(medium)],
            [len(hard & todo), len(hard & started),
             len(hard & committed), len(hard)],
            [len(todo), len(started), len(committed), len(all)],
        ]
        table = PrettyTable()
        table.field_names = ("", "Todo", "Started",
                             "Committed", "Total", "Percent")
        table.add_row(
            ("Easy", *data[0], f"{data[0][2] / data[0][3] * 100:.1f}%"))
        table.add_row(
            ("Medium", *data[1], f"{data[1][2] / data[1][3] * 100:.1f}%"))
        table.add_row(
            ("Hard", *data[2], f"{data[2][2] / data[2][3] * 100:.1f}%"))
        table.add_row(
            ("Total", *data[3], f"{data[3][2] / data[3][3] * 100:.1f}%"))
        print(table)
