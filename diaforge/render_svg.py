from __future__ import annotations

import html
import math

import cairosvg

from .ast import Diagram, Edge, Node, Point
from .icons import icon_svg
from .routing import route


# ============================================================
# SVG HELPERS
# ============================================================

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.3f}"


# ============================================================
# SVG RENDERER
# ============================================================

class SVGRenderer:

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

    # ========================================================
    # DEFINITIONS
    # ========================================================

    def definitions(self) -> str:
        colors = {
            edge.stroke
            for edge in self.diagram.edges
            if edge.stroke
        }

        markers = []

        for color in sorted(colors):
            marker_id = self.marker_id(color)

            markers.append(
                f"""
                <marker
                    id="{marker_id}"
                    viewBox="0 0 10 10"
                    refX="8"
                    refY="5"
                    markerWidth="8"
                    markerHeight="8"
                    orient="auto"
                    markerUnits="strokeWidth"
                >
                    <path
                        d="M 0 0 L 10 5 L 0 10 Z"
                        fill="{esc(color)}"
                    />
                </marker>
                """
            )

        return f"""
        <defs>

            <filter
                id="node-shadow"
                x="-30%"
                y="-30%"
                width="160%"
                height="170%"
            >
                <feDropShadow
                    dx="0"
                    dy="6"
                    stdDeviation="10"
                    flood-color="#64748B"
                    flood-opacity="0.18"
                />
            </filter>

            <filter
                id="small-shadow"
                x="-30%"
                y="-30%"
                width="160%"
                height="170%"
            >
                <feDropShadow
                    dx="0"
                    dy="3"
                    stdDeviation="5"
                    flood-color="#64748B"
                    flood-opacity="0.14"
                />
            </filter>

            {''.join(markers)}

        </defs>
        """

    # ========================================================
    # MARKER
    # ========================================================

    @staticmethod
    def marker_id(color: str) -> str:
        safe = "".join(
            character
            for character in color
            if character.isalnum()
        )

        return f"arrow-{safe or 'default'}"

    # ========================================================
    # CANVAS
    # ========================================================

    def render_canvas(self) -> str:
        canvas = self.diagram.canvas

        return (
            f'<rect '
            f'x="0" '
            f'y="0" '
            f'width="{fmt(canvas.width)}" '
            f'height="{fmt(canvas.height)}" '
            f'fill="{esc(canvas.background)}" '
            f'/>'
        )

    # ========================================================
    # NODE
    # ========================================================

    def render_node(self, node: Node) -> str:

        x = node.x or 0
        y = node.y or 0

        w = node.w
        h = node.h

        center_x = x + w / 2
        center_y = y + h / 2

        opacity = max(
            0,
            min(1, node.opacity),
        )

        shadow = ""

        if node.data.get(
            "shadow",
            True,
        ):
            shadow = 'filter="url(#node-shadow)"'

        parts = [
            (
                f'<g '
                f'id="node-{esc(node.id)}" '
                f'opacity="{fmt(opacity)}" '
                f'transform="rotate('
                f'{fmt(node.rotation)} '
                f'{fmt(center_x)} '
                f'{fmt(center_y)}'
                f')">'
            )
        ]

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------

        parts.append(
            f"""
            <rect
                x="{fmt(x)}"
                y="{fmt(y)}"
                width="{fmt(w)}"
                height="{fmt(h)}"
                rx="{fmt(node.radius)}"
                ry="{fmt(node.radius)}"
                fill="{esc(node.fill)}"
                stroke="{esc(node.stroke)}"
                stroke-width="{fmt(node.stroke_width)}"
                {shadow}
            />
            """
        )

        # ----------------------------------------------------
        # Content
        # ----------------------------------------------------

        parts.append(
            self.render_node_content(node)
        )

        # ----------------------------------------------------
        # Ports
        # ----------------------------------------------------

        parts.append(
            self.render_ports(node)
        )

        parts.append("</g>")

        return "\n".join(parts)

    # ========================================================
    # NODE CONTENT
    # ========================================================

    def render_node_content(
        self,
        node: Node,
    ) -> str:

        x = node.x or 0
        y = node.y or 0

        padding = max(
            0,
            node.padding,
        )

        content_x = x + padding
        content_y = y + padding

        parts = []

        # ----------------------------------------------------
        # Icon
        # ----------------------------------------------------

        title_x = content_x

        if node.icon:

            icon_size = node.icon_size

            icon_color = str(
                node.data.get(
                    "icon_color",
                    node.stroke,
                )
            )

            icon_position = str(
                node.data.get(
                    "icon_position",
                    "left",
                )
            )

            if icon_position == "right":

                icon_x = (
                    x
                    + node.w
                    - padding
                    - icon_size
                )

            elif icon_position == "center":

                icon_x = (
                    x
                    + (node.w - icon_size) / 2
                )

            else:

                icon_x = content_x

                title_x = (
                    content_x
                    + icon_size
                    + 12
                )

            icon_y = content_y

            parts.append(
                icon_svg(
                    node.icon,
                    icon_x,
                    icon_y,
                    icon_size,
                    icon_color,
                )
            )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title_y = (
            content_y
            + node.title_size
        )

        if node.title:

            parts.append(
                self.text(
                    x=title_x,
                    y=title_y,
                    value=node.title,
                    size=node.title_size,
                    weight=node.title_weight,
                    color=node.text,
                )
            )

        # ----------------------------------------------------
        # Body
        # ----------------------------------------------------

        if node.lines:

            body_y = (
                title_y
                + node.line_height
                + 8
            )

            for index, line in enumerate(
                node.lines
            ):

                line_y = (
                    body_y
                    + index * node.line_height
                )

                parts.append(
                    self.text(
                        x=content_x,
                        y=line_y,
                        value=line,
                        size=node.body_size,
                        weight="400",
                        color=node.text,
                    )
                )

        # ----------------------------------------------------
        # Table
        # ----------------------------------------------------

        if node.table:

            parts.append(
                self.render_table(
                    node,
                    node.table,
                )
            )

        return "\n".join(parts)

    # ========================================================
    # TEXT
    # ========================================================

    def text(
        self,
        *,
        x: float,
        y: float,
        value: str,
        size: float,
        weight: str,
        color: str,
        anchor: str = "start",
    ) -> str:

        return (
            f'<text '
            f'x="{fmt(x)}" '
            f'y="{fmt(y)}" '
            f'font-family="'
            f'{esc(self.diagram.canvas.font_family)}" '
            f'font-size="{fmt(size)}" '
            f'font-weight="{esc(weight)}" '
            f'fill="{esc(color)}" '
            f'text-anchor="{esc(anchor)}" '
            f'dominant-baseline="alphabetic">'
            f'{esc(value)}'
            f'</text>'
        )

    # ========================================================
    # PORTS
    # ========================================================

    def render_ports(
        self,
        node: Node,
    ) -> str:

        parts = []

        for port in node.ports.values():

            if not port.visible:
                continue

            point = self.port_position(
                node,
                port.side,
                port.offset,
            )

            parts.append(
                f"""
                <circle
                    cx="{fmt(point.x)}"
                    cy="{fmt(point.y)}"
                    r="{fmt(port.radius)}"
                    fill="{esc(node.stroke)}"
                    stroke="#FFFFFF"
                    stroke-width="2"
                />
                """
            )

        return "\n".join(parts)

    @staticmethod
    def port_position(
        node: Node,
        side: str,
        offset: float,
    ) -> Point:

        x = node.x or 0
        y = node.y or 0

        offset = max(
            0,
            min(1, offset),
        )

        if side == "west":
            return Point(
                x,
                y + node.h * offset,
            )

        if side == "north":
            return Point(
                x + node.w * offset,
                y,
            )

        if side == "south":
            return Point(
                x + node.w * offset,
                y + node.h,
            )

        if side == "center":
            return Point(
                x + node.w / 2,
                y + node.h / 2,
            )

        return Point(
            x + node.w,
            y + node.h * offset,
        )

    # ========================================================
    # TABLE
    # ========================================================

    def render_table(
        self,
        node: Node,
        table,
    ) -> str:

        if not table.rows:
            return ""

        x = node.x or 0
        y = node.y or 0

        table_x = x + table.padding
        table_y = y + table.padding

        width = (
            node.w
            - table.padding * 2
        )

        row_count = len(table.rows)

        if row_count == 0:
            return ""

        row_height = 34

        height = (
            row_count * row_height
            + table.row_gap
            * max(0, row_count - 1)
        )

        parts = [
            '<g class="diaforge-table">',
            f"""
            <rect
                x="{fmt(table_x)}"
                y="{fmt(table_y)}"
                width="{fmt(width)}"
                height="{fmt(height)}"
                rx="{fmt(table.radius)}"
                fill="{esc(table.fill)}"
                stroke="{esc(table.stroke)}"
                stroke-width="{fmt(table.stroke_width)}"
                filter="url(#small-shadow)"
            />
            """
        ]

        max_columns = max(
            len(row)
            for row in table.rows
        )

        if max_columns == 0:
            parts.append("</g>")
            return "\n".join(parts)

        column_width = (
            width / max_columns
        )

        for row_index, row in enumerate(
            table.rows
        ):

            row_y = (
                table_y
                + row_index * (
                    row_height
                    + table.row_gap
                )
            )

            for col_index, cell in enumerate(
                row
            ):

                cell_x = (
                    table_x
                    + col_index * column_width
                )

                cell_w = (
                    column_width
                    * max(1, cell.colspan)
                )

                cell_h = (
                    row_height
                    * max(1, cell.rowspan)
                )

                fill = (
                    cell.fill
                    or "transparent"
                )

                stroke = (
                    cell.stroke
                    or table.stroke
                )

                parts.append(
                    f"""
                    <rect
                        x="{fmt(cell_x)}"
                        y="{fmt(row_y)}"
                        width="{fmt(cell_w)}"
                        height="{fmt(cell_h)}"
                        rx="6"
                        fill="{esc(fill)}"
                        stroke="{esc(stroke)}"
                        stroke-width="{fmt(cell.stroke_width)}"
                    />
                    """
                )

                text_x = (
                    cell_x
                    + cell.padding
                )

                text_y = (
                    row_y
                    + cell_h / 2
                    + 5
                )

                if cell.icon:

                    icon_size = cell.icon.size

                    parts.append(
                        icon_svg(
                            cell.icon.name,
                            text_x,
                            row_y
                            + (
                                cell_h
                                - icon_size
                            ) / 2,
                            icon_size,
                            cell.icon.color
                            or node.stroke,
                        )
                    )

                    text_x += (
                        icon_size
                        + 8
                    )

                value = cell.value

                if cell.text:
                    value = cell.text.text

                if value:

                    color = (
                        cell.text.color
                        if cell.text
                        else node.text
                    )

                    size = (
                        cell.text.size
                        if cell.text
                        else node.body_size
                    )

                    weight = (
                        cell.text.weight
                        if cell.text
                        else "400"
                    )

                    parts.append(
                        self.text(
                            x=text_x,
                            y=text_y,
                            value=value,
                            size=size,
                            weight=weight,
                            color=color,
                        )
                    )

        parts.append("</g>")

        return "\n".join(parts)

    # ========================================================
    # EDGES
    # ========================================================

    def render_edge(
        self,
        edge: Edge,
    ) -> str:

        source = self.diagram.nodes[
            edge.source
        ]

        target = self.diagram.nodes[
            edge.target
        ]

        geometry = route(
            edge,
            source,
            target,
        )

        kind = geometry["kind"]

        if kind == "line":
            return self.render_line_edge(
                edge,
                geometry,
            )

        if kind == "quad":
            return self.render_curve_edge(
                edge,
                geometry,
            )

        if kind == "orthogonal":
            return self.render_orthogonal_edge(
                edge,
                geometry,
            )

        return ""

    # ========================================================
    # LINE EDGE
    # ========================================================

    def render_line_edge(
        self,
        edge: Edge,
        geometry: dict,
    ) -> str:

        a = geometry["a"]
        b = geometry["b"]

        marker_attr = ""

        if edge.marker != "none":

            marker_id = self.marker_id(
                edge.stroke
            )

            marker_attr = (
                f' marker-end="url(#{marker_id})"'
            )

        dash_attr = ""

        if edge.dash:

            dash_attr = (
                f' stroke-dasharray="'
                f'{esc(edge.dash)}"'
            )

        parts = [
            '<g class="diaforge-edge">',
            (
                f'<path '
                f'd="M {fmt(a[0])} {fmt(a[1])} '
                f'L {fmt(b[0])} {fmt(b[1])}" '
                f'fill="none" '
                f'stroke="{esc(edge.stroke)}" '
                f'stroke-width="{fmt(edge.width)}" '
                f'stroke-linecap="round" '
                f'stroke-linejoin="round" '
                f'opacity="{fmt(edge.opacity)}"'
                f'{dash_attr}'
                f'{marker_attr}'
                f'/>'
            ),
        ]

        if edge.label:

            parts.append(
                self.render_edge_label(
                    edge,
                    self.midpoint(
                        a,
                        b,
                    ),
                )
            )

        parts.append("</g>")

        return "\n".join(parts)

    # ========================================================
    # CURVED EDGE
    # ========================================================

    def render_curve_edge(
        self,
        edge: Edge,
        geometry: dict,
    ) -> str:

        a = geometry["a"]
        c = geometry["c"]
        b = geometry["b"]

        marker_attr = ""

        if edge.marker != "none":

            marker_id = self.marker_id(
                edge.stroke
            )

            marker_attr = (
                f' marker-end="url(#{marker_id})"'
            )

        dash_attr = ""

        if edge.dash:

            dash_attr = (
                f' stroke-dasharray="'
                f'{esc(edge.dash)}"'
            )

        parts = [
            '<g class="diaforge-edge">',
            (
                f'<path '
                f'd="M {fmt(a[0])} {fmt(a[1])} '
                f'Q {fmt(c[0])} {fmt(c[1])} '
                f'{fmt(b[0])} {fmt(b[1])}" '
                f'fill="none" '
                f'stroke="{esc(edge.stroke)}" '
                f'stroke-width="{fmt(edge.width)}" '
                f'stroke-linecap="round" '
                f'stroke-linejoin="round" '
                f'opacity="{fmt(edge.opacity)}"'
                f'{dash_attr}'
                f'{marker_attr}'
                f'/>'
            ),
        ]

        if edge.label:

            label_point = self.quadratic_point(
                a,
                c,
                b,
                0.5,
            )

            parts.append(
                self.render_edge_label(
                    edge,
                    label_point,
                )
            )

        parts.append("</g>")

        return "\n".join(parts)

    # ========================================================
    # ORTHOGONAL EDGE
    # ========================================================

    def render_orthogonal_edge(
        self,
        edge: Edge,
        geometry: dict,
    ) -> str:

        points = geometry["points"]

        if len(points) < 2:
            return ""

        radius = max(
            0,
            edge.corner_radius,
        )

        path = self.rounded_polyline_path(
            points,
            radius,
        )

        marker_attr = ""

        if edge.marker != "none":

            marker_id = self.marker_id(
                edge.stroke
            )

            marker_attr = (
                f' marker-end="url(#{marker_id})"'
            )

        dash_attr = ""

        if edge.dash:

            dash_attr = (
                f' stroke-dasharray="'
                f'{esc(edge.dash)}"'
            )

        parts = [
            '<g class="diaforge-edge">',
            (
                f'<path '
                f'd="{path}" '
                f'fill="none" '
                f'stroke="{esc(edge.stroke)}" '
                f'stroke-width="{fmt(edge.width)}" '
                f'stroke-linecap="round" '
                f'stroke-linejoin="round" '
                f'opacity="{fmt(edge.opacity)}"'
                f'{dash_attr}'
                f'{marker_attr}'
                f'/>'
            ),
        ]

        if edge.label:

            label_point = (
                self.polyline_midpoint(
                    points
                )
            )

            parts.append(
                self.render_edge_label(
                    edge,
                    label_point,
                )
            )

        parts.append("</g>")

        return "\n".join(parts)

    # ========================================================
    # EDGE LABEL
    # ========================================================

    def render_edge_label(
        self,
        edge: Edge,
        point: Point,
    ) -> str:

        x = point.x

        y = (
            point.y
            - edge.label_offset
        )

        width = (
            max(
                20,
                len(edge.label) * 7,
            )
            + 14
        )

        height = 24

        return f"""
        <g class="diaforge-edge-label">

            <rect
                x="{fmt(x - width / 2)}"
                y="{fmt(y - height + 4)}"
                width="{fmt(width)}"
                height="{fmt(height)}"
                rx="8"
                fill="#FFFFFF"
                fill-opacity="0.94"
                stroke="#E2E8F0"
                stroke-width="0.8"
            />

            <text
                x="{fmt(x)}"
                y="{fmt(y - 4)}"
                font-family="{esc(self.diagram.canvas.font_family)}"
                font-size="{fmt(edge.label_size)}"
                font-weight="600"
                fill="{esc(edge.label_color)}"
                text-anchor="middle"
            >
                {esc(edge.label)}
            </text>

        </g>
        """

    # ========================================================
    # GEOMETRY
    # ========================================================

    @staticmethod
    def midpoint(
        a,
        b,
    ) -> Point:

        return Point(
            (a[0] + b[0]) / 2,
            (a[1] + b[1]) / 2,
        )

    @staticmethod
    def quadratic_point(
        a,
        c,
        b,
        t: float,
    ) -> Point:

        u = 1 - t

        return Point(
            u * u * a[0]
            + 2 * u * t * c[0]
            + t * t * b[0],

            u * u * a[1]
            + 2 * u * t * c[1]
            + t * t * b[1],
        )

    @staticmethod
    def polyline_midpoint(
        points,
    ) -> Point:

        if len(points) == 1:

            return Point(
                points[0][0],
                points[0][1],
            )

        lengths = []
        total = 0

        for index in range(
            len(points) - 1
        ):

            a = points[index]
            b = points[index + 1]

            length = math.hypot(
                b[0] - a[0],
                b[1] - a[1],
            )

            lengths.append(length)
            total += length

        if total <= 0:

            return Point(
                points[0][0],
                points[0][1],
            )

        target = total / 2
        travelled = 0

        for index, length in enumerate(
            lengths
        ):

            if travelled + length >= target:

                a = points[index]
                b = points[index + 1]

                ratio = (
                    target - travelled
                ) / length

                return Point(
                    a[0]
                    + (
                        b[0] - a[0]
                    ) * ratio,

                    a[1]
                    + (
                        b[1] - a[1]
                    ) * ratio,
                )

            travelled += length

        last = points[-1]

        return Point(
            last[0],
            last[1],
        )

    # ========================================================
    # ROUNDED POLYLINE
    # ========================================================

    @staticmethod
    def rounded_polyline_path(
        points,
        radius: float,
    ) -> str:

        if len(points) < 2:
            return ""

        if len(points) == 2:

            a = points[0]
            b = points[1]

            return (
                f"M {fmt(a[0])} {fmt(a[1])} "
                f"L {fmt(b[0])} {fmt(b[1])}"
            )

        commands = [
            f"M {fmt(points[0][0])} "
            f"{fmt(points[0][1])}"
        ]

        for index in range(
            1,
            len(points) - 1,
        ):

            previous = points[index - 1]
            current = points[index]
            following = points[index + 1]

            incoming_length = math.hypot(
                current[0] - previous[0],
                current[1] - previous[1],
            )

            outgoing_length = math.hypot(
                following[0] - current[0],
                following[1] - current[1],
            )

            if (
                incoming_length <= 0
                or outgoing_length <= 0
                or radius <= 0
            ):

                commands.append(
                    f"L {fmt(current[0])} "
                    f"{fmt(current[1])}"
                )

                continue

            r = min(
                radius,
                incoming_length / 2,
                outgoing_length / 2,
            )

            before = (
                current[0]
                - (
                    current[0]
                    - previous[0]
                )
                / incoming_length
                * r,

                current[1]
                - (
                    current[1]
                    - previous[1]
                )
                / incoming_length
                * r,
            )

            after = (
                current[0]
                + (
                    following[0]
                    - current[0]
                )
                / outgoing_length
                * r,

                current[1]
                + (
                    following[1]
                    - current[1]
                )
                / outgoing_length
                * r,
            )

            commands.append(
                f"L {fmt(before[0])} "
                f"{fmt(before[1])}"
            )

            commands.append(
                f"Q {fmt(current[0])} "
                f"{fmt(current[1])} "
                f"{fmt(after[0])} "
                f"{fmt(after[1])}"
            )

        last = points[-1]

        commands.append(
            f"L {fmt(last[0])} "
            f"{fmt(last[1])}"
        )

        return " ".join(commands)

    # ========================================================
    # FINAL RENDER
    # ========================================================

    def render(self) -> str:

        canvas = self.diagram.canvas

        parts = [
            (
                f'<svg '
                f'xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{fmt(canvas.width)}" '
                f'height="{fmt(canvas.height)}" '
                f'viewBox="0 0 '
                f'{fmt(canvas.width)} '
                f'{fmt(canvas.height)}" '
                f'role="img" '
                f'aria-label="{esc(self.diagram.title)}">'
            ),
            self.definitions(),
            self.render_canvas(),
        ]

        # Edges first so they appear behind nodes.
        for edge in self.diagram.edges:

            parts.append(
                self.render_edge(edge)
            )

        # Nodes afterwards.
        for node in self.diagram.nodes.values():

            parts.append(
                self.render_node(node)
            )

        parts.append("</svg>")

        return "\n".join(parts)


# ============================================================
# PUBLIC API
# ============================================================

def render(
    diagram: Diagram,
) -> str:

    return SVGRenderer(
        diagram
    ).render()


def render_png(
    diagram: Diagram,
    *,
    dpi: float = 96.0,
) -> bytes:

    svg = render(diagram)

    return cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        dpi=dpi,
    )