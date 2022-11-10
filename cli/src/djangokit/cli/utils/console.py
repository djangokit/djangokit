from rich.console import Console as BaseConsole


class Console(BaseConsole):
    def header(self, text):
        self.rule()
        self.print(text, style="bold", highlight=False)
        self.print()

    def success(self, *args, **kwargs):
        kwargs.setdefault("style", "green")
        return self.print(*args, **kwargs)

    def warning(self, *args, **kwargs):
        kwargs.setdefault("style", "yellow")
        return self.print(*args, **kwargs)

    def error(self, *args, **kwargs):
        kwargs.setdefault("style", "red")
        return self.print(*args, **kwargs)
