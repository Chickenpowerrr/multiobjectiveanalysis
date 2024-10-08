from typing import Dict

from frozendict import frozendict


class Model:
    def __init__(self, name: str, prism_file: str, modest_file: str, property_id: int, prism_property: str, constants: Dict[str, str]):
        self._name = name
        self._prism_file = prism_file
        self._modest_file = modest_file
        self._property_id = property_id
        self._prism_property = prism_property
        self._constants = frozendict(constants)
        self._value = None

    def name(self):
        return self._name

    def prism_file(self):
        return self._prism_file

    def modest_file(self):
        return self._modest_file

    def property_id(self):
        return self._property_id

    def prism_property(self):
        return self._prism_property

    def value(self):
        return self._value

    def constants(self):
        return self._constants

    def maximize(self):
        return 'max=?' in self._prism_property

    def probability(self):
        return 'Pmax' in self._prism_property or 'Pmin' in self._prism_property

    def set_value(self, value: float):
        prism_property = self._prism_property.replace('max=?', f'>={value}').replace('min=?', f'<={value}')
        new_model = Model(f'{self._name}-{value:.5f}', self._prism_file, self._modest_file, self._property_id, prism_property, self._constants)
        new_model._value = value
        return new_model
