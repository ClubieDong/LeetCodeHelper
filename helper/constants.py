from datetime import timedelta

CACHE_PATH = "cache/problems.dat"
CACHE_TTL = timedelta(days=1).total_seconds()
API_URL = "https://leetcode-cn.com/api/problems/algorithms/"

SMART_SEARCH_TPL = [
    "https://leetcode-cn.com/problems/{slug}/",
    "{slug}",
    "{id_str}",
    "{id}-{slug}",
]

CURL_URL = "https://leetcode-cn.com/graphql/"
CURL_HEADER = {
    "referer": "https://leetcode-cn.com/"
}
CURL_REQUEST = {
    "operationName": "questionData",
    "variables": {
        "titleSlug": None
    },
    "query": "query questionData($titleSlug:String!){question(titleSlug:$titleSlug){translatedTitle codeSnippets{lang code}}}"
}

MAIN_BRANCH = "master"
INITIAL_COMMIT_MSG = "Initialize project"
TEMP_COMMIT_MSG = "Temporary commit"
REBASE_COMMIT_MSG = "Commit before rebase"

DIFFICULTY_DIR = {
    1: "easy",
    2: "medium",
    3: "hard",
}
SPECIAL_ID_DIR = [
    ("LCP", "LCP"),
    ("LCS", "LCS"),
    ("jian-zhi-offer-ii", "剑指 Offer II"),
    ("jian-zhi-offer", "剑指 Offer"),
    ("mian-shi-ti", "面试题"),
]

SOLUTION_HPP_PATH = "test_traits/solution.hpp"
SOLUTION_HPP_TPL = "#include \"../{src}\"\n"

TEST_RUN_MSG = "Testing {id}-{slug}..."
TEST_FAIL_BUILD_MSG = "Fail to build {id}-{slug}"
TEST_FAIL_RUN_MSG = "Fail to pass tests of {id}-{slug}"
TEST_BUILD_CMD = "cmake --build build >/dev/null"
TEST_RUN_CMD = "build/leetcode >/dev/null"
TEST_SUCCESS_MSG = "All committed problems have successfully passed the test"

ERR_DIRTY_TREE = "there are changes other than the solution file, clean them manually before running this command"
ERR_PROBLEM_NOT_FOUND = "cannot find problem by \"{text}\""
ERR_MORE_THAN_ONE_PROBLEM_FOUND = "more than one problem is found by \"{text}\":\n{names}"
ERR_UNKNOWN_DIFFICULTY = "unknown difficulty({diff}) of problem \"{id}-{slug}\""
ERR_UNKNOWN_FRONTEND_ID = "unknown frontend id({id_str}) of problem \"{id}-{slug}\""
ERR_COMMIT_ON_MAIN = "cannot commit on main branch"
ERR_INVALID_BRANCH = "cannot find problem associated with this branch({branch})"
ERR_INVALID_CATEGORY = "cannot understand category \"{category}\""
ERR_PROBLEM_NOT_COMMITTED = "the problem \"{id}-{slug}\" is not committed"