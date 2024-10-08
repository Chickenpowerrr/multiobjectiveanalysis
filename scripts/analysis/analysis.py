import math
from typing import Dict, List, Tuple

import numpy as np

from model.model import Model
from output.activity import logger
from tools.tool import Tool, Method


def run_value_iteration_analysis(tool: Tool, model: Model, timeout: int,
                                 approx_infinity: float, approx_precision: float,
                                 min_epsilon: float, max_epsilon: float, epsilon_step: float, absolute_epsilon: bool) \
        -> Tuple[List[float], List[float], List[float]]:
    logger.start_value_iteration(tool, model)
    approx_results = []
    query_results = []
    epsilons = list(np.arange(max_epsilon, min_epsilon, -epsilon_step))

    logger.start_value_iteration_check_early_stop()
    parameters = {'epsilon': epsilons[-1], 'absoluteEpsilon': absolute_epsilon}
    last_approx_result = _run_approximation(tool, Method.ValueIteration, model, timeout, parameters,
                                            approx_infinity, approx_precision)
    last_query_result = _run_query(tool, Method.ValueIteration, model, timeout, parameters)

    for epsilon in epsilons[:-1]:
        logger.start_value_iteration_epsilon(epsilon)
        parameters = {'epsilon': epsilon, 'absoluteEpsilon': absolute_epsilon}
        approx_result = _run_approximation(tool, Method.ValueIteration, model, timeout, parameters,
                                           approx_infinity, approx_precision)
        approx_results.append(approx_result)
        query_result = _run_query(tool, Method.ValueIteration, model, timeout, parameters)
        query_results.append(query_result)

        if last_approx_result == approx_result and last_query_result == query_result:
            break

    epsilons[len(approx_results)] = epsilons[-1]
    approx_results.append(last_approx_result)
    query_results.append(last_query_result)

    return epsilons, approx_results, query_results


def run_linear_programming_analysis(tool: Tool, model: Model, timeout: int,
                                    approx_infinite: float, approx_precision: float) -> Tuple[float, float]:
    logger.start_linear_programming(tool, model)
    approx_result = _run_approximation(tool, Method.LinearProgramming, model, timeout, {},
                                       approx_infinite, approx_precision)
    query_result = _run_query(tool, Method.LinearProgramming, model, timeout, {})

    return approx_result, query_result


def _run_approximation(tool: Tool, method: Method, model: Model, timeout: int, parameters: Dict,
                       approx_infinity: float, approx_precision: float) -> float:
    logger.start_approximation(tool, method, model)

    low = 0
    high = 1 if model.probability() else approx_infinity

    maximize = model.maximize()
    best_bound_model = model.set_value(high if maximize else 0)
    best_bound_result = tool.solve(method, best_bound_model, timeout, parameters)

    if best_bound_result:
        return math.inf if maximize else 0

    worst_model = model.set_value(0 if maximize else high)
    worst_bound_result = tool.solve(method, worst_model, timeout, parameters)

    if not worst_bound_result:
        return False

    iterations = math.ceil(math.log2((high - low) / approx_precision))

    for iteration in range(iterations):
        logger.start_approximation_iteration(iteration + 1, iterations)
        current_target = (high + low) / 2
        current_model = model.set_value(current_target)
        current_result = tool.solve(method, current_model, timeout, parameters)

        if current_result == maximize:
            low = current_target
        else:
            high = current_target
    return (high + low) / 2


def _run_query(tool: Tool, method: Method, model: Model, timeout: int, parameters: Dict) -> float:
    logger.start_query(tool, method, model)
    return tool.solve(method, model, timeout, parameters)
