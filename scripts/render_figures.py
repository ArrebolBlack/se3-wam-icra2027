"""Regenerate PDF assets from their editable SVG sources.

Local raster images are inlined before conversion.  This avoids URI-resolution
failures when the repository lives under a non-ASCII Windows path while keeping
the checked-in SVG portable and human-editable.
"""

import base64
import mimetypes
from pathlib import Path
import re

from cairosvg import svg2pdf


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"


_LOCAL_IMAGE = re.compile(
    r'(?P<attr>(?:xlink:)?href)="(?P<path>[^"#]+\.(?:png|jpe?g|webp))"',
    re.IGNORECASE,
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


def main() -> None:
    for source in sorted(FIGURES.glob("*.svg")):
        target = source.with_suffix(".pdf")
        svg2pdf(
            bytestring=_inline_local_images(source),
            write_to=str(target),
        )
        print(f"rendered {source.name} -> {target.name}")


if __name__ == "__main__":
    main()
