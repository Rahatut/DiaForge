import math


def port_point(node, port):

    x = node.x
    y = node.y

    w = node.w
    h = node.h

    ports = {

        "west":
            (x, y + h / 2),

        "east":
            (x + w, y + h / 2),

        "north":
            (x + w / 2, y),

        "south":
            (x + w / 2, y + h),

        "center":
            (x + w / 2, y + h / 2),
    }

    return ports.get(
        port,
        ports["east"],
    )


def route(
    edge,
    source,
    target,
):

    start = port_point(
        source,
        edge.start_port,
    )

    end = port_point(
        target,
        edge.end_port,
    )


    # -------------------------
    # Curved
    # -------------------------

    if edge.route == "curve":

        mx = (
            start[0] + end[0]
        ) / 2

        my = (
            start[1] + end[1]
        ) / 2

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        length = max(
            1,
            math.hypot(dx, dy),
        )

        control = (

            mx
            -
            dy / length
            * edge.curve,

            my
            +
            dx / length
            * edge.curve,
        )

        return {
            "kind": "quad",

            "a": start,

            "c": control,

            "b": end,
        }


    # -------------------------
    # Orthogonal
    # -------------------------

    if edge.route == "orthogonal":

        middle_x = (
            start[0] + end[0]
        ) / 2

        return {

            "kind":
                "orthogonal",

            "points": [

                start,

                (
                    middle_x,
                    start[1],
                ),

                (
                    middle_x,
                    end[1],
                ),

                end,
            ],

            "radius": 12,
        }


    # -------------------------
    # Straight
    # -------------------------

    return {

        "kind": "line",

        "a": start,

        "b": end,
    }