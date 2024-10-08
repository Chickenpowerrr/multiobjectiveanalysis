import os
from typing import List, Dict

from model.model import Model

MODEL_PATH = '../models'


def load_models():
    models = []

    for model_dir_name in os.listdir(MODEL_PATH):
        model_dir = os.path.join(MODEL_PATH, model_dir_name)
        prism_model_file = os.path.join(model_dir, 'model.nm')
        modest_model_file = os.path.join(model_dir, 'model.modest')
        properties_file = os.path.join(model_dir, 'properties.pctl')
        constants_file = os.path.join(model_dir, 'constants.txt')

        if model_dir_name == 'team_formation':
            print(f'Skipping: {model_dir_name}, missing entries...')
            continue

        for pi, property in enumerate(parse_properties(properties_file)):
            constants = parse_constants(constants_file)
            if len(constants) == 0:
                models.append(Model(f'{model_dir_name}-{pi}-0', prism_model_file, modest_model_file, pi, property, {}))
                continue
            for ci, constants in enumerate(constants):
                models.append(Model(f'{model_dir_name}-{pi}-{ci}', prism_model_file, modest_model_file, pi, property, constants))

    return models


def parse_properties(properties_file: str) -> List[str]:
    with open(properties_file, 'r') as properties_file:
        return [line.strip() for line in properties_file.readlines()]


def parse_constants(constants_file: str) -> List[Dict[str, str]]:
    if not os.path.exists(constants_file):
        return [{}]

    with open(constants_file, 'r') as constants_file:
        return [{item.split('=')[0]: item.split('=')[1] for item in line.strip().split(',')}
                for line in constants_file.readlines() if line.strip() != '']
