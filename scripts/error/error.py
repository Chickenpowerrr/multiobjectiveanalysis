from abc import ABC


class ModelError(ABC, Exception):
    pass


class NoFiniteRewardError(ModelError):
    pass


class StepboundUnsupported(ModelError):
    pass


class ConvergeError(ModelError):
    pass


class OnlyCumulativeSupported(ModelError):
    pass
