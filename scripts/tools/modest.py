import os
import re
import subprocess
from typing import Dict, Optional, List

from error.error import NoFiniteRewardError, StepboundUnsupported, SegmentationFault
from model.model import Model
from tools.tool import Tool, Method, Setting


class Modest(Tool):

    def __init__(self, path):
        self._path = path

    def validate(self) -> bool:
        try:
            output = subprocess.run(self._path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return 'The Modest Toolset' in output.stdout
        except FileNotFoundError:
            return False

    def supported_methods(self) -> List[Method]:
        return [Method.ValueIteration, Method.LinearProgramming]

    def supported_settings(self) -> List[Setting]:
        return [Setting.AbsoluteEpsilon, Setting.RelativeEpsilon]

    def solve(self, method: Method, model: Model, timeout: int, parameters: Dict) -> bool | Optional[float]:
        if method == Method.ValueIteration:
            return self._vi_solve(model, timeout, parameters['epsilon'] , parameters['absoluteEpsilon'])
        if method == Method.LinearProgramming:
            return self._lp_solve(model, timeout)
        raise ValueError(f"Unsupported method: {method}")

    def _vi_solve(self, model: Model, timeout: int, epsilon: float, absolute_epsilon: bool) -> bool | Optional[float]:
        try:
            arguments = [self._path, "check", model.modest_file(),
                                     "--alg", "ValueIteration",
                                     "--epsilon", str(epsilon),
                                     "--props", f'{"Achievability" if model.value() is not None else "Numerical"}{model.property_id()}',
                                     "--experiment", ",".join(f"{name}={value}" for name, value in {**model.constants(), "UNKNOWN": model.value() if model.value() is not None else 0}.items())]
            if absolute_epsilon:
                arguments.append("--absolute-epsilon")

            result = subprocess.run(arguments, stdout=subprocess.PIPE, text=True, timeout=timeout)
            return self._parse_result(result.stdout)
        finally:
            for file in os.listdir(os.getcwd()):
                if file.startswith('CompiledAutomata'):
                    os.remove(file)

    def _lp_solve(self, model: Model, timeout: int) -> bool | Optional[float]:
        try:
            arguments = [self._path, "check", model.modest_file(),
                                     "--alg", "LinearProgramming",
                                     "--props", f'{"Achievability" if model.value() is not None else "Numerical"}{model.property_id()}',
                                     "--experiment", ",".join(f"{name}={value}" for name, value in {**model.constants(), "UNKNOWN": model.value() if model.value() is not None else 0}.items())]
            result = subprocess.run(arguments, stdout=subprocess.PIPE, text=True, timeout=timeout)
            return self._parse_result(result.stdout)
        finally:
            for file in os.listdir(os.getcwd()):
                if file.startswith('CompiledAutomata'):
                    os.remove(file)

    def _parse_result(self, message: str) -> bool | Optional[float]:
        value = re.search('Result: (.+?)\n', message)
        value = value if value is not None else re.search('Probability: (.+?)\n', message)
        if value is None:
            if 'infinite cumulative reward' in message:
                raise NoFiniteRewardError()
            raise Exception(message)

        try:
            return float(value.group(1))
        except ValueError:
            if value.group(1).lower().strip() == 'true':
                return True
            if value.group(1).lower().strip() == 'false':
                return False
            raise ValueError(message)
