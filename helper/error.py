class LeetCodeError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class LeetCodeInvalidArg(Exception):
    pass
