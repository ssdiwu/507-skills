"""Media-quality regressions, separate from manifest bookkeeping tests."""
from __future__ import annotations

import hashlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from pptx_svg import prepare_svg_fallbacks, svg_pictures, validate_svg_fallbacks

ROOT = Path(__file__).resolve().parents[1]
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 200 100"><rect width="100" height="100" fill="#ff0000"/><rect x="100" width="100" height="100" fill="#0000ff"/></svg>'


def png(size: tuple[int, int], color: str) -> bytes:
    output = io.BytesIO()
    Image.new("RGBA", size, color).save(output, format="PNG")
    return output.getvalue()


def sample(path: Path, bitmap: bytes, svg: bytes = SVG, *, svg_target: str = "/ppt/media/image.svg") -> None:
    # Minimal image package for the media validator; not a forged complete PPTX/report.
    with ZipFile(path, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:s="http://schemas.microsoft.com/office/drawing/2016/SVG/main"><p:pic><p:blipFill><a:blip r:embed="png"><a:extLst><a:ext uri="test"><s:svgBlip r:embed="svg"/></a:ext></a:extLst></a:blip></p:blipFill><p:spPr><a:xfrm><a:ext cx="3600000" cy="3600000"/></a:xfrm></p:spPr></p:pic></p:sld>')
        archive.writestr("ppt/slides/_rels/slide1.xml.rels", f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="png" Target="/ppt/media/image.png"/><Relationship Id="svg" Target="{svg_target}"/></Relationships>')
        archive.writestr("ppt/media/image.png", bitmap)
        archive.writestr("ppt/media/image.svg", svg)


class SvgFallbackTests(unittest.TestCase):
    def test_rejects_placeholder_transparent_corrupt_and_distorted_fallbacks(self) -> None:
        cases = [
            (png((1, 1), "#00000000"), "placeholder"),
            (png((100, 100), "#00000000"), "transparent"),
            (b"not PNG", "failed"),
            (png((200, 100), "red"), "aspect"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "media.pptx"
            for bitmap, message in cases:
                with self.subTest(message=message):
                    sample(path, bitmap)
                    with self.assertRaisesRegex(ValueError, message):
                        validate_svg_fallbacks(path)

    def test_rejects_missing_vector_relationship(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "media.pptx"
            sample(path, png((100, 100), "red"), svg_target="/ppt/media/missing.svg")
            with self.assertRaisesRegex(ValueError, "relationship"):
                validate_svg_fallbacks(path)

    def test_rendered_fallback_preserves_source_content_and_contains_without_stretch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "media.pptx"
            sample(path, png((1, 1), "#00000000"))
            with ZipFile(path) as archive:
                unchanged = {name: archive.read(name) for name in archive.namelist() if name != "ppt/media/image.png"}
            self.assertEqual(prepare_svg_fallbacks(path), 1)
            self.assertEqual(validate_svg_fallbacks(path), 1)
            with ZipFile(path) as archive:
                self.assertEqual({name: archive.read(name) for name in unchanged}, unchanged)
                with Image.open(io.BytesIO(archive.read("ppt/media/image.png"))) as image:
                    image = image.convert("RGBA")
                    self.assertEqual(image.size, (1000, 1000))
                    self.assertEqual(image.getpixel((250, 500)), (255, 0, 0, 255))
                    self.assertEqual(image.getpixel((750, 500)), (0, 0, 255, 255))
                    self.assertEqual(image.getpixel((500, 100))[3], 0)
                    left, top, right, bottom = image.getchannel("A").getbbox()
                    self.assertAlmostEqual((right - left) / (bottom - top), 2, places=2)

    def test_external_svg_reference_fails_without_replacing_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "media.pptx"
            sample(path, png((100, 100), "red"), b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.invalid/private.png"/></svg>')
            before = hashlib.sha256(path.read_bytes()).digest()
            with self.assertRaisesRegex(ValueError, "self-contained"):
                validate_svg_fallbacks(path)
            with self.assertRaisesRegex(ValueError, "self-contained"):
                prepare_svg_fallbacks(path)
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), before)

    def test_shared_bitmap_consumer_is_not_silently_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "media.pptx"
            sample(path, png((1, 1), "#00000000"))
            with ZipFile(path) as archive:
                parts = [(part, archive.read(part.filename)) for part in archive.infolist()]
            with ZipFile(path, "w") as archive:
                for part, content in parts:
                    if part.filename == "ppt/slides/slide1.xml":
                        content = content.replace(b'</p:sld>', b'<p:pic><p:blipFill><a:blip r:embed="png"/></p:blipFill></p:pic></p:sld>')
                    archive.writestr(part, content)
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "non-SVG"):
                prepare_svg_fallbacks(path)
            self.assertEqual(path.read_bytes(), before)

    def test_published_pptx_contains_real_fallback_and_fresh_screenshots(self) -> None:
        # This is the real generation boundary; the manifest tests never repair their inputs.
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "generated.pptx"
            evidence = Path(temporary) / "evidence"
            result = subprocess.run([
                sys.executable, "-B", str(ROOT / "scripts/generate_pptx.py"),
                "--input", str(ROOT / "examples/system-prototypes/prototype-content.json"),
                "--plan", str(ROOT / "examples/system-prototypes/candidate-a-swiss.visual-plan.json"),
                "--prototype-candidate", "--output", str(output), "--evidence-dir", str(evidence),
            ], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(validate_svg_fallbacks(output), 1)
            with ZipFile(output) as archive:
                picture = svg_pictures(archive)[0]
                self.assertAlmostEqual(picture.width / picture.height, 1280 / 720, places=4)
            self.assertEqual(len(list(evidence.glob("slide-*.png"))), 3)


if __name__ == "__main__":
    unittest.main()
