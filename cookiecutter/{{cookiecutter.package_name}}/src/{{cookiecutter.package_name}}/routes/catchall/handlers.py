def catchall(request, *args, **kwargs):
    """Return a 404 for ALL requests."""
    return 404, {
        "explanation": "Not Found",
        "detail": "The requested path was not found",
        "path": request.path,
    }
