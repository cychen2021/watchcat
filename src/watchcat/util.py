__all__ = ["UnimplementedError", "unimplemented", "strip_indent", "protect_indent"]


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


def strip_indent(text: str, *, keep_last_ws: bool = False) -> str:
    lines = text.strip().splitlines()
    if not lines:
        return ""

    new_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line[0:1] == "||":
            new_line = line[: len(line) - len(stripped_line)] + "|" + stripped_line[2:]
        elif stripped_line[0] == "|":
            new_line = stripped_line[1:]
        else:
            new_line = line
        new_lines.append(new_line)
    if keep_last_ws:
        content = "\n".join(new_lines).lstrip()
        content += text[: len(content) - len(text.lstrip())]
    else:
        content = "\n".join(new_lines).strip()
    return content


def protect_indent(text: str) -> str:
    lines = text.splitlines()

    new_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith("|"):
            new_line = line[: len(line) - len(stripped_line)] + "||" + stripped_line[1:]
        else:
            new_line = line
        new_lines.append(new_line)
    return "\n".join(new_lines)
