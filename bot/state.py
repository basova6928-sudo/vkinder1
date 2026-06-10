class UserState:
    def __init__(self):
        self.candidates = []
        self.index = 0

    def set_candidates(self, candidates: list):
        self.candidates = candidates
        self.index = 0

    def current(self):
        if self.index < len(self.candidates):
            return self.candidates[self.index]
        return None

    def next(self):
        self.index += 1
        return self.current()
