from functools import cached_property

from rich.console import Console as BaseConsole


class Console(BaseConsole):
    @cached_property
    def err_console(self) -> "Console":
        """Attach error console for convenience."""
        return Console(stderr=True)

    def header(self, text):
        self.rule()
        self.print(text, style="bold", highlight=False)
        self.print()

    def info(self, *args, **kwargs):
        kwargs.setdefault("style", "blue")
        return self.print(*args, **kwargs)

    def success(self, *args, **kwargs):
        kwargs.setdefault("style", "green")
        return self.print(*args, **kwargs)

    def warning(self, *args, stderr=False, **kwargs):
        # Prints to stdout by default
        kwargs.setdefault("style", "yellow")
        if stderr:
            return self.err_console.print(*args, **kwargs)
        return self.print(*args, **kwargs)

    def danger(self, *args, **kwargs):
        # Prints to stdout
        kwargs.setdefault("style", "red")
        return self.print(*args, **kwargs)

    def error(self, *args, **kwargs):
        # Prints to stderr
        kwargs.setdefault("style", "red")
        return self.err_console.print(*args, **kwargs)

    def command(self, *args, **kwargs):
        kwargs.setdefault("style", "bold")
        return self.print(*args, **kwargs)
