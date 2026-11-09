#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                   __        __
#?             _____/ /___  __/ /__
#?            / ___/ __/ / / / / _ \
#?           (__  ) /_/ /_/ / /  __/
#?          /____/\__/\__, /_/\___/
#?                   /____/
#?
#? Name:        style.py
#? Purpose:     Apply the project's house style to Python files: figlet header (Name / Purpose / Author / Created),
#?              column-aligned imports, '=' at column 28, trailing comments at column 87, #?--- separators and
#?              3-line section banners. The module docstring becomes the Purpose text. Files that already carry the
#?              header are skipped. Every result is checked: the code's AST must be unchanged.
#?              Usage:  python scripts/style.py FILE [FILE ...]      (needs: pip install pyfiglet)
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  ast
import  io
import  re
import  sys
import  textwrap
import  tokenize
from    pathlib                     import  Path
#?----------------------------------------------------------------------------------------------------------------------------------------
WIDTH                       = 138                                                      # total width of #?---- separator lines
COL                         = 28                                                       # absolute column of '=' in assignments
COMMENT_COL                 = 87                                                       # absolute column of trailing comments
MOD_W                       = 28                                                       # module column width in 'from' imports
CREATED                     = "05/09/2019"
AUTHOR                      = "Mohamed Gueni ( mohamedgueni@outlook.com)"
#?----------------------------------------------------------------------------------------------------------------------------------------
def sep(indent: str = "") -> str:
    return indent + "#?" + "-" * (WIDTH - len(indent) - 2)
#?----------------------------------------------------------------------------------------------------------------------------------------
SEP_RE                      = re.compile(r"^\s*#\?-{20,}$")
BANNER_A                    = re.compile(r"^(\s*)#\s*[-=]{6,}\s*(.*?)\s*[-=]*\s*$")
BANNER_B                    = re.compile(r"^(\s*)#\s*(.+?)\s*[-=]{6,}\s*$")
#?----------------------------------------------------------------------------------------------------------------------------------------
def figlet(name: str) -> list[str]:
    from    pyfiglet                    import  Figlet
    art                     = [l.rstrip() for l in Figlet(font="slant", width=300).renderText(name).split("\n")]
    while art and not art[-1].strip():
        art.pop()
    while art and not art[0].strip():
        art.pop(0)
    return art
#?----------------------------------------------------------------------------------------------------------------------------------------
def header(path: Path, purpose: str) -> list[str]:
    name                    = path.parent.name if path.stem in ("__init__", "__main__") else path.stem
    out                     = ["#!/usr/bin/env python", "# coding=utf-8", "#? " + "-" * 79, "#?"]
    out                    += [("#?          " + l).rstrip() for l in figlet(name)]
    out                    += ["#?", "#?", f"#? Name:        {path.name}"]
    paras                   = [p.strip() for p in purpose.strip().split("\n\n") if p.strip()] or [path.stem]
    first                   = True
    for para in paras:
        for line in textwrap.wrap(" ".join(l.strip() for l in para.splitlines()), 110):
            out.append(("#? Purpose:     " if first else "#?              ") + line)
            first           = False
    out                    += ["#?", f"#? Author:      {AUTHOR}", "#?", f"#? Created:     {CREATED}",
                               "#? " + "-" * 79, "#? " + "-" * 79]
    return out
#?----------------------------------------------------------------------------------------------------------------------------------------
def string_lines(src: str) -> set[int]:
    """Line numbers lying inside (after the first line of) multi-line string tokens."""
    inside                  = set()
    kinds                   = {tokenize.STRING, getattr(tokenize, "FSTRING_MIDDLE", -1), getattr(tokenize, "FSTRING_END", -1)}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in kinds and tok.end[0] > tok.start[0]:
            inside.update(range(tok.start[0] + 1, tok.end[0] + 1))
    return inside
#?----------------------------------------------------------------------------------------------------------------------------------------
def ch(line: str, byte_off: int) -> int:
    return len(line.encode("utf-8")[:byte_off].decode("utf-8"))
#?----------------------------------------------------------------------------------------------------------------------------------------
def format_imports(src: str) -> str:
    tree                    = ast.parse(src)
    lines                   = src.split("\n")
    comments: dict[int, list[str]] = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            comments.setdefault(tok.start[0], []).append(tok.string)
    nodes                   = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    mods                    = ["." * n.level + (n.module or "") for n in nodes if isinstance(n, ast.ImportFrom)]
    width                   = max([MOD_W] + [len(m) + 2 for m in mods])
    alias                   = lambda a: a.name + (f" as {a.asname}" if a.asname else "")
    for n in sorted(nodes, key=lambda n: -n.lineno):
        indent              = lines[n.lineno - 1][: n.col_offset]
        if indent.strip():
            continue
        cmts                = [c for ln in range(n.lineno, n.end_lineno + 1) for c in comments.get(ln, [])]
        suffix              = ("  " + "  ".join(cmts)) if cmts else ""
        if isinstance(n, ast.Import):
            new             = [f"{indent}import  {', '.join(alias(a) for a in n.names)}{suffix}"]
        else:
            head            = f"{indent}from    {('.' * n.level + (n.module or '')).ljust(width)}import  "
            names           = [alias(a) for a in n.names]
            one             = head + ", ".join(names)
            if len(one) + len(suffix) <= WIDTH + 12:
                new         = [one + suffix]
            else:
                cont        = " " * (len(head) + 1)
                new, cur    = [], head + "("
                for i, name in enumerate(names):
                    piece   = name + (", " if i < len(names) - 1 else ")")
                    if len(cur) + len(piece.rstrip()) > WIDTH + 12 and cur.strip() != head.strip() + " (":
                        new.append(cur.rstrip())
                        cur = cont
                    cur    += piece
                new.append(cur.rstrip() + suffix)
        lines[n.lineno - 1: n.end_lineno] = new
    return "\n".join(lines)
#?----------------------------------------------------------------------------------------------------------------------------------------
def align_assignments(src: str) -> str:
    tree                    = ast.parse(src)
    lines                   = src.split("\n")
    in_str                  = string_lines(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            lhs_node, value, op = n.targets[0], n.value, "="
        elif isinstance(n, ast.AnnAssign) and n.value is not None:
            lhs_node, value, op = n.annotation, n.value, "="
        elif isinstance(n, ast.AugAssign):
            lhs_node, value, op = n.target, n.value, None
        else:
            continue
        ln                  = n.lineno
        if lhs_node.end_lineno != ln or value.lineno != ln or ln in in_str:
            continue
        line                = lines[ln - 1]
        if line[:ch(line, n.col_offset)].strip():
            continue
        lhs_end, v_col      = ch(line, lhs_node.end_col_offset), ch(line, value.col_offset)
        token               = line[lhs_end:v_col].strip()
        if op == "=" and token != "=":
            continue
        if op is None:
            if not re.fullmatch(r"[-+*/%&|^@<>]{1,3}=|//=|\*\*=", token):
                continue
            op              = token
        lhs                 = line[:lhs_end].rstrip()
        target_w            = COL - (len(op) - 1)
        lhs                 = lhs.ljust(target_w) if len(lhs) < target_w else lhs + " "
        new                 = lhs + op + " " + line[v_col:]
        delta               = len(new) - len(line)
        lines[ln - 1]       = new
        hanging             = line.rstrip().endswith(("(", "[", "{"))                  # hanging indent keeps its own column
        conts               = range(ln + 1, n.end_lineno + 1)
        if delta and not hanging and conts and not any(c in in_str for c in conts):
            for c in conts:
                text        = lines[c - 1]
                if not text.strip():
                    continue
                if delta > 0:
                    lines[c - 1] = " " * delta + text
                else:
                    lead    = len(text) - len(text.lstrip(" "))
                    lines[c - 1] = text[min(lead, -delta):]
    return "\n".join(lines)
#?----------------------------------------------------------------------------------------------------------------------------------------
def align_trailing_comments(src: str) -> str:
    lines                   = src.split("\n")
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type != tokenize.COMMENT:
            continue
        ln, col             = tok.start
        line                = lines[ln - 1]
        code                = line[:col].rstrip()
        if not code.strip():
            continue
        pad                 = COMMENT_COL if len(code) < COMMENT_COL - 1 else len(code) + 2
        lines[ln - 1]       = code.ljust(pad) + line[col:]
    return "\n".join(lines)
#?----------------------------------------------------------------------------------------------------------------------------------------
def convert_banners(src: str) -> str:
    lines                   = src.split("\n")
    in_str                  = string_lines(src)
    out: list[str]          = []
    i                       = 0
    while i < len(lines):
        line                = lines[i]
        m                   = None if (i + 1) in in_str or line.lstrip().startswith("#?") else \
            (BANNER_A.match(line) or BANNER_B.match(line))
        if not m:
            out.append(line)
            i              += 1
            continue
        indent, title       = m.group(1), (m.group(2) or "").strip()
        if not title:
            nxt             = BANNER_A.match(lines[i + 2]) if i + 2 < len(lines) else None
            if nxt and not nxt.group(2) and re.match(r"^\s*#\s*[^-=\s].*$", lines[i + 1]):
                title       = lines[i + 1].strip().lstrip("#").strip()
                i          += 2
            else:
                out.append(sep(indent))
                i          += 1
                continue
        title               = title[0].upper() + title[1:]
        out                += [sep(indent), f"{indent}#? {title}", sep(indent)] if len(indent) <= 4 else [f"{indent}#? {title}"]
        i                  += 1
    return "\n".join(out)
#?----------------------------------------------------------------------------------------------------------------------------------------
def top_level_separators(src: str) -> str:
    tree                    = ast.parse(src)
    lines                   = src.split("\n")
    kind                    = lambda n: ("import" if isinstance(n, (ast.Import, ast.ImportFrom)) else
                                         "def" if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                                         else "other")
    inserts                 = []
    for prev, cur in zip(tree.body, tree.body[1:]):
        kp, kc              = kind(prev), kind(cur)
        if kc == "def" or kp == "def" or (kp == "import" and kc != "import"):
            start           = min([cur.lineno] + [d.lineno for d in getattr(cur, "decorator_list", [])])
            while start - 2 >= 0 and lines[start - 2].lstrip().startswith("#") and not SEP_RE.match(lines[start - 2]):
                start      -= 1
            inserts.append(start)
    for ln in sorted(set(inserts), reverse=True):
        lines.insert(ln - 1, sep())
    out: list[str]          = []
    for line in ("\n".join(lines).rstrip("\n") + "\n" + sep()).split("\n"):
        if line == sep():
            while out and not out[-1].strip():
                out.pop()
            if out and out[-1] == sep():
                continue
        elif not line.strip() and out and out[-1] == sep():
            continue
        out.append(line)
    return "\n".join(out)
#?----------------------------------------------------------------------------------------------------------------------------------------
def strip_doc(tree: ast.Module) -> ast.Module:
    first                   = tree.body[0] if tree.body else None
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        tree.body           = tree.body[1:]
    return tree
#?----------------------------------------------------------------------------------------------------------------------------------------
def process(path: Path) -> bool:
    src                     = path.read_text(encoding="utf-8")
    if src.startswith("#!/usr/bin/env python\n# coding=utf-8\n#? ---"):
        print(f"skip (already styled): {path}")
        return False
    original                = ast.dump(strip_doc(ast.parse(src)))
    tree                    = ast.parse(src)
    lines                   = src.split("\n")
    purpose                 = ""
    first                   = tree.body[0] if tree.body else None
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        purpose             = ast.get_docstring(tree) or ""
        del lines[first.lineno - 1: first.end_lineno]
    while lines and (not lines[0].strip() or lines[0].startswith("#!") or "coding" in lines[0][:40]):
        lines.pop(0)
    body                    = "\n".join(lines)
    for step in (format_imports, align_assignments, align_trailing_comments, convert_banners, top_level_separators):
        body                = step(body)
    result                  = ("\n".join(header(path, purpose)) + "\n" + body.lstrip("\n")).rstrip("\n") + "\n"
    if ast.dump(strip_doc(ast.parse(result))) != original:
        raise SystemExit(f"AST changed for {path} - nothing written")
    path.write_text(result, encoding="utf-8", newline="\n")
    print(f"styled: {path}")
    return True
#?----------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__ or "usage: python scripts/style.py FILE [FILE ...]")
    for arg in sys.argv[1:]:
        process(Path(arg))
#?----------------------------------------------------------------------------------------------------------------------------------------
