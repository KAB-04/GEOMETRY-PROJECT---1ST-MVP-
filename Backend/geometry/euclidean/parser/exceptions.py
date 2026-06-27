class ParserError(Exception):
    """Base parser exception."""
    pass


class InvalidGeminiResponse(ParserError):
    """Raised when Gemini returns an invalid response."""
    pass


class GeminiConnectionError(ParserError):
    """Raised when Gemini cannot be reached."""
    pass