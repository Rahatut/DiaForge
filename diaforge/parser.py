from __future__ import annotations

from typing import Any

from .ast import (
    Cell,
    Diagram,
    Edge,
    Icon,
    Node,
    Port,
    Style,
    Table,
    TextBlock,
    Canvas,
)
from .lexer import Token, lex


class Parser:
    """
    Parser for the DiaForge declarative diagram language.

    Example:

        diagram "Architecture" {

            canvas {
                width: 1400
                height: 800
                background: "#F8FAFC"
                padding: 40
            }

            node api {
                title: "API Server"
                icon: "cpu"
                fill: "#EEF4FF"
                stroke: "#4F46E5"
                radius: 20
                padding: 24
            }

            edge api -> db {
                route: orthogonal
                stroke: "#64748B"
            }
        }
    """

    def __init__(self, text: str):
        self.tokens: list[Token] = list(lex(text))
        self.i = 0

    # ========================================================
    # TOKEN HELPERS
    # ========================================================

    def peek(self) -> Token:
        return self.tokens[self.i]

    def pop(self) -> Token:
        token = self.tokens[self.i]
        self.i += 1
        return token

    def expect(self, value: str) -> Token:
        token = self.pop()

        if token.value != value:
            raise SyntaxError(
                f"Expected {value!r} at position {token.pos}, "
                f"got {token.value!r}"
            )

        return token

    def accept(self, value: str) -> Token | None:
        if self.peek().value == value:
            return self.pop()

        return None

    def error(self, message: str) -> SyntaxError:
        token = self.peek()

        return SyntaxError(
            f"{message} at position {token.pos}"
        )

    # ========================================================
    # PRIMITIVE VALUES
    # ========================================================

    def text(self) -> str:
        """
        Read an identifier or string as text.

        Strings are already decoded by the lexer.
        """

        token = self.pop()

        if token.kind in {"STRING", "ID"}:
            return token.value

        raise self.error(
            f"Expected text, got {token.value!r}"
        )

    def value(self) -> Any:
        """
        Read a scalar value.

        Supported:

            strings
            identifiers
            integers
            floats
        """

        token = self.pop()

        if token.kind in {"STRING", "ID"}:
            return token.value

        if token.kind == "NUMBER":
            if "." in token.value:
                return float(token.value)

            return int(token.value)

        raise self.error(
            f"Unexpected value {token.value!r}"
        )

    # ========================================================
    # PROPERTY BLOCK
    # ========================================================

    def block(self) -> dict[str, Any]:
        """
        Parse:

            {
                key: value
                key: value
            }

        Values are currently scalar.
        """

        values: dict[str, Any] = {}

        self.expect("{")

        while self.peek().value != "}":

            if self.peek().kind == "EOF":
                raise self.error(
                    "Unexpected end of file inside block"
                )

            key_token = self.pop()

            if key_token.kind not in {"ID", "STRING"}:
                raise SyntaxError(
                    f"Expected property name at "
                    f"position {key_token.pos}, "
                    f"got {key_token.value!r}"
                )

            self.expect(":")

            values[key_token.value] = self.value()

            self.accept(";")

        self.expect("}")

        return values

    # ========================================================
    # CANVAS
    # ========================================================

    def parse_canvas(self) -> Canvas:
        props = self.block()

        return Canvas(
            width=self.number(
                props,
                "width",
                1200,
            ),
            height=self.number(
                props,
                "height",
                800,
            ),
            background=self.string(
                props,
                "background",
                "#FFFFFF",
            ),
            padding=self.number(
                props,
                "padding",
                40,
            ),
            font_family=self.string(
                props,
                "font_family",
                "Inter, Arial, sans-serif",
            ),
            font_size=self.number(
                props,
                "font_size",
                14,
            ),
        )

    # ========================================================
    # STYLE
    # ========================================================

    def parse_style(self) -> Style:
        name = self.text()
        props = self.block()

        return Style(
            name=name,
            values=props,
        )

    # ========================================================
    # ICON
    # ========================================================

    def parse_icon_value(self, value: Any) -> Icon | None:
        if value is None:
            return None

        return Icon(
            name=str(value),
            size=24,
            color=None,
            position="left",
        )

    # ========================================================
    # PORT
    # ========================================================

    def parse_port(
        self,
        name: str,
        props: dict[str, Any],
    ) -> Port:

        return Port(
            name=name,
            side=self.string(
                props,
                "side",
                "east",
            ),
            offset=self.number(
                props,
                "offset",
                0.5,
            ),
            radius=self.number(
                props,
                "radius",
                4,
            ),
            visible=self.boolean(
                props,
                "visible",
                False,
            ),
        )

    # ========================================================
    # TABLE CELL
    # ========================================================

    def parse_cell(
        self,
        props: dict[str, Any],
    ) -> Cell:

        icon = None

        if "icon" in props:
            icon = Icon(
                name=str(props["icon"]),
                size=self.number(
                    props,
                    "icon_size",
                    20,
                ),
                color=(
                    str(props["icon_color"])
                    if "icon_color" in props
                    else None
                ),
                position=self.string(
                    props,
                    "icon_position",
                    "left",
                ),
            )

        text = None

        if "text" in props:
            text = TextBlock(
                text=str(props["text"]),
                size=self.number(
                    props,
                    "text_size",
                    14,
                ),
                weight=self.string(
                    props,
                    "text_weight",
                    "400",
                ),
                color=self.string(
                    props,
                    "text_color",
                    "#16233B",
                ),
                align=self.string(
                    props,
                    "align",
                    "left",
                ),
                line_height=self.number(
                    props,
                    "line_height",
                    1.4,
                ),
            )

        return Cell(
            value=self.string(
                props,
                "value",
                "",
            ),
            icon=icon,
            text=text,
            fill=self.optional_string(
                props,
                "fill",
            ),
            stroke=self.optional_string(
                props,
                "stroke",
            ),
            stroke_width=self.number(
                props,
                "stroke_width",
                1,
            ),
            padding=self.number(
                props,
                "padding",
                10,
            ),
            align=self.string(
                props,
                "align",
                "left",
            ),
            valign=self.string(
                props,
                "valign",
                "middle",
            ),
            colspan=self.integer(
                props,
                "colspan",
                1,
            ),
            rowspan=self.integer(
                props,
                "rowspan",
                1,
            ),
        )

    # ========================================================
    # TABLE
    # ========================================================

    def parse_table(
        self,
        props: dict[str, Any],
    ) -> Table:

        rows: list[list[Cell]] = []

        return Table(
            rows=rows,
            padding=self.number(
                props,
                "padding",
                12,
            ),
            row_gap=self.number(
                props,
                "row_gap",
                0,
            ),
            column_gap=self.number(
                props,
                "column_gap",
                0,
            ),
            radius=self.number(
                props,
                "radius",
                12,
            ),
            fill=self.string(
                props,
                "fill",
                "#FFFFFF",
            ),
            stroke=self.string(
                props,
                "stroke",
                "#D6DFEA",
            ),
            stroke_width=self.number(
                props,
                "stroke_width",
                1,
            ),
        )

    # ========================================================
    # NODE
    # ========================================================

    def parse_node(
        self,
        node_id: str,
    ) -> Node:

        props = self.block()

        node = Node(
            id=node_id,

            title=self.string(
                props,
                "title",
                "",
            ),

            icon=(
                str(props["icon"])
                if "icon" in props
                else None
            ),

            icon_size=self.number(
                props,
                "icon_size",
                26,
            ),

            x=self.optional_number(
                props,
                "x",
            ),

            y=self.optional_number(
                props,
                "y",
            ),

            w=self.number(
                props,
                "w",
                220,
            ),

            h=self.number(
                props,
                "h",
                120,
            ),

            fill=self.string(
                props,
                "fill",
                "#EEF5FF",
            ),

            stroke=self.string(
                props,
                "stroke",
                "#5B86C5",
            ),

            text=self.string(
                props,
                "text",
                "#16233B",
            ),

            stroke_width=self.number(
                props,
                "stroke_width",
                1.8,
            ),

            radius=self.number(
                props,
                "radius",
                18,
            ),

            padding=self.number(
                props,
                "padding",
                18,
            ),

            opacity=self.number(
                props,
                "opacity",
                1.0,
            ),

            title_size=self.number(
                props,
                "title_size",
                18,
            ),

            title_weight=self.string(
                props,
                "title_weight",
                "700",
            ),

            body_size=self.number(
                props,
                "body_size",
                14,
            ),

            line_height=self.number(
                props,
                "line_height",
                21,
            ),

            rotation=self.number(
                props,
                "rotation",
                0,
            ),

            classes=self.parse_list(
                props.get("classes")
            ),

            data={},
        )

        # ----------------------------------------------------
        # Lines
        # ----------------------------------------------------

        if "lines" in props:
            node.lines = str(
                props["lines"]
            ).split("|")

        # ----------------------------------------------------
        # Icon customization
        # ----------------------------------------------------

        if "icon_color" in props:
            node.data["icon_color"] = str(
                props["icon_color"]
            )

        if "icon_position" in props:
            node.data["icon_position"] = str(
                props["icon_position"]
            )

        # ----------------------------------------------------
        # Shadow
        # ----------------------------------------------------

        if "shadow" in props:
            node.data["shadow"] = self.boolean(
                props,
                "shadow",
                False,
            )

        if "shadow_color" in props:
            node.data["shadow_color"] = str(
                props["shadow_color"]
            )

        if "shadow_blur" in props:
            node.data["shadow_blur"] = self.number(
                props,
                "shadow_blur",
                12,
            )

        if "shadow_offset_x" in props:
            node.data["shadow_offset_x"] = self.number(
                props,
                "shadow_offset_x",
                0,
            )

        if "shadow_offset_y" in props:
            node.data["shadow_offset_y"] = self.number(
                props,
                "shadow_offset_y",
                4,
            )

        # ----------------------------------------------------
        # Table
        # ----------------------------------------------------

        if "table" in props:
            node.data["table"] = props["table"]

        return node

    # ========================================================
    # EDGE
    # ========================================================

    def parse_edge(
        self,
        source: str,
        arrow: str,
        target: str,
    ) -> Edge:

        props = self.block()

        edge = Edge(
            source=source,
            target=target,

            route=self.string(
                props,
                "route",
                "straight",
            ),

            curve=self.number(
                props,
                "curve",
                40,
            ),

            corner_radius=self.number(
                props,
                "corner_radius",
                12,
            ),

            start_port=self.string(
                props,
                "start_port",
                "east",
            ),

            end_port=self.string(
                props,
                "end_port",
                "west",
            ),

            stroke=self.string(
                props,
                "stroke",
                "#52657A",
            ),

            width=self.number(
                props,
                "width",
                2,
            ),

            dash=self.optional_string(
                props,
                "dash",
            ),

            opacity=self.number(
                props,
                "opacity",
                1.0,
            ),

            marker=self.string(
                props,
                "marker",
                "arrow",
            ),

            start_marker=self.optional_string(
                props,
                "start_marker",
            ),

            label=self.string(
                props,
                "label",
                "",
            ),

            label_size=self.number(
                props,
                "label_size",
                14,
            ),

            label_color=self.string(
                props,
                "label_color",
                "#52657A",
            ),

            label_offset=self.number(
                props,
                "label_offset",
                8,
            ),

            data={},
        )

        # Dashed arrow syntax.
        if arrow == "~>":
            edge.dash = edge.dash or "7 5"

        # Bidirectional arrow syntax.
        if arrow == "<->":
            edge.start_marker = (
                edge.start_marker or "arrow"
            )

        return edge

    # ========================================================
    # MAIN PARSER
    # ========================================================

    def parse(self) -> Diagram:

        self.expect("diagram")

        title = self.text()

        diagram = Diagram(
            title=title
        )

        self.expect("{")

        while self.peek().value != "}":

            if self.peek().kind == "EOF":
                raise self.error(
                    "Unexpected end of file"
                )

            kind = self.pop().value

            # ------------------------------------------------
            # Canvas
            # ------------------------------------------------

            if kind == "canvas":
                diagram.canvas = (
                    self.parse_canvas()
                )

            # ------------------------------------------------
            # Style
            # ------------------------------------------------

            elif kind == "style":
                style = self.parse_style()

                if style.name in diagram.styles:
                    raise SyntaxError(
                        f"Duplicate style name "
                        f"{style.name!r}"
                    )

                diagram.styles[
                    style.name
                ] = style

            # ------------------------------------------------
            # Node
            # ------------------------------------------------

            elif kind == "node":

                node_id = self.text()

                if node_id in diagram.nodes:
                    raise SyntaxError(
                        f"Duplicate node id "
                        f"{node_id!r}"
                    )

                node = self.parse_node(
                    node_id
                )

                diagram.add_node(
                    node
                )

            # ------------------------------------------------
            # Edge
            # ------------------------------------------------

            elif kind == "edge":

                source = self.text()

                arrow_token = self.pop()

                if arrow_token.value not in {
                    "->",
                    "<->",
                    "~>",
                }:
                    raise SyntaxError(
                        f"Expected edge operator "
                        f"at position "
                        f"{arrow_token.pos}, "
                        f"got "
                        f"{arrow_token.value!r}"
                    )

                target = self.text()

                edge = self.parse_edge(
                    source,
                    arrow_token.value,
                    target,
                )

                diagram.add_edge(
                    edge
                )

            # ------------------------------------------------
            # Unknown
            # ------------------------------------------------

            else:
                raise SyntaxError(
                    f"Unknown statement "
                    f"{kind!r} at position "
                    f"{self.tokens[self.i - 1].pos}"
                )

        self.expect("}")

        if self.peek().kind != "EOF":
            raise self.error(
                "Unexpected content after diagram"
            )

        return diagram

    # ========================================================
    # TYPE HELPERS
    # ========================================================

    @staticmethod
    def number(
        props: dict[str, Any],
        key: str,
        default: float,
    ) -> float:

        value = props.get(
            key,
            default,
        )

        if isinstance(value, bool):
            raise ValueError(
                f"Property {key!r} must be numeric"
            )

        if not isinstance(
            value,
            (int, float),
        ):
            raise ValueError(
                f"Property {key!r} must be numeric"
            )

        return float(value)

    @staticmethod
    def optional_number(
        props: dict[str, Any],
        key: str,
    ) -> float | None:

        if key not in props:
            return None

        return Parser.number(
            props,
            key,
            0,
        )

    @staticmethod
    def integer(
        props: dict[str, Any],
        key: str,
        default: int,
    ) -> int:

        value = props.get(
            key,
            default,
        )

        if isinstance(value, bool):
            raise ValueError(
                f"Property {key!r} must be an integer"
            )

        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(
                    f"Property {key!r} must be an integer"
                )

            return int(value)

        if isinstance(value, int):
            return value

        raise ValueError(
            f"Property {key!r} must be an integer"
        )

    @staticmethod
    def string(
        props: dict[str, Any],
        key: str,
        default: str,
    ) -> str:

        value = props.get(
            key,
            default,
        )

        return str(value)

    @staticmethod
    def optional_string(
        props: dict[str, Any],
        key: str,
    ) -> str | None:

        if key not in props:
            return None

        return str(
            props[key]
        )

    @staticmethod
    def boolean(
        props: dict[str, Any],
        key: str,
        default: bool,
    ) -> bool:

        value = props.get(
            key,
            default,
        )

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.lower()

            if normalized in {
                "true",
                "yes",
                "on",
                "1",
            }:
                return True

            if normalized in {
                "false",
                "no",
                "off",
                "0",
            }:
                return False

        if isinstance(value, (int, float)):
            return bool(value)

        raise ValueError(
            f"Property {key!r} must be boolean"
        )

    @staticmethod
    def parse_list(
        value: Any,
    ) -> list[str]:

        if value is None:
            return []

        if isinstance(value, str):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return [
            str(value)
        ]


def parse(text: str) -> Diagram:
    """
    Convenience function.
    """

    return Parser(text).parse()