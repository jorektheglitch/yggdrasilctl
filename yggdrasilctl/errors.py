class APIError(Exception):
    "Base class for Yggdrasil admin API related errors."

class APIUnreachable(APIError):
    "Exception raised in case of unsucessful attemption to connect to API."
