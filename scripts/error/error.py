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


class StateRewardUnsupported(ModelError):
    pass


class LongRunAverageUnsupported(ModelError):
    pass


class SegmentationFault(ModelError):
    pass


class NullPointerException(ModelError):
    pass


class UnsupportedProperty(ModelError):
    pass


class UnsupportedConversion(ModelError):
    pass
