from typing import Dict, Tuple

from frozendict import frozendict


class Model:
    def __init__(self, name: str, file: str, property: str, constants: Dict[str, str]):
        self._name = name
        self._file = file
        self._property = property
        self._constants = frozendict(constants)

    def name(self):
        return self._name

    def file(self):
        return self._file

    def property(self):
        return self._property

    def constants(self):
        return self._constants

    def maximize(self):
        return 'max=?' in self._property

    def set_value(self, value: float):
        property = self._property.replace('max=?', f'>={value}').replace('min=?', f'<={value}')
        return Model(f'{self._name}-{value:.5f}', self._file, property, self._constants)
