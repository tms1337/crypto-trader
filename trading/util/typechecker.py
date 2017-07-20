class TypeChecker:
    @staticmethod
    def check_type(x, asserted_type):
        if type(x) is asserted_type:
            raise TypeError("Object %s should be of type %s" %
                            (x, asserted_type))