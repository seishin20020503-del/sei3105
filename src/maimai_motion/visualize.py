"""Optional visualization: plot a hand trajectory with detected touch points."""
from .geometry import Point
from .touch_detection import TouchEvent


def plot_trajectory(
    times: list[float],
    positions: list[Point],
    events: list[TouchEvent],
    out_path: str,
    title: str = "",
) -> None:
    import matplotlib.pyplot as plt

    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(xs, ys, "-", linewidth=0.7, alpha=0.6, label="trajectory")
    if events:
        ex = [e.position[0] for e in events]
        ey = [e.position[1] for e in events]
        ax.scatter(ex, ey, c="red", s=30, zorder=3, label="touch")
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel("x (px)")
    ax.set_ylabel("y (px)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
