__all__ = ["UnimplementedError", "unimplemented"]


class UnimplementedError(Exception):
    def __init__(self, message: str = "This feature is not implemented yet."):
        self.message = message

    def __str__(self):
        return f"Unimplemented Error: {self.message}"


def unimplemented(message: str | None = None) -> None:
    if message is None:
        raise UnimplementedError()
    else:
        raise UnimplementedError(message)


def strip_indent(text: str, *, keep_last_newline: bool = False) -> str:
    lines = text.strip().splitlines()
    if not lines:
        return ""

    new_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line[0] == "|":
            new_line = stripped_line[1:]
        elif stripped_line[0:1] == r"\|":
            new_line = stripped_line[1:]
        else:
            new_line = line
        new_lines.append(new_line)
    content = "\n".join(new_lines).strip()
    if (
        keep_last_newline
        and text
        and text[-1] == "\n"
        and content
        and content[-1] != "\n"
    ):
        content += "\n"
    return content
