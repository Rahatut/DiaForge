def auto_layout(
    diagram,
    gap=70,
    margin=70,
):
    """
    Very simple deterministic layout.

    Explicit x/y coordinates always win.
    This is intentionally replaceable later with
    a real graph layout engine.
    """

    x = margin

    y = margin

    for node in diagram.nodes.values():

        if node.x is None:

            node.x = x

        if node.y is None:

            node.y = y

        x += node.w + gap

        if (
            x + node.w
            >
            diagram.canvas.width - margin
        ):

            x = margin

            y += 230

    return diagram