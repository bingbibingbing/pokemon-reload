from __future__ import annotations

from pathlib import Path
from typing import Iterable
import argparse
import json

from PIL import Image, ImageDraw, ImageFont


DEFAULT_FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
)
DEFAULT_FONT_SIZE = 16
DEFAULT_LINE_SPACING = 4
DEFAULT_FILL = (255, 255, 255, 255)
DEFAULT_ALPHA_THRESHOLD = 96


def make_line_key(folder: str, filename: str, line_number: int) -> str:
    return f"{folder}__{filename}__{line_number}"


def resolve_font_path(font_path: Path | None = None) -> Path:
    if font_path is not None:
        return font_path
    for candidate in DEFAULT_FONT_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("no supported Chinese font found in Windows font directory")


def _measure_lines(lines: Iterable[str], font: ImageFont.FreeTypeFont, line_spacing: int) -> tuple[list[tuple[str, tuple[int, int, int, int]]], tuple[int, int]]:
    probe = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    measured: list[tuple[str, tuple[int, int, int, int]]] = []
    width = 1
    height = 0

    line_list = list(lines)
    for index, line in enumerate(line_list):
        bbox = draw.textbbox((0, 0), line or " ", font=font)
        measured.append((line, bbox))
        width = max(width, bbox[2] - bbox[0])
        height += bbox[3] - bbox[1]
        if index + 1 < len(line_list):
            height += line_spacing

    return measured, (width, max(height, 1))


def render_bitmap_text(
    text: str,
    output_path: Path,
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
    line_spacing: int = DEFAULT_LINE_SPACING,
    alpha_threshold: int = DEFAULT_ALPHA_THRESHOLD,
) -> tuple[int, int]:
    lines = text.split("#")
    font = ImageFont.truetype(str(resolve_font_path(font_path)), font_size)
    measured, size = _measure_lines(lines, font, line_spacing)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    y = 0
    for index, (line, bbox) in enumerate(measured):
        draw.text((-bbox[0], y - bbox[1]), line or " ", font=font, fill=DEFAULT_FILL)
        y += bbox[3] - bbox[1]
        if index + 1 < len(measured):
            y += line_spacing

    alpha = image.getchannel("A")
    hardened_alpha = alpha.point(lambda value: 255 if value >= alpha_threshold else 0)
    image.putalpha(hardened_alpha)
    bbox = image.getbbox()
    if bbox is not None:
        image = image.crop(bbox)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return image.size


def render_manifest(
    manifest_path: Path,
    output_dir: Path,
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
    line_spacing: int = DEFAULT_LINE_SPACING,
) -> list[tuple[str, tuple[int, int]]]:
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    rendered: list[tuple[str, tuple[int, int]]] = []
    for entry in entries:
        key = entry.get("key") or make_line_key(entry["folder"], entry["filename"], entry["line"])
        output_path = output_dir / f"{key}.png"
        size = render_bitmap_text(
            entry["text"],
            output_path,
            font_path=font_path,
            font_size=font_size,
            line_spacing=line_spacing,
        )
        rendered.append((key, size))
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--font-path", type=Path)
    parser.add_argument("--font-size", type=int, default=DEFAULT_FONT_SIZE)
    parser.add_argument("--line-spacing", type=int, default=DEFAULT_LINE_SPACING)
    args = parser.parse_args()

    rendered = render_manifest(
        args.manifest,
        args.output_dir,
        font_path=args.font_path,
        font_size=args.font_size,
        line_spacing=args.line_spacing,
    )
    for key, size in rendered:
        print(f"{key} {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
