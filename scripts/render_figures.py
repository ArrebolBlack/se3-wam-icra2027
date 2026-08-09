"""Regenerate vector PDF assets from their editable SVG sources."""

from pathlib import Path

from cairosvg import svg2pdf


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"


def main() -> None:
    for source in sorted(FIGURES.glob("*.svg")):
        target = source.with_suffix(".pdf")
        svg2pdf(url=str(source), write_to=str(target))
        print(f"rendered {source.name} -> {target.name}")


if __name__ == "__main__":
    main()

