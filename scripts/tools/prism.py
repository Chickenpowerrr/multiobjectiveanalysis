import re
import subprocess
from typing import List, Dict, Optional

from scripts.error.error import NoFiniteRewardError, StepboundUnsupported, ConvergeError, OnlyCumulativeSupported
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
        arguments = [self._path, model.file(),
                     "-pf", model.property(),
                     "-epsilon", str(epsilon), "-abs",
                     "-paretoepsilon", str(epsilon),
                     "-maxiters", "100000"]
        if len(arguments) > 0:
            arguments.extend(["-const", ",".join(f"{name}={value}" for name, value in model.constants().items())])

        result = subprocess.run(arguments, stdout=subprocess.PIPE, text=True)
        return self._parse_result(result.stdout)

    def _lp_solve(self, model: Model) -> bool | Optional[float]:
        arguments = [self._path, model.file(), "-pf", model.property(), "-lp"]
        if len(arguments) > 0:
            arguments.extend(["-const", ",".join(f"{name}={value}" for name, value in model.constants().items())])

        result = subprocess.run(arguments, stdout=subprocess.PIPE, text=True)
        return self._parse_result(result.stdout)

    def _parse_result(self, message: str) -> bool | Optional[float]:
        value = re.search('Result: (.+?)\n', message)
        if value is None:
            if 'Step-bounded objectives are not currently supported with linear programming' in message:
                raise StepboundUnsupported()
            if 'Consider using a different numerical method or increasing the maximum number of iterations' in message:
                raise ConvergeError()
            if 'Only the C and C>=k reward operators are currently supported for multi-objective properties' in message:
                raise OnlyCumulativeSupported()
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
