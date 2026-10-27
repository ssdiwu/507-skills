"""Shared artifact and screenshot evidence validation for 507-ppt."""
from __future__ import annotations

import zipfile
from xml.etree import ElementTree
from pathlib import Path

from PIL import Image, ImageStat, UnidentifiedImageError
from pptx_svg import validate_svg_fallbacks


def validate_artifact(path: Path, carrier: str) -> None:
    expected_suffix = f".{carrier}"
    if path.suffix.lower() != expected_suffix:
        raise ValueError(f"artifact format does not match carrier {carrier}: {path.name}")
    if carrier == "html":
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise ValueError(f"HTML artifact is unreadable: {path}") from error
        required = ("<!doctype html", '<main id="deck"', 'class="slide')
        if any(token not in content for token in required):
            raise ValueError(f"HTML artifact contract is incomplete: {path}")
        return
    if carrier != "pptx":
        raise ValueError(f"unknown artifact carrier: {carrier}")
    if not zipfile.is_zipfile(path):
        raise ValueError(f"PPTX artifact is not an Open XML package: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            required = {"[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels"}
            slide_names = sorted(name for name in names if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
            if not required.issubset(names) or not slide_names:
                raise ValueError(f"PPTX artifact package is incomplete: {path}")
            try:
                content_types = ElementTree.fromstring(archive.read("[Content_Types].xml"))
                relationships = ElementTree.fromstring(archive.read("_rels/.rels"))
                presentation = ElementTree.fromstring(archive.read("ppt/presentation.xml"))
                ElementTree.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
                for name in slide_names:
                    ElementTree.fromstring(archive.read(name))
            except (KeyError, ElementTree.ParseError) as error:
                raise ValueError(f"PPTX artifact contains invalid Open XML: {path}") from error
    except (OSError, zipfile.BadZipFile) as error:
        raise ValueError(f"PPTX artifact is unreadable: {path}") from error
    office_relationships = [item for item in relationships if str(item.attrib.get("Type", "")).endswith("/officeDocument")]
    overrides = [item.attrib.get("PartName") for item in content_types if item.tag.endswith("Override")]
    presentation_content_type = any(part == "/ppt/presentation.xml" for part in overrides) or any(item.tag.endswith("Default") and item.attrib.get("Extension") == "xml" and str(item.attrib.get("ContentType", "")).endswith("presentation.main+xml") for item in content_types)
    slide_ids = [item for item in presentation.iter() if item.tag.endswith("sldId")]
    if len(office_relationships) != 1 or not presentation_content_type or len(slide_ids) != len(slide_names):
        raise ValueError(f"PPTX artifact package relationships or slide mapping are incomplete: {path}")
    validate_svg_fallbacks(path)


def validate_png(path: Path, label: str = "screenshot", *, minimum_size: tuple[int, int] = (320, 180)) -> None:
    if path.suffix.lower() != ".png":
        raise ValueError(f"{label} must be a PNG file: {path}")
    try:
        with Image.open(path) as source:
            if source.format != "PNG":
                raise ValueError(f"{label} must contain PNG image data: {path}")
            source.load()
            image = source.convert("RGB")
    except (OSError, UnidentifiedImageError) as error:
        raise ValueError(f"{label} is not a readable PNG image: {path}") from error
    width, height = image.size
    if width < minimum_size[0] or height < minimum_size[1]:
        raise ValueError(f"{label} PNG is too small: {path} ({width}x{height})")
    if max(ImageStat.Stat(image).stddev) < 1:
        raise ValueError(f"{label} PNG is visually blank: {path}")
