class ExtractorError(Exception):
    """Custom exception for errors during the extraction process."""
    def __init__(self, message):
        super().__init__(message)


class URLProcessingError(Exception):
    """Custom exception for errors during URL processing."""
    def __init__(self, message):
        super().__init__(message)
