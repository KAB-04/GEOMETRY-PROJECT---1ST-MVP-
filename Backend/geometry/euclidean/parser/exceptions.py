class ParserError(Exception):
    """Base parser exception."""
    pass


class InvalidGeminiResponse(ParserError):
    """Raised when Gemini returns an invalid response."""
    pass


class GeminiConnectionError(ParserError):
    """Raised when Gemini cannot be reached."""
    pass


class ProviderUnreachable(ParserError):
    """Raised when a provider cannot be reached because of DNS/network/timeout failure."""
    pass


class ProviderAccessDenied(ParserError):
    """Raised when a provider or its edge rejects access."""
    pass


class ProviderRateLimited(ParserError):
    """Raised when a provider rate limit is reached."""
    pass


class ProviderResponseError(ParserError):
    """Raised when a provider returns an unusable response."""
    pass


class UnsupportedGeometryOperation(ParserError):
    """Raised when the interpreted intent is not safely executable."""
    pass


class ProviderUnavailable(ParserError):
    """Raised when a provider is temporarily busy or unavailable."""
    pass