from dataclasses import dataclass, field
from typing import Any


# ============================================================
# BASIC GEOMETRY
# ============================================================

@dataclass
class Point:
    x: float
    y: float


@dataclass
class Size:
    width: float
    height: float


@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Point:
        return Point(
            self.x + self.width / 2,
            self.y + self.height / 2,
        )


# ============================================================
# CANVAS
# ============================================================

@dataclass
class Canvas:
    width: float = 1200
    height: float = 800

    background: str = "#FFFFFF"

    # Optional outer padding around the diagram.
    padding: float = 40

    # Default font used by the SVG renderer.
    font_family: str = "Inter, Arial, sans-serif"

    # Default font size.
    font_size: float = 14


# ============================================================
# STYLE
# ============================================================

@dataclass
class Style:
    name: str

    values: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ICON
# ============================================================

@dataclass
class Icon:
    """
    Icon specification.

    name:
        Name registered in the DiaForge icon registry.

    size:
        Icon size in pixels.

    color:
        Optional icon color.

    position:
        left / right / top / bottom / center.
    """

    name: str

    size: float = 24

    color: str | None = None

    position: str = "left"


# ============================================================
# TEXT
# ============================================================

@dataclass
class TextBlock:
    text: str

    size: float = 14

    weight: str = "400"

    color: str = "#16233B"

    align: str = "left"

    line_height: float = 1.4


# ============================================================
# TABLE CELL
# ============================================================

@dataclass
class Cell:
    """
    A single table cell.

    This is deliberately a real AST object rather than
    representing tables as strings.

    That allows us to eventually support:

        icon
        text
        custom padding
        alignment
        fill
        borders
        spans
        relationships
    """

    value: str = ""

    icon: Icon | None = None

    text: TextBlock | None = None

    fill: str | None = None

    stroke: str | None = None

    stroke_width: float = 1

    padding: float = 10

    align: str = "left"

    valign: str = "middle"

    colspan: int = 1

    rowspan: int = 1


# ============================================================
# TABLE
# ============================================================

@dataclass
class Table:
    """
    Structured table contained inside a node.

    Example conceptual structure:

        table {
            row {
                cell "Model"
                cell "Accuracy"
            }

            row {
                cell "BGE-M3"
                cell "73%"
            }
        }
    """

    rows: list[list[Cell]] = field(
        default_factory=list
    )

    padding: float = 12

    row_gap: float = 0

    column_gap: float = 0

    radius: float = 12

    fill: str = "#FFFFFF"

    stroke: str = "#D6DFEA"

    stroke_width: float = 1


# ============================================================
# PORT
# ============================================================

@dataclass
class Port:
    """
    A named connection point on a node.

    Examples:

        north
        south
        input
        output
        database
        verifier
    """

    name: str

    side: str = "east"

    offset: float = 0.5

    radius: float = 4

    visible: bool = False


# ============================================================
# NODE
# ============================================================

@dataclass
class Node:
    id: str

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    title: str = ""

    lines: list[str] = field(
        default_factory=list
    )

    icon: str | None = None

    icon_size: float = 26

    table: Table | None = None

    # --------------------------------------------------------
    # POSITION
    # --------------------------------------------------------

    x: float | None = None
    y: float | None = None

    w: float = 220
    h: float = 120

    # Whether dimensions were explicitly specified by the user.
    width_explicit: bool = False
    height_explicit: bool = False

    # --------------------------------------------------------
    # VISUAL STYLE
    # --------------------------------------------------------

    fill: str = "#EEF5FF"

    stroke: str = "#5B86C5"

    text: str = "#16233B"

    stroke_width: float = 1.8

    radius: float = 18

    padding: float = 18

    opacity: float = 1.0

    # --------------------------------------------------------
    # TYPOGRAPHY
    # --------------------------------------------------------

    title_size: float = 18

    title_weight: str = "700"

    body_size: float = 14

    line_height: float = 21

    # --------------------------------------------------------
    # TRANSFORM
    # --------------------------------------------------------

    rotation: float = 0

    # --------------------------------------------------------
    # PORTS
    # --------------------------------------------------------

    ports: dict[str, Port] = field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    classes: list[str] = field(
        default_factory=list
    )

    data: dict[str, Any] = field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # GEOMETRY
    # --------------------------------------------------------

    @property
    def rect(self) -> Rect:
        return Rect(
            x=self.x or 0,
            y=self.y or 0,
            width=self.w,
            height=self.h,
        )

    @property
    def center(self) -> Point:
        return self.rect.center


# ============================================================
# EDGE
# ============================================================

@dataclass
class Edge:
    """
    Relationship between two nodes.

    source / target may later support:

        node
        node.port
        node.port.anchor

    while keeping the basic syntax simple.
    """

    source: str

    target: str

    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    route: str = "straight"

    curve: float = 40

    corner_radius: float = 12

    # --------------------------------------------------------
    # PORTS
    # --------------------------------------------------------

    start_port: str = "east"

    end_port: str = "west"

    # --------------------------------------------------------
    # VISUAL STYLE
    # --------------------------------------------------------

    stroke: str = "#52657A"

    width: float = 2

    dash: str | None = None

    opacity: float = 1.0

    # --------------------------------------------------------
    # ARROW
    # --------------------------------------------------------

    marker: str = "arrow"

    start_marker: str | None = None

    # --------------------------------------------------------
    # LABEL
    # --------------------------------------------------------

    label: str = ""

    label_size: float = 14

    label_color: str = "#52657A"

    label_offset: float = 8

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    data: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# DIAGRAM
# ============================================================

@dataclass
class Diagram:
    title: str

    canvas: Canvas = field(
        default_factory=Canvas
    )

    styles: dict[str, Style] = field(
        default_factory=dict
    )

    nodes: dict[str, Node] = field(
        default_factory=dict
    )

    edges: list[Edge] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    data: dict[str, Any] = field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def add_node(self, node: Node):
        if node.id in self.nodes:
            raise ValueError(
                f"Duplicate node id: {node.id!r}"
            )

        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        if edge.source not in self.nodes:
            raise ValueError(
                f"Unknown source node: "
                f"{edge.source!r}"
            )

        if edge.target not in self.nodes:
            raise ValueError(
                f"Unknown target node: "
                f"{edge.target!r}"
            )

        self.edges.append(edge)