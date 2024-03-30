import math
from typing import Dict, List, Tuple

import numpy as np

from scripts.model.model import Model
from scripts.output.activity import logger
from scripts.tools.tool import Tool, Method


def run_value_iteration_analysis(tool: Tool, model: Model,
                                 approx_infinity: float, approx_precision: float,
                                 min_epsilon: float, max_epsilon: float, epsilon_step: float) \
        -> Tuple[List[float], List[float], List[float]]:
    logger.start_value_iteration(tool, model)
    approx_results = []
    query_results = []
    epsilons = list(np.arange(max_epsilon, min_epsilon, -epsilon_step))
    for epsilon in epsilons:
        logger.start_value_iteration_epsilon(epsilon)
        approx_result = _run_approximation(tool, Method.ValueIteration, model, {'epsilon': epsilon},
                                           approx_infinity, approx_precision)
        approx_results.append(approx_result)
        query_result = _run_query(tool, Method.ValueIteration, model, {'epsilon': epsilon})
        query_results.append(query_result)
    return epsilons, approx_results, query_results


def run_linear_programming_analysis(tool: Tool, model: Model, approx_infinite: float, approx_precision: float) \
        -> Tuple[float, float]:
    logger.start_linear_programming(tool, model)
    approx_result = _run_approximation(tool, Method.LinearProgramming, model, {}, approx_infinite, approx_precision)
    query_result = _run_query(tool, Method.LinearProgramming, model, {})

    return approx_result, query_result


def _run_approximation(tool: Tool, method: Method, model: Model, parameters: Dict,
                       approx_infinity: float, approx_precision: float) -> float:
    logger.start_approximation(tool, method, model)

    low = 0
    high = 1 if model.probability() else approx_infinity

    maximize = model.maximize()
    bound_model = model.set_value(0 if maximize else high)
    bound_result = tool.solve(method, bound_model, parameters)

    if not bound_result:
        return math.inf if maximize else 0

    iterations = math.ceil(math.log2((high - low) / approx_precision))

    for iteration in range(iterations):
        logger.start_approximation_iteration(iteration + 1, iterations)
        current_target = (high + low) / 2
        current_model = model.set_value(current_target)
        current_result = tool.solve(method, current_model, parameters)

        if current_result == maximize:
            low = current_target
        else:
            high = current_target
    return (high + low) / 2


def _run_query(tool: Tool, method: Method, model: Model, parameters: Dict) -> float:
    logger.start_query(tool, method, model)
    return tool.solve(method, model, parameters)
