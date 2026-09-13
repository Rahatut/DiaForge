import argparse

from pathlib import Path

from .parser import parse

from .layout import auto_layout

from .render_svg import render


def main():

    parser = argparse.ArgumentParser(
        description="DiaForge diagram compiler"
    )

    parser.add_argument(
        "input",
        help="Input .dia file",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="diagram.svg",
        help="Output SVG file",
    )

    args = parser.parse_args()


    source = Path(
        args.input
    ).read_text(
        encoding="utf-8"
    )


    diagram = parse(source)

    diagram = auto_layout(
        diagram
    )


    svg = render(
        diagram
    )


    Path(
        args.output
    ).write_text(
        svg,
        encoding="utf-8"
    )


    print(
        f"Wrote {args.output}"
    )


if __name__ == "__main__":

    main()