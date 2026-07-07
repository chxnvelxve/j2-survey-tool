"""Clear, defensive failure — missing/malformed .esx contents."""


class ParseError(Exception):
    def __init__(self, message: str, *, source_name: str | None = None) -> None:
        self.source_name = source_name
        if source_name:
            super().__init__(f"{source_name}: {message}")
        else:
            super().__init__(message)
