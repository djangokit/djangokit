class DjangoKitError(Exception):
    pass


class BuildError(DjangoKitError):
    pass


class RenderError(DjangoKitError):
    pass


class RouteError(DjangoKitError):
    pass
