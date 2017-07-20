from trading.exceptions.servererror import ServerError


def is_provider_error(error):
    return type(error) in [ConnectionError, ServerError]