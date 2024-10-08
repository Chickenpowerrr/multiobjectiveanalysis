from error.error import ModelError
from model.model import Model
from output.activity import ActivityHandler
from tools.tool import Tool, Method


class ProgressActivityHandler(ActivityHandler):
    def start_value_iteration(self, tool: Tool, model: Model):
        print(f'Starting VI {model.name()} ({tool.__class__.__name__})')

    def start_value_iteration_check_early_stop(self):
        print(f'Starting VI early stop check')

    def start_value_iteration_epsilon(self, epsilon: float):
        print(f'\tCurrent epsilon: {epsilon:.5f}')

    def start_linear_programming(self, tool: Tool, model: Model):
        print(f'Starting LP {model.name()} ({tool.__class__.__name__})')

    def start_approximation(self, tool: Tool, method: Method, model: Model):
        print(f'\t\tStarting approx {model.name()} ({tool.__class__.__name__}, {method.name})')

    def start_approximation_iteration(self, iteration: int, total_iterations: int):
        print(f'\t\t\tApprox iteration: {iteration}/{total_iterations}')

    def start_query(self, tool: Tool, method: Method, model: Model):
        print(f'\t\tStarting query {model.name()} ({tool.__class__.__name__}, {method.name})')

    def invalid_model(self, tool: Tool, model: Model, method: Method, error: ModelError):
        print(f'Invalid model for {tool.__class__.__name__} detected: {model.name()} ({error.__class__.__name__})')
