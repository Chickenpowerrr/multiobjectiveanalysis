import re
import subprocess
from typing import Dict, Optional, List

from scripts.error.error import NoFiniteRewardError
from scripts.model.model import Model
from scripts.tools.tool import Tool, Method


class Storm(Tool):

    def __init__(self, path):
        self._path = path

    def validate(self) -> bool:
        try:
            output = subprocess.run(self._path, stdout=subprocess.PIPE, text=True)
            return 'Storm' in output.stdout
        except FileNotFoundError:
            return False

    def supported_methods(self) -> List[Method]:
        return [Method.ValueIteration]

    def solve(self, method: Method, model: Model, parameters: Dict) -> bool | Optional[float]:
        if method == Method.ValueIteration:
            return self._vi_solve(model, parameters['epsilon'])
        raise ValueError(f"Unsupported method: {method}")

    def _vi_solve(self, model: Model, epsilon: float) -> bool | Optional[float]:
        result = subprocess.run([self._path,
                                 "--prism", model.file(),
                                 "-const", ",".join(f"{name}={value}" for name, value in model.constants().items()),
                                 "-prop", model.property(),
                                 "--multiobjective:precision", str(epsilon), "reldiff",
                                 "--multiobjective:method", "pcaa"],
                                stdout=subprocess.PIPE, text=True)
        return self._parse_result(result.stdout)

    def _parse_result(self, message: str) -> bool | Optional[float]:
        value = re.search('Result \\(for initial states\\): (.+?)\n', message)
        if (value is None
                and 'There is no Pareto optimal scheduler that yields finite reward for all objectives' in message):
            raise NoFiniteRewardError()
        if value is None:
            raise Exception(message)

        try:
            return float(value.group(1))
        except ValueError:
            if value == 'true':
                return True
            if value == 'false':
                return False
            raise ValueError(message)
