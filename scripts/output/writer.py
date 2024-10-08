import time
import os.path
from typing import List

from error.error import ModelError
from model.model import Model
from output.activity import ActivityHandler
from tools.tool import Tool, Method


class ResultActivityHandler(ActivityHandler):

    def __init__(self):
        self._path = f'../results/{int(round(time.time() * 1000))}'
        self._value_iteration_absolute_exists = False
        self._value_iteration_relative_exists = False
        self._linear_programming_exists = False
        self._errors_exist = False

    def start_program(self):
        os.makedirs(self._path, exist_ok=True)
        with open('settings.yml', 'r') as default:
            with open(os.path.join(self._path, 'settings.yml'), 'w') as settings:
                settings.write(''.join(default.readlines()))

    def handle_value_iteration_result(self, tool: Tool, model: Model, absolute_epsilon: bool, epsilons: List[float],
                                      approx_results: List[float], query_results: List[float]):
        if len(approx_results) == 0 or len(query_results) == 0:
            return
        if not all(approx_result == approx_results[0] and query_result == query_results[0]
               for approx_result, query_result in zip(approx_results, query_results)):
            path = os.path.join(self._path, f'graph-{model.name()}-vi-{"abs" if absolute_epsilon else "rel"}'
                                            f'-{tool.__class__.__name__}.dat')
            with open(path, 'w') as file:
                file.write('epsilon approx query\n')
                for row in zip(epsilons, approx_results, query_results):
                    file.write(f'{" ".join(map(str, row))}\n')
            return

        path = os.path.join(self._path, f'value-iteration-{"abs" if absolute_epsilon else "rel"}.dat')
        if ((absolute_epsilon and not self._value_iteration_absolute_exists)
                or (not absolute_epsilon and not self._value_iteration_relative_exists)):
            self._value_iteration_absolute_exists = self._value_iteration_absolute_exists or absolute_epsilon
            self._value_iteration_relative_exists = self._value_iteration_relative_exists or not absolute_epsilon
            with open(path, 'w') as file:
                file.write(f'model tool approx query\n')
        with open(path, 'a') as file:
            file.write(f'{model.name()} {tool.__class__.__name__} {approx_results[0]} {query_results[0]}\n')

    def handle_linear_program_result(self, tool: Tool, model: Model, approx_result: float, query_result: float):
        path = os.path.join(self._path, f'linear-programming.dat')
        if not self._linear_programming_exists:
            self._linear_programming_exists = True
            with open(path, 'w') as file:
                file.write('model tool approx query\n')
        with open(path, 'a') as file:
            file.write(f'{model.name()} {tool.__class__.__name__} {approx_result} {query_result}\n')

    def invalid_model(self, tool: Tool, model: Model, method: Method, error: ModelError):
        path = os.path.join(self._path, f'errors.txt')
        if not self._errors_exist:
            self._errors_exist = True
            with open(path, 'w') as file:
                file.write(f'model tool error\n')
        with open(path, 'a') as file:
            file.write(f'{model.name()} {tool.__class__.__name__} {method.name} {error.__class__.__name__}\n')
