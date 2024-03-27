from abc import ABC


class ModelError(ABC, Exception):
    pass


class NoFiniteRewardError(ModelError):
    pass
