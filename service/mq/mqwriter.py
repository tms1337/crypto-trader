from abc import ABC, abstractclassmethod

from util.asserting import TypeChecker


class MQWriter(ABC):
    @abstractclassmethod
    def write(self, key, value):
        TypeChecker.check_type(key, str)
        TypeChecker.check_type(value, str)
