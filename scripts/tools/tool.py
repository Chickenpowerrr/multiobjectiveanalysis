from abc import abstractmethod, ABC
from enum import Enum
from typing import Optional, Dict, List

from scripts.model.model import Model


class Method(Enum):
    ValueIteration = 0
    LinearProgramming = 1


class Tool(ABC):

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def solve(self, method: Method, model: Model, parameters: Dict) -> bool | Optional[float]:
        pass

    @abstractmethod
    def supported_methods(self) -> List[Method]:
        pass
