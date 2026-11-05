#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                  ____
#?            ___  / __/_  __________
#?           / _ \/ /_/ / / / ___/ _ \
#?          /  __/ __/ /_/ (__  )  __/
#?          \___/_/  \__,_/____/\___/
#?
#?
#? Name:        efuse.py
#? Purpose:     Parse ``espefuse summary --format json`` output and export it.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  csv
import  json
from    dataclasses                 import  dataclass
from    pathlib                     import  Path
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class EfuseField:
    name: str
    category: str
    description: str
    value: str
    raw_value: str
    readable: bool
    writeable: bool
    block: str
    bit_len: str
    efuse_type: str

    @property
    def access(self) -> str:
        return f"{'R' if self.readable else '-'}/{'W' if self.writeable else '-'}"
#?----------------------------------------------------------------------------------------------------------------------------------------
COLUMNS                     = ["Name", "Category", "Value", "Raw", "R/W", "Block", "Description"]
#?----------------------------------------------------------------------------------------------------------------------------------------
def _fmt(value) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return str(value)
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_summary(data: dict | str) -> list[EfuseField]:
    if isinstance(data, str):
        data                = json.loads(data)
    fields                  = []
    for key, info in data.items():
        if not isinstance(info, dict):
            continue
        fields.append(EfuseField(
            name=str(info.get("name", key)),
            category=str(info.get("category", "")),
            description=str(info.get("description", "")),
            value=_fmt(info.get("value")),
            raw_value=_fmt(info.get("raw_value")),
            readable=bool(info.get("readable", True)),
            writeable=bool(info.get("writeable", True)),
            block=_fmt(info.get("block")),
            bit_len=_fmt(info.get("bit_len")),
            efuse_type=_fmt(info.get("efuse_type")),
        ))
    fields.sort(key=lambda f: (f.category, f.name))
    return fields
#?----------------------------------------------------------------------------------------------------------------------------------------
def load_summary_file(path: str | Path) -> list[EfuseField]:
    text                    = Path(path).read_text(encoding="utf-8", errors="replace")
    # Be tolerant of any banner text before the JSON object.
    start                   = text.find("{")
    if start < 0:
        raise ValueError("No eFuse JSON data found")
    return parse_summary(text[start:])
#?----------------------------------------------------------------------------------------------------------------------------------------
def _row(f: EfuseField) -> list[str]:
    return [f.name, f.category, f.value, f.raw_value, f.access, f.block, f.description]
#?----------------------------------------------------------------------------------------------------------------------------------------
def export(fields: list[EfuseField], path: str | Path) -> Path:
    """Export to ``.xlsx`` (if openpyxl is available) or ``.csv``."""
    path                    = Path(path)
    if path.suffix.lower() == ".xlsx":
        try:
            from    openpyxl                    import  Workbook
            from    openpyxl.styles             import  Font
        except ImportError:
            path            = path.with_suffix(".csv")
        else:
            wb              = Workbook()
            ws              = wb.active
            ws.title        = "eFuses"
            ws.append(COLUMNS)
            for cell in ws[1]:
                cell.font   = Font(bold=True)
            for f in fields:
                ws.append(_row(f))
            for col, width in zip("ABCDEFG", (34, 16, 26, 22, 6, 8, 70)):
                ws.column_dimensions[col].width = width
            ws.freeze_panes = "A2"
            wb.save(path)
            return path
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer              = csv.writer(fh)
        writer.writerow(COLUMNS)
        writer.writerows(_row(f) for f in fields)
    return path
#?----------------------------------------------------------------------------------------------------------------------------------------
