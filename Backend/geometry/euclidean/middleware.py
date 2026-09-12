import os

from django.http import HttpResponse


class FrontendCorsMiddleware:
    """Add CORS headers for the configured frontend origin."""

    def __init__(self, get_response):
        self.get_response = get_response
        configured_origins = os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        self.allowed_origins = {
            origin.strip() for origin in configured_origins.split(",") if origin.strip()
        }

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        origin = request.headers.get("Origin")
        if origin in self.allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        response["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        response["Vary"] = "Origin"
        return response
