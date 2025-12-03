from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

try:  # pragma: no cover - optional dependency handled at runtime
    from lxml import etree as LET
except ImportError:  # pragma: no cover
    LET = None


class XLFParseError(Exception):
    """Raised when an XLF payload cannot be parsed or repaired."""


@dataclass
class ParsedXLF:
    tree: ET.ElementTree
    recovered: bool = False


def parse_xlf_document(file_path: Path) -> ParsedXLF:
    """Parse an XLF file, attempting recovery when mismatched tags are present."""
    try:
        tree = ET.parse(file_path)
        return ParsedXLF(tree=tree, recovered=False)
    except ET.ParseError as exc:
        if LET is None:
            raise XLFParseError(str(exc)) from exc

        parser = LET.XMLParser(recover=True, remove_blank_text=False)
        try:
            recovered_tree = LET.parse(str(file_path), parser)
        except LET.XMLSyntaxError as recover_exc:  # pragma: no cover - mirrors ET failure
            raise XLFParseError(str(recover_exc)) from recover_exc

        serialized = LET.tostring(recovered_tree.getroot(), encoding="utf-8")
        root = ET.fromstring(serialized)
        tree = ET.ElementTree(root)
        return ParsedXLF(tree=tree, recovered=True)
