"""Regenerate PDF assets from their editable SVG sources.

Local raster images are inlined before conversion.  This avoids URI-resolution
failures when the repository lives under a non-ASCII Windows path while keeping
the checked-in SVG portable and human-editable.
"""

import base64
import mimetypes
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

try:
    from cairosvg import svg2pdf
except (ImportError, OSError):
    svg2pdf = None


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"


_LOCAL_IMAGE = re.compile(
    r'(?P<attr>(?:xlink:)?href)="(?P<path>[^"#]+\.(?:png|jpe?g|webp))"',
    re.IGNORECASE,
)
_VIEWBOX = re.compile(
    rb'viewBox="\s*0\s+0\s+(?P<width>[0-9.]+)\s+(?P<height>[0-9.]+)\s*"'
)


def _inline_local_images(source: Path) -> bytes:
    svg = source.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        relative = match.group("path")
        if relative.startswith(("data:", "http://", "https://")):
            return match.group(0)
        image = (source.parent / relative).resolve()
        mime = mimetypes.guess_type(image.name)[0] or "application/octet-stream"
        payload = base64.b64encode(image.read_bytes()).decode("ascii")
        return f'{match.group("attr")}="data:{mime};base64,{payload}"'

    return _LOCAL_IMAGE.sub(replace, svg).encode("utf-8")


def _find_chromium() -> Path | None:
    for command in ("chrome", "msedge", "chromium"):
        resolved = shutil.which(command)
        if resolved:
            return Path(resolved)
    for path in (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ):
        if path.exists():
            return path
    raise RuntimeError("CairoSVG is unavailable and no Chromium browser was found")


def _svg2pdf_chromium(source: Path, target: Path, svg: bytes) -> None:
    match = _VIEWBOX.search(svg)
    if not match:
        raise ValueError(f"missing 0 0 width height viewBox in {source}")
    width = match.group("width").decode("ascii")
    height = match.group("height").decode("ascii")
    payload = base64.b64encode(svg).decode("ascii")
    html = f"""<!doctype html>
<meta charset="utf-8">
<style>
@page {{ size: {width}px {height}px; margin: 0; }}
html, body {{ width: {width}px; height: {height}px; margin: 0; overflow: hidden; }}
img {{ display: block; width: {width}px; height: {height}px; }}
</style>
<img src="data:image/svg+xml;base64,{payload}">
"""
    browser = _find_chromium()
    with tempfile.TemporaryDirectory(prefix="se3wam-figure-") as temporary:
        temp = Path(temporary)
        page = temp / "figure.html"
        profile = temp / "chrome-profile"
        page.write_text(html, encoding="utf-8")
        target.unlink(missing_ok=True)
        command = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={target}",
            page.resolve().as_uri(),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0 or not target.exists():
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"Chromium SVG conversion failed for {source}: {detail}")


def main() -> None:
    for source in sorted(FIGURES.glob("*.svg")):
        target = source.with_suffix(".pdf")
        svg = _inline_local_images(source)
        if svg2pdf is not None:
            svg2pdf(bytestring=svg, write_to=str(target))
        else:
            _svg2pdf_chromium(source, target, svg)
        print(f"rendered {source.name} -> {target.name}")


if __name__ == "__main__":
    main()
