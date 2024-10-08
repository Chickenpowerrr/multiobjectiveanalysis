import re
import subprocess
from typing import Dict, Optional, List

from error.error import NoFiniteRewardError, StepboundUnsupported, SegmentationFault, UnknownError
from model.model import Model
from tools.tool import Tool, Method, Setting


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
        return [Method.ValueIteration, Method.LinearProgramming]

    def supported_settings(self) -> List[Setting]:
        return [Setting.AbsoluteEpsilon]

    def solve(self, method: Method, model: Model, timeout: int, parameters: Dict) -> bool | Optional[float]:
        if method == Method.ValueIteration:
            return self._vi_solve(model, timeout, parameters['epsilon'])
        if method == Method.LinearProgramming:
            return self._lp_solve(model, timeout)
        raise ValueError(f"Unsupported method: {method}")

    def _vi_solve(self, model: Model, timeout: int, epsilon: float) -> bool | Optional[float]:
        arguments = [self._path, "--prism", model.prism_file(),
                                 "-prop", model.prism_property(),
                                 "-eps", str(epsilon), "--absolute",
                                 "--multiobjective:precision", str(epsilon), "abs",
                                 "--multiobjective:method", "pcaa"]
        if len(model.constants()) > 0:
            arguments.extend(["-const", ",".join(f"{name}={value}" for name, value in model.constants().items())])
        result = subprocess.run(arguments, stdout=subprocess.PIPE, text=True, timeout=timeout)
        return self._parse_result(result.stdout)

    def _lp_solve(self, model: Model, timeout: int) -> bool | Optional[float]:
        if '?' in model.prism_property():
            return None

        arguments = [self._path, "--prism", model.prism_file(),
                                 "-prop", model.prism_property(),
                                 "--multiobjective:method", "constraintbased", "--exact"]
        if len(model.constants()) > 0:
            arguments.extend(["-const", ",".join(f"{name}={value}" for name, value in model.constants().items())])
        result = subprocess.run(arguments, stdout=subprocess.PIPE, text=True, timeout=timeout)
        return self._parse_result(result.stdout)

    def _parse_result(self, message: str) -> bool | Optional[float]:
        value = re.search('Result \\(for initial states\\): (.+?)\n', message)
        if value is None:
            if 'There is no Pareto optimal scheduler that yields finite reward for all objectives' in message:
                raise NoFiniteRewardError()
            if 'Constraint-based solver only supports total-reward objectives' in message:
                raise StepboundUnsupported()
            if 'mars_rover' in message and 'constraintbased' in message:
                raise SegmentationFault()
            print(message)
            raise UnknownError()

        try:
            return float(value.group(1))
        except ValueError:
            if value.group(1) == 'true':
                return True
            if value.group(1) == 'false':
                return False
            raise ValueError(message)
