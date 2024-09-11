import os.path
from subprocess import TimeoutExpired
from typing import List

import yaml
from jsonschema.validators import validate

from analysis import analysis
from error.error import ModelError, ConvergeError
from model.loader import load_models
from output.activity import logger
from output.progress import ProgressActivityHandler
from output.writer import ResultActivityHandler
from tools.modest import Modest
from tools.epmc import Epmc
from tools.prism import Prism
from tools.storm import Storm
from tools.tool import Tool, Method, Setting

SUPPORTED_TOOLS = {'storm': Storm, 'prism': Prism, 'epmc': Epmc, 'modest': Modest}


def get_or_create_settings():
    if not os.path.exists('settings.yml'):
        with open('settings-default.yml', 'r') as default:
            with open('settings.yml', 'w') as settings:
                settings.write(''.join(default.readlines()))
    with open('settings.yml', 'r') as settings:
        return yaml.safe_load(settings)


def validate_settings(settings) -> List[Tool]:
    with open('setting-schema.yml', 'r') as schema:
        validate(settings, yaml.safe_load(schema))
    tools = []
    for tool, properties in settings['tools'].items():
        if tool != 'modest':
            continue
        if tool == 'epmc':
            parsed_tool = SUPPORTED_TOOLS[tool](os.path.expanduser(properties['path']),
                                                os.path.expanduser(properties['java']),
                                                os.path.expanduser(properties['spot']))
        else:
            parsed_tool = SUPPORTED_TOOLS[tool](os.path.expanduser(properties['path']))

        assert parsed_tool.validate(), f"Invalid path for '{tool}': '{properties['path']}'"
        tools.append(parsed_tool)
    return tools


def run_experiments(models, tools, settings):
    approx_infinity = settings['analysis']['approximation']['infinity']
    approx_precision = settings['analysis']['approximation']['precision']
    min_epsilon = settings['analysis']['valueiteration']['epsilon']['min']
    max_epsilon = settings['analysis']['valueiteration']['epsilon']['max']
    epsilon_step = settings['analysis']['valueiteration']['epsilon']['step']
    timeout = settings['analysis']['timeout']

    for model in models:
        for tool in tools:
            for method in tool.supported_methods():
                try:
                    if method == Method.ValueIteration:
                        epsilon_settings = []
                        epsilon_settings += [True] if Setting.AbsoluteEpsilon in tool.supported_settings() else []
                        epsilon_settings += [False] if Setting.RelativeEpsilon in tool.supported_settings() else []

                        for epsilon_setting in epsilon_settings:
                            epsilons, approx_results, query_results = (
                                analysis.run_value_iteration_analysis(tool, model, timeout,
                                                                      approx_infinity, approx_precision,
                                                                      min_epsilon, max_epsilon, epsilon_step,
                                                                      epsilon_setting))
                            logger.handle_value_iteration_result(tool, model, epsilon_setting,
                                                                 epsilons, approx_results, query_results)
                    if method == Method.LinearProgramming:
                        approx_result, query_result = (
                            analysis.run_linear_programming_analysis(tool, model, timeout,
                                                                     approx_infinity, approx_precision))
                        logger.handle_linear_program_result(tool, model, approx_result, query_result)
                except TimeoutExpired:
                    logger.invalid_model(tool, model, ConvergeError())
                except ModelError as error:
                    logger.invalid_model(tool, model, error)


if __name__ == '__main__':
    settings = get_or_create_settings()
    tools = validate_settings(settings)
    models = load_models()

    logger.register(ProgressActivityHandler())
    logger.register(ResultActivityHandler())
    logger.start_program()

    run_experiments(models, tools, settings)

    logger.stop_program()
