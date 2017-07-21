class TypeChecker:
    @staticmethod
    def check_type(x, asserted_type):
        if not type(x) is asserted_type and not issubclass(type(x), asserted_type):
            return

    @staticmethod
    def check_one_of_types(x, asserted_types):
        for asserted_type in asserted_types:
            if type(x) is asserted_type or issubclass(type(x), asserted_type):
                return

        raise TypeError("Object %s should be one of the types %s" %
                        (x, asserted_types))