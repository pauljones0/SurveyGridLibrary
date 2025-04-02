class CoordinateParseException(Exception):
    """Exception raised while parsing coordinates."""
    def __init__(self, message, inner_exception=None):
        super().__init__(message)
        self.inner_exception = inner_exception
