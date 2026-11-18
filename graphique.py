
from reportlab.graphics.shapes import Drawing, Line, String, Rect
from reportlab.lib import colors
from reportlab.lib.units import mm


# ==========================================
# GRAPHIC THEME
# ==========================================

BROWN = colors.HexColor("#554238")
TAUPE = colors.HexColor("#917568")
GRID = colors.HexColor("#D8CDC5")


def payoff_chart(product, language="FR"):
    """
    Generate an illustrative payoff chart for a structured product.

    Supported families:
    - Phoenix Autocall
    - Athena Autocall
    - European Option
    - Capital Protected Note
    - Credit Linked Note

    All values are expressed as a fraction of notional.

    The charts exclude previously paid coupons,
    transaction costs, issuer default and early redemption.

    Athena: the chart illustrates principal redemption only,
    not any additional maturity premium.
    """

    fr = language == "FR"
    #family = product.family
    family = getattr(product, "family", None)

    if family is None:
        family = type(product).__name__

    if family == "Phoenix":
        family = "Phoenix Autocall"
    elif family == "Athena":
        family = "Athena Autocall"

    width = 174 * mm
    height = 78 * mm

    drawing = Drawing(width, height)

    left = 15 * mm
    right = 5 * mm
    bottom = 15 * mm
    top = 9 * mm

    plot_width = width - left - right
    plot_height = height - bottom - top

    # ==========================================
    # DRAWING HELPERS
    # ==========================================

    def line(x1, y1, x2, y2, color=BROWN, thickness=2):
        drawing.add(
            Line(
                x1, y1, x2, y2,
                strokeColor=color,
                strokeWidth=thickness
            )
        )

    def text(x, y, value, size=7, color=TAUPE):
        drawing.add(
            String(
                x, y, str(value),
                fontName="Helvetica",
                fontSize=size,
                fillColor=color
            )
        )

    def x_pos(x):
        return left + x / 1.5 * plot_width

    def y_pos(y, maximum):
        return bottom + y / maximum * plot_height

    # ==========================================
    # CREDIT LINKED NOTE
    # ==========================================

    if family == "Credit Linked Note":

        recovery = float(product.recovery)

        if not 0 <= recovery <= 1:
            raise ValueError(
                "Recovery must be between 0 and 1."
            )

        text(
            left,
            height - 4 * mm,
            "Principal repayment / Notional"
            if not fr else
            "Remboursement du capital / Nominal"
        )

        scenarios = [
            (
                "No credit event"
                if not fr else
                "Sans evenement",
                1.0
            ),
            (
                "Credit event"
                if not fr else
                "Avec evenement",
                recovery
            )
        ]

        line(
            left,
            bottom,
            left + plot_width,
            bottom,
            GRID,
            1
        )

        for i, (label, value) in enumerate(scenarios):

            center_x = left + plot_width * (
                0.25 + 0.5 * i
            )

            bar_width = 25 * mm
            bar_height = value * plot_height

            drawing.add(
                Rect(
                    center_x - bar_width / 2,
                    bottom,
                    bar_width,
                    bar_height,
                    fillColor=BROWN,
                    strokeColor=None
                )
            )

            text(
                center_x - 15 * mm,
                bottom - 7 * mm,
                label
            )

            text(
                center_x - 6 * mm,
                bottom + bar_height + 3 * mm,
                f"{value:.0%}"
            )

        return drawing

    # ==========================================
    # PAYOFF FUNCTIONS
    # ==========================================

    def payoff_ratio(x):

        # PHOENIX / ATHENA
        if family in (
            "Phoenix Autocall",
            "Athena Autocall"
        ):

            barrier = float(
                product.protection_barrier
            )

            if x >= barrier:
                return 1.0

            return x

        # EUROPEAN OPTION
        if family == "European Option":

            strike = float(product.strike)
            option_type = product.option_type

            if option_type == "Put":
                return max(strike - x, 0.0)

            if option_type == "Call":
                return max(x - strike, 0.0)

            raise ValueError(
                f"Unsupported option type: {option_type}"
            )

        # CAPITAL PROTECTED NOTE
        if family == "Capital Protected Note":

            protection = float(
                product.protection
            )

            participation = float(
                product.participation
            )

            strike = float(product.strike)

            return (
                protection
                + participation * max(x - strike, 0.0)
            )

        raise ValueError(
            f"Unsupported product family: {family}"
        )

    # ==========================================
    # GENERATE PAYOFF POINTS
    # ==========================================

    xs = [
        i * 1.5 / 300
        for i in range(301)
    ]

    if family in (
        "Phoenix Autocall",
        "Athena Autocall"
    ):

        barrier = float(
            product.protection_barrier
        )

        if 0 < barrier < 1.5:
            xs.extend([
                barrier - 0.000001,
                barrier
            ])

    xs = sorted(set(xs))

    points = [
        (x, payoff_ratio(x))
        for x in xs
    ]

    maximum_y = max(
        1.15,
        max(y for _, y in points) * 1.12
    )

    # ==========================================
    # AXES
    # ==========================================

    line(
        left,
        bottom,
        left,
        bottom + plot_height,
        GRID,
        1
    )

    line(
        left,
        bottom,
        left + plot_width,
        bottom,
        GRID,
        1
    )

    for x in [
        0, 0.25, 0.50, 0.75,
        1.0, 1.25, 1.50
    ]:

        text(
            x_pos(x) - 4 * mm,
            bottom - 6 * mm,
            f"{x:.0%}"
        )

    text(
        left,
        height - 4 * mm,
        "Payoff / Notional"
        if not fr else
        "Remboursement / Nominal"
    )

    # ==========================================
    # DRAW CURVE
    # ==========================================

    for i in range(len(points) - 1):

        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        line(
            x_pos(x1),
            y_pos(y1, maximum_y),
            x_pos(x2),
            y_pos(y2, maximum_y)
        )

    # ==========================================
    # PROTECTION BARRIER
    # ==========================================

    if family in (
        "Phoenix Autocall",
        "Athena Autocall"
    ):

        barrier = float(
            product.protection_barrier
        )

        if 0 <= barrier <= 1.5:

            bx = x_pos(barrier)

            line(
                bx,
                bottom,
                bx,
                bottom + plot_height,
                TAUPE,
                0.8
            )

            text(
                bx + 2 * mm,
                bottom + plot_height - 4 * mm,
                "Protection barrier"
                if not fr else
                "Barriere de protection"
            )

    # ==========================================
    # STRIKE
    # ==========================================

    if family in (
        "European Option",
        "Capital Protected Note"
    ):

        strike = float(
            product.strike
        )

        if 0 <= strike <= 1.5:

            sx = x_pos(strike)

            line(
                sx,
                bottom,
                sx,
                bottom + plot_height,
                GRID,
                0.8
            )

            text(
                sx + 2 * mm,
                bottom + plot_height - 4 * mm,
                "Strike"
            )

    return drawing
