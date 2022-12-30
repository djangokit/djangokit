import dataclasses
import os
from fnmatch import fnmatch
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import djangokit.core
from django.conf import settings
from djangokit.core.build import make_client_bundle, make_server_bundle, run_bundle
from djangokit.core.http import make_request
from djangokit.core.serializers import dump_json
from djangokit.core.utils import get_unmasked_csrf_token
from typer import Option
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .app import app, state
from .utils.console import Console


@app.command()
def build_client(
    ssr: bool = True,
    minify: bool = False,
    source_map: bool = True,
    watch: bool = Option(False, help="Watch files and rebuild automatically?"),
    join: bool = Option(True, help="Only relevant with --watch"),
):
    """Build client bundle

    The client bundle is *not* request dependent.

    .. note::
        By default, the front end bundle is configured to hydrate
        server-rendered markup. You can use the `--no-ssr` anti-flag to
        enable client side-only rendering--i.e., configure the bundle to
        render into the React root instead.

    """
    settings.DJANGOKIT.ssr = ssr
    console = state.console

    bundle_kwargs = {
        "env": state.env,
        "settings_file": state.settings_file,
        "minify": minify,
        "source_map": source_map,
        "quiet": state.quiet,
    }

    console.header("Building client bundle")
    make_client_bundle(**bundle_kwargs)
    console.print()

    if watch and not os.getenv("RUN_MAIN"):
        event_handler, observer = get_build_watch_event_handler()
        event_handler.add_handler(
            Handler(
                callable=make_client_bundle,
                kwargs=bundle_kwargs,
                exclude_patterns=["*/server.app.*", "*/server.main.*"],
            ),
        )
        join_observer(observer, join)


@app.command()
def build_server(
    path="/",
    minify: bool = False,
    source_map: bool = False,
    watch: bool = Option(False, help="Watch files and rebuild automatically?"),
    join: bool = Option(False, help="Only relevant with --watch"),
):
    """Build server bundle

    The serer bundle *is* request dependent.

    """
    console = state.console

    bundle_args = [make_request(path=path)]

    bundle_kwargs = {
        "env": state.env,
        "settings_file": state.settings_file,
        "minify": minify,
        "source_map": source_map,
        "quiet": state.quiet,
    }

    console.header("Building server bundle")
    make_server_bundle(*bundle_args, **bundle_kwargs)
    console.print()

    if watch and not os.getenv("RUN_MAIN"):
        event_handler, observer = get_build_watch_event_handler()
        event_handler.add_handler(
            Handler(
                callable=make_server_bundle,
                args=bundle_args,
                kwargs=bundle_kwargs,
                exclude_patterns=["*/client.app.*", "*/client.main.*"],
            ),
        )
        join_observer(observer, join)


@app.command()
def render_markup(path: str = "/", csrf_token=None):
    """Render markup for the specified request path"""
    from django.contrib.auth.models import AnonymousUser

    request = make_request(path=path)

    if csrf_token is None:
        # NOTE: The CSRF token is arbitrary
        csrf_token = get_unmasked_csrf_token(request)

    user = AnonymousUser()
    user_data = settings.DJANGOKIT.current_user_serializer(user)
    user_json = dump_json(user_data)

    data: Any = {}
    data_json = dump_json(data)

    bundle_kwargs = {
        "env": state.env,
        "minify": False,
        "source_map": False,
        "quiet": state.quiet,
    }
    bundle = make_server_bundle(request, **bundle_kwargs)
    markup = run_bundle(bundle, [path, user_json, data_json])
    markup = markup.replace("__DJANGOKIT_CSRF_TOKEN__", csrf_token)
    print(markup, flush=True)


@dataclasses.dataclass
class Handler:
    callable: Callable
    args: List[Any] = dataclasses.field(default_factory=list)
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)
    exclude_patterns: List[str] = dataclasses.field(default_factory=list)

    @property
    def name(self):
        return self.callable.__name__


class WatchEventHandler(PatternMatchingEventHandler):
    default_extensions = ("js", "jsx", "ts", "tsx")

    def __init__(
        self,
        console: Console,
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        ignore_directories=True,
        case_sensitive=True,
    ):
        self.handlers: List[Handler] = []
        self.console = console

        patterns = patterns or [f"*.{ext}" for ext in self.default_extensions]
        ignore_patterns = ignore_patterns or ["build/*"]

        super().__init__(
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=ignore_directories,
            case_sensitive=case_sensitive,
        )

    def add_handler(self, handler: Handler):
        self.handlers.append(handler)

    def on_any_event(self, event: FileSystemEvent):
        path = event.src_path
        console = self.console
        console.print()
        console.header("File change detected")
        console.warning(f"Changed file:\n  {path}")
        for handler in self.handlers:
            if any(fnmatch(path, pattern) for pattern in handler.exclude_patterns):
                console.warning(
                    f"\nSkipping handler {handler.name} because file is excluded"
                )
            else:
                console.info(f"\nRunning handler {handler.name}")
                try:
                    handler.callable(*handler.args, **handler.kwargs)
                    console.print()
                except Exception as exc:
                    console.error(
                        f"\nError encountered during rebuild while running "
                        f"handler {handler}:\n\n{exc}"
                    )


@lru_cache(maxsize=None)
def get_build_watch_event_handler() -> Tuple[WatchEventHandler, Observer]:
    """Get the singleton build watch event handler."""
    handler = WatchEventHandler(state.console)
    core_dir = Path(djangokit.core.__path__[0])
    package_dir = settings.DJANGOKIT.package_dir
    observer = Observer()

    for d in (core_dir, package_dir):
        state.console.info(f"Watching {d}")
        observer.schedule(handler, d, recursive=True)

    observer.start()

    return handler, observer


def join_observer(observer: Observer, join: bool):
    """Join the observer to the main thread if `join`.

    This will cause the observer to block.

    """
    if join:
        try:
            while observer.is_alive():
                observer.join(1)
        finally:
            observer.stop()
            observer.join()
