import argparse

from pathlib import Path

from .parser import parse

from .layout import auto_layout

from .render_svg import render, render_png


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
        help="Output file (SVG or PNG)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["svg", "png"],
        default=None,
        help="Output format (auto-detected from extension)",
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


    output_path = Path(args.output)
    if args.format == "png" or (
        args.format is None
        and output_path.suffix.lower() == ".png"
    ):

        png = render_png(diagram)

        output_path.write_bytes(png)

        print(
            f"Wrote {args.output}"
        )
    else:

        svg = render(diagram)

        output_path.write_text(
            svg,
            encoding="utf-8",
        )

        print(
            f"Wrote {args.output}"
        )


if __name__ == "__main__":

    main()