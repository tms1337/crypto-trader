class TypeChecker:
    @staticmethod
    def check_type(x, asserted_type):
        if not type(x) is asserted_type and not issubclass(type(x), asserted_type):
            raise TypeError("Object %s should be of type %s" %
                            (x, asserted_type))