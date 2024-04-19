from abc import ABC
from typing import List

from scripts.model.model import Model
from scripts.tools.tool import Tool, Method


class ActivityHandler(ABC):
    def start_program(self):
        pass

    def stop_program(self):
        pass

    def start_value_iteration(self, tool: Tool, model: Model):
        pass

    def start_value_iteration_epsilon(self, epsilon: float):
        pass

    def start_linear_programming(self, tool: Tool, model: Model):
        pass

    def start_approximation(self, tool: Tool, method: Method, model: Model):
        pass

    def start_approximation_iteration(self, iteration: int, total_iterations: int):
        pass

    def start_query(self, tool: Tool, method: Method, model: Model):
        pass

    def invalid_model(self, tool: Tool, model: Model):
        pass

    def handle_value_iteration_result(self, tool: Tool, model: Model, absolute_epsilon: bool,
                                      epsilons: List[float], approx_results: List[float], query_results: List[float]):
        pass

    def handle_linear_program_result(self, tool: Tool, model: Model, approx_result: float, query_result: float):
        pass


class SubscribableActivityHandler(ActivityHandler):

    def __init__(self):
        self._activity_handlers: List[ActivityHandler] = []

    def register(self, activity_handler: ActivityHandler):
        self._activity_handlers.append(activity_handler)

    def start_program(self):
        for activity_handler in self._activity_handlers:
            activity_handler.start_program()

    def stop_program(self):
        for activity_handler in self._activity_handlers:
            activity_handler.stop_program()

    def start_value_iteration(self, tool: Tool, model: Model):
        for activity_handler in self._activity_handlers:
            activity_handler.start_value_iteration(tool, model)

    def start_value_iteration_epsilon(self, epsilon: float):
        for activity_handler in self._activity_handlers:
            activity_handler.start_value_iteration_epsilon(epsilon)

    def start_linear_programming(self, tool: Tool, model: Model):
        for activity_handler in self._activity_handlers:
            activity_handler.start_linear_programming(tool, model)

    def start_approximation(self, tool: Tool, method: Method, model: Model):
        for activity_handler in self._activity_handlers:
            activity_handler.start_approximation(tool, method, model)

    def start_approximation_iteration(self, iteration: int, total_iterations: int):
        for activity_handler in self._activity_handlers:
            activity_handler.start_approximation_iteration(iteration, total_iterations)

    def start_query(self, tool: Tool, method: Method, model: Model):
        for activity_handler in self._activity_handlers:
            activity_handler.start_query(tool, method, model)

    def invalid_model(self, tool: Tool, model: Model):
        for activity_handler in self._activity_handlers:
            activity_handler.invalid_model(tool, model)

    def handle_value_iteration_result(self, tool: Tool, model: Model, absolute_epsilon: bool,
                                      epsilons: List[float], approx_results: List[float], query_results: List[float]):
        for activity_handler in self._activity_handlers:
            activity_handler.handle_value_iteration_result(tool, model, absolute_epsilon,
                                                           epsilons, approx_results, query_results)

    def handle_linear_program_result(self, tool: Tool, model: Model, approx_result: float, query_result: float):
        for activity_handler in self._activity_handlers:
            activity_handler.handle_linear_program_result(tool, model, approx_result, query_result)


logger = SubscribableActivityHandler()
