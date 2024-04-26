import os
import re
import subprocess
from typing import List, Dict, Optional

from scripts.model.model import Model
from scripts.tools.tool import Tool, Method, Setting


class Epmc(Tool):

    def __init__(self, path: str, java: str, spot: str):
        self._path = path
        self._java = java
        self._spot = spot

    def validate(self) -> bool:
        try:
            arguments = [self._java, '-jar', self._path]
            output = subprocess.run(arguments, stdout=subprocess.PIPE, text=True)
            return '<epmc> help' in output.stdout
        except FileNotFoundError:
            return False

    def solve(self, method: Method, model: Model, timeout: int, parameters: Dict) -> bool | Optional[float]:
        if method == Method.ValueIteration:
            return self._vi_solve(model, timeout, parameters['epsilon'], parameters['absoluteEpsilon'])
        raise ValueError(f"Unsupported method: {method}")

    def _vi_solve(self, model: Model, timeout: int, epsilon: float, absolute_epsilon: bool) -> bool | Optional[float]:
        if os.path.exists("epmc-prop.pctl"):
            os.remove("epmc-prop.pctl")
        with open("epmc-prop.pctl", 'w') as prop_file:
            prop_file.write(model.property())

        arguments = [self._java, '-jar', self._path, 'check',
                     "--model-input-files", model.file(),
                     "--property-input-files", "epmc-prop.pctl",
                     "--graphsolver-iterative-stop-criterion", "absolute" if absolute_epsilon else "relative",
                     "--automaton-spot-ltl2tgba-cmd", self._spot,
                     "--graphsolver-iterative-tolerance", str(epsilon),
                     "--multi-objective-min-increase", str(epsilon)]
        if len(arguments) > 0:
            arguments.extend(["--const", ",".join(f"{name}={value}" for name, value in model.constants().items())])

        result = subprocess.run(arguments, stdout=subprocess.PIPE, text=True, timeout=timeout)
        return self._parse_result(result.stdout)

    def _parse_result(self, message: str) -> bool | Optional[float]:
        value = re.search('multi.+?: (.+?)\n', message)
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
        return [Method.ValueIteration]

    def supported_settings(self) -> List[Setting]:
        return [Setting.AbsoluteEpsilon, Setting.RelativeEpsilon]
