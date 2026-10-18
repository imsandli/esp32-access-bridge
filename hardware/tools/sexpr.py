"""Minimal S-expression reader/writer for KiCad files.

Atoms are kept as Python ``str``; quoted strings are wrapped in :class:`QStr`
so they round-trip with quotes. Lists are plain Python lists.
"""

from __future__ import annotations


class QStr(str):
    """A string that must be written quoted."""


def parse(text: str):
    pos = 0
    n = len(text)

    def skip_ws():
        nonlocal pos
        while pos < n and text[pos] in " \t\r\n":
            pos += 1

    def read():
        nonlocal pos
        skip_ws()
        c = text[pos]
        if c == "(":
            pos += 1
            out = []
            while True:
                skip_ws()
                if text[pos] == ")":
                    pos += 1
                    return out
                out.append(read())
        if c == '"':
            pos += 1
            buf = []
            while True:
                c = text[pos]
                if c == "\\":
                    buf.append(text[pos + 1])
                    pos += 2
                    continue
                if c == '"':
                    pos += 1
                    return QStr("".join(buf))
                buf.append(c)
                pos += 1
        start = pos
        while pos < n and text[pos] not in ' \t\r\n()"':
            pos += 1
        return text[start:pos]

    return read()


def _fmt_atom(a) -> str:
    if isinstance(a, QStr):
        return '"' + a.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(a, bool):
        return "yes" if a else "no"
    if isinstance(a, float):
        s = f"{a:.4f}".rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return str(a)


def dumps(node, indent: int = 0) -> str:
    if not isinstance(node, list):
        return _fmt_atom(node)
    if not node:
        return "()"
    simple = all(not isinstance(x, list) for x in node)
    if simple:
        return "(" + " ".join(_fmt_atom(x) for x in node) + ")"
    pad = "\t" * (indent + 1)
    parts = ["(" + _fmt_atom(node[0])]
    for x in node[1:]:
        if isinstance(x, list):
            parts.append("\n" + pad + dumps(x, indent + 1))
        else:
            parts.append(" " + _fmt_atom(x))
    parts.append("\n" + "\t" * indent + ")")
    return "".join(parts)


def find(node, key):
    """Return first child list whose head is ``key``."""
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def find_all(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]
