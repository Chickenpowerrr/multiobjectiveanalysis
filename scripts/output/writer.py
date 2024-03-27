import time
import os.path
from typing import List

from scripts.model.model import Model
from scripts.output.activity import ActivityHandler
from scripts.tools.tool import Tool


class ResultActivityHandler(ActivityHandler):

    def __init__(self):
        self._path = f'../results/{int(round(time.time() * 1000))}'

    def start_program(self):
        os.makedirs(self._path, exist_ok=True)
        with open('settings.yml', 'r') as default:
            with open(os.path.join(self._path, 'settings.yml'), 'w') as settings:
                settings.write(''.join(default.readlines()))

    def handle_value_iteration_result(self, tool: Tool, model: Model, epsilons: List[float],
                                      approx_results: List[float], query_results: List[float]):
        path = os.path.join(self._path, f'{model.name()}-vi-{tool.__class__.__name__}.dat')
        with open(path, 'w') as file:
            for row in zip(epsilons, approx_results, query_results):
                file.write(f'{" ".join(map(str, row))}\n')

    def handle_linear_program_result(self, tool: Tool, model: Model, approx_result: float, query_result: float):
        path = os.path.join(self._path, f'{model.name()}-lp-{tool.__class__.__name__}.dat')
        with open(path, 'w') as file:
            file.write(f'{approx_result} {query_result}')
