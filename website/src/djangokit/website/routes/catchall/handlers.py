def catchall(request, *args, **kwargs):
    return 404, {
        "explanation": "Not Found",
        "detail": "The requested path was not found",
        "path": request.path,
    }
