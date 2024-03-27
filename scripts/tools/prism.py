import re
import subprocess
from typing import List, Dict, Optional

from scripts.model.model import Model
from scripts.tools.tool import Tool, Method


class Prism(Tool):

    def __init__(self, path):
        self._path = path

    def validate(self) -> bool:
        try:
            output = subprocess.run(self._path, stdout=subprocess.PIPE, text=True)
            return 'PRISM' in output.stdout
        except FileNotFoundError:
            return False

    def solve(self, method: Method, model: Model, parameters: Dict) -> bool | Optional[float]:
        if method == Method.ValueIteration:
            return self._vi_solve(model, parameters['epsilon'])
        if method == Method.LinearProgramming:
            return self._lp_solve(model)
        raise ValueError(f"Unsupported method: {method}")

    def _vi_solve(self, model: Model, epsilon: float) -> bool | Optional[float]:
        result = subprocess.run([self._path, model.file(),
                                 "-const", ",".join(f"{name}={value}" for name, value in model.constants().items()),
                                 "-pf", model.property(),
                                 "-epsilon", str(epsilon), "-rel",
                                 "-maxiters", "10000"],
                                stdout=subprocess.PIPE, text=True)
        return self._parse_result(result.stdout)

    def _lp_solve(self, model: Model) -> bool | Optional[float]:
        result = subprocess.run([self._path, model.file(),
                                 "-const", ",".join(f"{name}={value}" for name, value in model.constants().items()),
                                 "-pf", model.property(),
                                 "-lp"],
                                stdout=subprocess.PIPE, text=True)
        return self._parse_result(result.stdout)

    def _parse_result(self, message: str) -> bool | Optional[float]:
        value = re.search('Result: (.+?)\n', message)
        if value is None:
            raise Exception(message)

        try:
            return float(value.group(1))
        except ValueError:
            if value.group(1) == 'true':
                return True
            if value.group(1) == 'false':
                return False
            raise ValueError(message)

    def supported_methods(self) -> List[Method]:
        return [Method.ValueIteration, Method.LinearProgramming]
