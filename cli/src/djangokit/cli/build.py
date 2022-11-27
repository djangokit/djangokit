import dataclasses
import os.path
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import djangokit.core
from djangokit.core.build import build
from djangokit.core.render import render
from djangokit.core.utils import make_request
from typer import Option
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .app import app, state
from .django import configure_settings_module
from .utils.console import Console


@app.command(name="build")
def build_command(
    watch: bool = Option(False, help="Watch files and rebuild automatically?"),
    join: bool = Option(False, help="Only relevant with --watch"),
):
    """Build front end bundle (CSR)

    The CSR bundle is *not* request dependent.

    """
    configure_settings_module()
    console = state.console
    minify = state.env == "production"

    console.header("Building front end (CSR)")
    build(minify=minify)
    console.print()

    if watch:
        core_dir = Path(djangokit.core.__path__[0])
        app_dir = state.settings.app_dir

        handlers = [
            Handler(callable=build, kwargs={"minify": minify}),
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


@app.command(name="render")
def render_command(path: str = "/"):
    """Render front end (SSR)

    The SSR bundle *is* request dependent--in particular, on the request
    path.

    """
    configure_settings_module()
    minify = state.env == "production"
    render(make_request(path), minify=minify)


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
