from __future__ import annotations

from .ast import Diagram, Node, Table, Cell


# ============================================================
# DEFAULT LAYOUT / SIZING CONSTANTS
# ============================================================

DEFAULT_MIN_WIDTH = 120.0
DEFAULT_MAX_WIDTH = 520.0

DEFAULT_MIN_HEIGHT = 70.0
DEFAULT_MAX_HEIGHT = 800.0

# Approximate average character width as a fraction
# of font size.
CHAR_WIDTH_FACTOR = 0.52

ICON_TEXT_GAP = 10.0


# ============================================================
# TEXT MEASUREMENT
# ============================================================

def estimate_text_width(
    text: str,
    font_size: float,
    weight: str = "400",
) -> float:
    """
    Renderer-independent text width estimation.

    This is intentionally approximate.

    Later, DiaForge can replace this with real font metrics
    supplied by the renderer.
    """

    if not text:
        return 0.0

    weight_factor = {
        "300": 0.98,
        "400": 1.00,
        "500": 1.02,
        "600": 1.04,
        "700": 1.06,
        "800": 1.08,
        "900": 1.10,
    }.get(str(weight), 1.04)

    width = 0.0

    for char in text:

        # Narrow characters
        if char in "ilI.,'|!":
            factor = 0.30

        # Wide characters
        elif char in "MW@#%&":
            factor = 0.90

        # Space
        elif char == " ":
            factor = 0.30

        # Normal character
        else:
            factor = CHAR_WIDTH_FACTOR

        width += font_size * factor

    return width * weight_factor


# ============================================================
# TABLE MEASUREMENT
# ============================================================

def cell_text(cell: Cell) -> str:
    """
    Return the visible text represented by a cell.
    """

    if cell.text is not None:
        return cell.text.text

    return cell.value or ""


def estimate_cell_width(
    cell: Cell,
) -> float:
    """
    Estimate the minimum width required by one table cell.

    Accounts for:

        text
        font size
        font weight
        icon
        icon/text gap
        horizontal padding
    """

    text = cell_text(cell)

    if cell.text is not None:
        font_size = cell.text.size
        font_weight = cell.text.weight
    else:
        font_size = 14.0
        font_weight = "400"

    width = estimate_text_width(
        text,
        font_size,
        font_weight,
    )

    # Icon
    if cell.icon is not None:
        width += (
            cell.icon.size
            + ICON_TEXT_GAP
        )

    # Horizontal padding
    width += cell.padding * 2

    return width


def estimate_table_width(
    table: Table,
) -> float:
    """
    Estimate the minimum width required by a table.
    """

    if not table.rows:
        return 0.0

    column_count = max(
        len(row)
        for row in table.rows
    )

    if column_count == 0:
        return 0.0

    column_widths = [
        0.0
        for _ in range(column_count)
    ]

    for row in table.rows:

        for index, cell in enumerate(row):

            if index >= column_count:
                continue

            width = estimate_cell_width(cell)

            # Basic colspan support.
            if cell.colspan > 1:
                width /= cell.colspan

            column_widths[index] = max(
                column_widths[index],
                width,
            )

    gap_width = (
        max(0, column_count - 1)
        * table.column_gap
    )

    return (
        sum(column_widths)
        + gap_width
        + table.padding * 2
    )


def estimate_table_height(
    table: Table,
) -> float:
    """
    Estimate the minimum height required by a table.
    """

    if not table.rows:
        return 0.0

    row_heights: list[float] = []

    for row in table.rows:

        row_height = 0.0

        for cell in row:

            # Text height
            if cell.text is not None:
                cell_height = (
                    cell.text.size
                    * cell.text.line_height
                )
            else:
                cell_height = (
                    14.0 * 1.4
                )

            # Icon height
            if cell.icon is not None:
                cell_height = max(
                    cell_height,
                    cell.icon.size,
                )

            # Vertical padding
            cell_height += (
                cell.padding * 2
            )

            row_height = max(
                row_height,
                cell_height,
            )

        row_heights.append(
            row_height
        )

    gap_height = (
        max(0, len(row_heights) - 1)
        * table.row_gap
    )

    return (
        sum(row_heights)
        + gap_height
        + table.padding * 2
    )


# ============================================================
# NODE CONTENT MEASUREMENT
# ============================================================

def estimate_node_content_width(
    node: Node,
) -> float:
    """
    Calculate the width required by the content
    inside a node.

    Considers:

        title
        title font
        title weight
        node icon
        body lines
        table
    """

    required = 0.0

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title_width = estimate_text_width(
        node.title,
        node.title_size,
        node.title_weight,
    )

    # Icon next to title
    if node.icon:
        title_width += (
            node.icon_size
            + ICON_TEXT_GAP
        )

    required = max(
        required,
        title_width,
    )

    # --------------------------------------------------------
    # Body lines
    # --------------------------------------------------------

    for line in node.lines:

        line_width = estimate_text_width(
            line,
            node.body_size,
            "400",
        )

        required = max(
            required,
            line_width,
        )

    # --------------------------------------------------------
    # Table
    # --------------------------------------------------------

    if node.table is not None:

        required = max(
            required,
            estimate_table_width(
                node.table
            ),
        )

    return required


def estimate_node_content_height(
    node: Node,
) -> float:
    """
    Calculate the height required by the node content.
    """

    height = 0.0

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    if node.title:

        height += (
            node.title_size
            * 1.25
        )

    # --------------------------------------------------------
    # Body
    # --------------------------------------------------------

    if node.lines:

        if height > 0:
            height += 6.0

        height += (
            len(node.lines)
            * node.line_height
        )

    # --------------------------------------------------------
    # Table
    # --------------------------------------------------------

    if node.table is not None:

        if node.title or node.lines:
            height += 8.0

        height += estimate_table_height(
            node.table
        )

    return height


# ============================================================
# NODE SIZE CALCULATION
# ============================================================

def calculate_node_width(
    node: Node,
    *,
    min_width: float = DEFAULT_MIN_WIDTH,
    max_width: float = DEFAULT_MAX_WIDTH,
) -> float:
    """
    Calculate the final width of a node.

    Explicit `w:` always wins.

    Otherwise:

        content width
        + left padding
        + right padding

    followed by min/max constraints.
    """

    # Explicit width
    if node.width_explicit:
        return node.w

    content_width = (
        estimate_node_content_width(node)
    )

    required_width = (
        content_width
        + node.padding * 2
    )

    return max(
        min_width,
        min(
            max_width,
            required_width,
        ),
    )


def calculate_node_height(
    node: Node,
    *,
    min_height: float = DEFAULT_MIN_HEIGHT,
    max_height: float = DEFAULT_MAX_HEIGHT,
) -> float:
    """
    Calculate the final height of a node.

    Explicit `h:` always wins.
    """

    # Explicit height
    if node.height_explicit:
        return node.h

    content_height = (
        estimate_node_content_height(node)
    )

    required_height = (
        content_height
        + node.padding * 2
    )

    return max(
        min_height,
        min(
            max_height,
            required_height,
        ),
    )


# ============================================================
# AUTO-SIZE ONE NODE
# ============================================================

def auto_size_node(
    node: Node,
    *,
    min_width: float = DEFAULT_MIN_WIDTH,
    max_width: float = DEFAULT_MAX_WIDTH,
    min_height: float = DEFAULT_MIN_HEIGHT,
    max_height: float = DEFAULT_MAX_HEIGHT,
) -> Node:
    """
    Calculate and apply the final dimensions of a node.

    Explicit dimensions remain unchanged.
    """

    node.w = calculate_node_width(
        node,
        min_width=min_width,
        max_width=max_width,
    )

    node.h = calculate_node_height(
        node,
        min_height=min_height,
        max_height=max_height,
    )

    return node


# ============================================================
# AUTO-SIZE ALL NODES
# ============================================================

def auto_size_nodes(
    diagram: Diagram,
    *,
    min_width: float = DEFAULT_MIN_WIDTH,
    max_width: float = DEFAULT_MAX_WIDTH,
    min_height: float = DEFAULT_MIN_HEIGHT,
    max_height: float = DEFAULT_MAX_HEIGHT,
) -> Diagram:
    """
    Automatically size all nodes.

    This must happen before:

        placement
        edge routing
        rendering
    """

    for node in diagram.nodes.values():

        auto_size_node(
            node,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
        )

    return diagram


# ============================================================
# AUTO LAYOUT
# ============================================================

def auto_layout(
    diagram: Diagram,
    gap: float = 70,
    margin: float = 70,
) -> Diagram:
    """
    Perform automatic sizing and deterministic placement.

    Pipeline:

        1. Calculate node sizes.
        2. Place nodes left-to-right.
        3. Wrap rows according to actual node height.
        4. Preserve explicit x/y coordinates.

    After this function returns, node.x/y/w/h represent
    the final geometry to be used by routing and rendering.
    """

    # ========================================================
    # 1. AUTO-SIZE
    # ========================================================

    auto_size_nodes(diagram)

    # ========================================================
    # 2. INITIAL POSITION
    # ========================================================

    x = margin
    y = margin

    row_height = 0.0

    # ========================================================
    # 3. PLACE NODES
    # ========================================================

    for node in diagram.nodes.values():

        # ----------------------------------------------------
        # Wrap only automatically positioned nodes.
        # ----------------------------------------------------

        if (
            node.x is None
            and x + node.w
            > diagram.canvas.width - margin
        ):

            x = margin

            y += (
                row_height
                + gap
            )

            row_height = 0.0

        # ----------------------------------------------------
        # Preserve explicit coordinates.
        # ----------------------------------------------------

        if node.x is None:
            node.x = x

        if node.y is None:
            node.y = y

        # ----------------------------------------------------
        # Track row height.
        # ----------------------------------------------------

        row_height = max(
            row_height,
            node.h,
        )

        # ----------------------------------------------------
        # Advance automatic x position.
        # ----------------------------------------------------

        x = (
            node.x
            + node.w
            + gap
        )

    return diagram


# ============================================================
# DEBUG / INSPECTION
# ============================================================

def layout_debug(
    diagram: Diagram,
) -> None:
    """
    Print the final geometry of every node.

    Useful for verifying that automatic sizing is actually
    being executed before rendering.
    """

    print()
    print("=== DiaForge Layout ===")

    for node in diagram.nodes.values():

        print(
            f"{node.id}: "
            f"x={node.x:.1f}, "
            f"y={node.y:.1f}, "
            f"w={node.w:.1f}, "
            f"h={node.h:.1f}, "
            f"width_explicit={node.width_explicit}, "
            f"height_explicit={node.height_explicit}"
        )

    print("=======================")
    print()