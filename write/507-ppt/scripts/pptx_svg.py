"""Keep native SVG pictures and provide real, proportional PNG fallbacks.

Preparation runs on a closed, unpublished PPTX candidate and replaces it atomically.
Validation reads the embedded bytes without depending on officecli's platform-specific
issue detector. CLI usage: python3 pptx_svg.py FILE.pptx [FILE.pptx ...].
"""
from __future__ import annotations

import argparse
import base64
import io
import os
import posixpath
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PIL import Image

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "svg": "http://schemas.microsoft.com/office/drawing/2016/SVG/main",
}
EMBED = f"{{{NS['r']}}}embed"


def image_aspect_ratio(path: Path) -> float:
    if path.suffix.lower() != ".svg":
        with Image.open(path) as image:
            return image.width / image.height
    root = ET.fromstring(path.read_bytes())
    units = {"": 1, "px": 1, "pt": 96 / 72, "pc": 16, "in": 96, "cm": 96 / 2.54, "mm": 96 / 25.4}

    def length(value: str) -> float:
        match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(px|pt|pc|in|cm|mm)?\s*", value)
        return float(match[1]) * units[match[2] or ""] if match else 0

    width, height = length(root.get("width", "")), length(root.get("height", ""))
    if width <= 0 or height <= 0:
        viewbox = [float(value) for value in re.split(r"[\s,]+", root.get("viewBox", "").strip()) if value]
        if len(viewbox) == 4:
            width, height = viewbox[2:]
    if width <= 0 or height <= 0:
        raise ValueError(f"SVG has no usable intrinsic aspect ratio: {path.name}")
    return width / height


@dataclass(frozen=True)
class SvgPicture:
    slide: str
    svg: str
    png: str
    width: int
    height: int
    png_relation: str


def svg_pictures(archive: ZipFile) -> list[SvgPicture]:
    names = set(archive.namelist())
    result = []
    for slide in sorted(name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)):
        rel_path = posixpath.join(posixpath.dirname(slide), "_rels", posixpath.basename(slide) + ".rels")
        rels = {item.attrib["Id"]: item.attrib for item in ET.fromstring(archive.read(rel_path))} if rel_path in names else {}

        def target(element: ET.Element) -> str:
            relation = rels.get(element.get(EMBED), {})
            value = relation.get("Target", "")
            resolved = posixpath.normpath(value.lstrip("/") if value.startswith("/") else posixpath.join(posixpath.dirname(slide), value))
            if not value or relation.get("TargetMode") == "External" or resolved not in names:
                raise ValueError(f"SVG picture relationship is missing or external: {slide}")
            return resolved

        for picture in ET.fromstring(archive.read(slide)).findall(".//p:pic", NS):
            vector = picture.find(".//svg:svgBlip", NS)
            if vector is None:
                continue
            bitmap = picture.find("p:blipFill/a:blip", NS)
            extent = picture.find("p:spPr/a:xfrm/a:ext", NS)
            if bitmap is None or extent is None:
                raise ValueError(f"SVG picture has no fallback or extent: {slide}")
            width, height = int(extent.get("cx", "0")), int(extent.get("cy", "0"))
            if width <= 0 or height <= 0:
                raise ValueError(f"SVG picture has an invalid extent: {slide}")
            svg, png = target(vector), target(bitmap)
            if svg == png or not png.lower().endswith(".png"):
                raise ValueError(f"SVG picture needs a separate PNG fallback: {slide}")
            result.append(SvgPicture(slide, svg, png, width, height, bitmap.attrib[EMBED]))
    return result


def check_fallback_consumers(archive: ZipFile, pictures: list[SvgPicture]) -> None:
    """Never overwrite an image part used by a non-SVG picture/background."""
    expected = Counter((picture.slide, picture.png_relation) for picture in pictures)
    fallback_parts = {picture.png for picture in pictures}
    for name in archive.namelist():
        if not name.endswith(".rels"):
            continue
        directory, filename = posixpath.split(name)
        owner = posixpath.join(posixpath.dirname(directory), filename[:-5]) if filename != ".rels" else ""
        for relation in ET.fromstring(archive.read(name)):
            value = relation.get("Target", "")
            target = posixpath.normpath(value.lstrip("/") if value.startswith("/") else posixpath.join(posixpath.dirname(owner), value))
            if relation.get("TargetMode") == "External" or target not in fallback_parts:
                continue
            if not owner.endswith(".xml") or owner not in archive.namelist():
                raise ValueError("SVG fallback image part has an unsupported additional consumer")
            relation_id = relation.get("Id")
            references = sum(
                1 for element in ET.fromstring(archive.read(owner)).iter()
                for key, item in element.attrib.items()
                if key.startswith("{" + NS["r"] + "}") and item == relation_id
            )
            if references != expected[(owner, relation_id)]:
                raise ValueError("SVG fallback image part is shared with a non-SVG consumer")


def validate_self_contained_svg(svg: bytes) -> None:
    if re.search(rb"<!DOCTYPE|<!ENTITY|<\?xml-stylesheet|@import", svg, re.I):
        raise ValueError("SVG requires a self-contained static document")
    root = ET.fromstring(svg)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("vector part is not SVG")
    # Generation renders an inert <img>; validation enforces the same dependency contract.
    for node in root.iter():
        for name, value in node.attrib.items():
            if name.rsplit("}", 1)[-1] == "href" and not value.startswith(("#", "data:")):
                raise ValueError("SVG requires self-contained image references")
    for match in re.finditer(rb"url\(\s*['\"]?([^)'\"]+)", svg, re.I):
        if not match.group(1).startswith((b"#", b"data:")):
            raise ValueError("SVG requires self-contained CSS references")


def validate_svg_fallbacks(path: Path) -> int:
    with ZipFile(path) as archive:
        pictures = svg_pictures(archive)
        for picture in pictures:
            try:
                validate_self_contained_svg(archive.read(picture.svg))
                with Image.open(io.BytesIO(archive.read(picture.png))) as bitmap:
                    bitmap.load()
                    if bitmap.format != "PNG" or min(bitmap.size) <= 1:
                        raise ValueError("PNG fallback is a placeholder")
                    if bitmap.convert("RGBA").getchannel("A").getbbox() is None:
                        raise ValueError("PNG fallback is fully transparent")
                    # A one-pixel rounding allowance, not a visual distortion threshold.
                    expected = picture.width / picture.height
                    if abs(bitmap.width - bitmap.height * expected) > 1 + expected:
                        raise ValueError("PNG fallback aspect differs from the picture viewport")
            except (ET.ParseError, OSError, ValueError) as error:
                raise ValueError(f"{picture.slide} SVG fallback failed: {error}") from error
    return len(pictures)


def prepare_svg_fallbacks(path: Path) -> int:
    with ZipFile(path) as archive:
        pictures = svg_pictures(archive)
        if not pictures:
            return 0
        check_fallback_consumers(archive, pictures)
        source = {picture.svg: archive.read(picture.svg) for picture in pictures}
    targets: dict[str, tuple[bytes, int, int]] = {}
    for picture in pictures:
        svg = source[picture.svg]
        validate_self_contained_svg(svg)
        scale = min(100 / 360000, 2048 / max(picture.width, picture.height))
        width, height = max(2, round(picture.width * scale)), max(2, round(picture.height * scale))
        value = (svg, width, height)
        if picture.png in targets and targets[picture.png] != value:
            raise ValueError("shared SVG fallback has conflicting picture viewports")
        targets[picture.png] = value

    from browser_tools import find_chrome
    from html_browser_evidence import CdpSession

    chrome = find_chrome()
    if chrome is None:
        raise ValueError("Chrome/Chromium is required for SVG fallback generation")
    with tempfile.TemporaryDirectory(prefix=".svg-fallback-", dir=path.parent) as temporary:
        directory = Path(temporary)
        session = CdpSession(chrome, directory)
        replacements = {}
        try:
            session.command("Network.enable")
            session.command("Network.setBlockedURLs", {"urls": ["http://*", "https://*", "file://*"]})
            session.command("Emulation.setDefaultBackgroundColorOverride", {"color": {"r": 0, "g": 0, "b": 0, "a": 0}})
            for target, (svg, width, height) in targets.items():
                uri = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
                html = '<style>html,body{margin:0;width:100%;height:100%;background:transparent}img{display:block;width:100%;height:100%;object-fit:contain}</style>' + f'<img src="{uri}">'
                session.set_viewport(width, height)
                session.navigate("data:text/html;base64," + base64.b64encode(html.encode()).decode())
                session.evaluate("document.images[0].decode()", await_promise=True)
                shot = session.command("Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": False})
                replacements[target] = base64.b64decode(shot["data"])
        finally:
            session.close()
            if session.process.stderr:
                session.process.stderr.close()
        candidate = directory / path.name
        with ZipFile(path) as original, ZipFile(candidate, "w") as archive:
            for item in original.infolist():
                content = replacements[item.filename] if item.filename in replacements else original.read(item.filename)
                archive.writestr(item, content)
        validate_svg_fallbacks(candidate)
        os.replace(candidate, path)
    return len(pictures)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.files:
        try:
            count = validate_svg_fallbacks(path)
        except (OSError, ValueError) as error:
            raise SystemExit(str(error)) from error
        print(f"SVG fallback contract passed: {path} ({count} pictures)")


if __name__ == "__main__":
    main()
