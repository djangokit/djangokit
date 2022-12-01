import dataclasses
import os.path
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import djangokit.core
from djangokit.core.build import make_client_bundle, make_server_bundle, render_bundle
from djangokit.core.http import make_request
from typer import Option
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .app import app, state
from .django import configure_settings_module
from .utils.console import Console


@app.command()
def build_client(
    ssr: bool = Option(True, envvar="DJANGOKIT_SSR"),
    minify: bool = True,
    watch: bool = Option(False, help="Watch files and rebuild automatically?"),
    join: bool = Option(False, help="Only relevant with --watch"),
):
    """Build front end bundle

    The front end bundle is *not* request dependent.

    .. note::
        By default, the front end bundle is configured to hydrate
        server-rendered markup. You can use the `--no-ssr` anti-flag to
        enable client side-only rendering--i.e., configure the bundle to
        render into the React root instead.

    """
    configure_settings_module(DJANGOKIT_SSR=ssr)
    console = state.console

    build_kwargs = {
        "env": state.env,
        "minify": minify,
        "source_map": minify,
        "quiet": state.quiet,
    }

    console.header("Building front end (CSR)")
    if not ssr:
        console.warning("SSR disabled")
    make_client_bundle(**build_kwargs)
    console.print()

    if watch:
        core_dir = Path(djangokit.core.__path__[0])
        app_dir = state.settings.app_dir

        handlers = [
            Handler(callable=make_client_bundle, kwargs=build_kwargs),
        ]

        event_handlers = [
            WatchEventHandler(core_dir, handlers, state.console),
            WatchEventHandler(app_dir, handlers, state.console),
        ]

        observer = Observer()

        for event_handler in event_handlers:
            console.info(f"Watching {event_handler.root_dir}")
            observer.schedule(event_handler, event_handler.root_dir, recursive=True)

        observer.start()

        if join:
            try:
                while observer.is_alive():
                    observer.join(1)
            finally:
                observer.stop()
                observer.join()


@app.command()
def render_markup(path: str = "/"):
    """Render markup for the specified request path"""
    configure_settings_module()
    request = make_request(path)
    minify = state.env == "production"
    render_kwargs = {
        "env": state.env,
        "minify": minify,
        "source_map": minify,
        "quiet": state.quiet,
    }
    bundle_path = make_server_bundle(request, **render_kwargs)
    markup = render_bundle(bundle_path)
    print(markup, flush=True)


@dataclasses.dataclass
class Handler:
    callable: Callable
    args: List[Any] = dataclasses.field(default_factory=list)
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)


class WatchEventHandler(PatternMatchingEventHandler):
    default_extensions = ("js", "jsx", "ts", "tsx")

    def __init__(
        self,
        root_dir: Path,
        handlers: List[Handler],
        console: Console,
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        ignore_directories=True,
        case_sensitive=True,
    ):
        self.root_dir = root_dir
        self.handlers = handlers
        self.console = console

        patterns = patterns or [f"*.{ext}" for ext in self.default_extensions]

        # NOTE: The way watchdog does matching doesn't seem to allow
        #       specifying *anything* under a given directory, hence
        #       this hack to specify multiple sub-levels manually.
        ignore_patterns = ignore_patterns or ["build/*", "build/*/*"]

        super().__init__(
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=ignore_directories,
            case_sensitive=case_sensitive,
        )

    def on_any_event(self, event: FileSystemEvent):
        root_dir = self.root_dir
        rel_src_path = os.path.relpath(event.src_path, root_dir)
        console = self.console
        console.print()
        console.header(f"Rebuilding")
        console.warning(f"Detected change in {root_dir}")
        console.warning(f"File: {rel_src_path}")
        for handler in self.handlers:
            handler.callable(*handler.args, **handler.kwargs)
            console.print()
