from util.asserting import TypeChecker


class StateVector:
    def __init__(self, dimension_n, initial_value=None):
        TypeChecker.check_type(dimension_n, int)
        self.dimension_n = dimension_n

        TypeChecker.check_one_of_types(initial_value, [tuple, list])
        for v in initial_value:
            TypeChecker.check_one_of_types(v, [float, int])

        assert len(initial_value) == dimension_n, \
            "Initial value must be vector of length %d" % dimension_n
        self.value = tuple(initial_value)

    def get_value(self):
        return self.value

    def set_value(self, value):
        TypeChecker.check_one_of_types(value, [tuple, list])
        for v in value:
            TypeChecker.check_one_of_types(v, [float, int])

        assert len(value) == self.dimension_n, \
            "Value must be vector of length %d" % self.dimension_n

        self.value = tuple(value)

    def set_random_value(self):
        pass
