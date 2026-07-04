"""Render the leaderboard as a grouped bar chart (matplotlib, headless)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from eval.leaderboard import Leaderboard  # noqa: E402

_COLORS = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#0EA5E9", "#8B5CF6"]


def render_leaderboard_chart(
    lb: Leaderboard, path: str | Path, title: str = "Model leaderboard"
) -> Path:
    models = sorted(lb, key=lambda m: lb[m]["overall"], reverse=True)
    tasks = [t for t in next(iter(lb.values())) if t != "overall"]
    width = 0.8 / max(1, len(tasks))

    fig, ax = plt.subplots(figsize=(1.6 * len(models) + 3, 4.5))
    for i, task in enumerate(tasks):
        xs = [j + i * width for j in range(len(models))]
        ax.bar(
            xs, [lb[m][task] for m in models], width, label=task, color=_COLORS[i % len(_COLORS)]
        )

    ax.set_xticks([j + width * (len(tasks) - 1) / 2 for j in range(len(models))])
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("pass rate")
    ax.set_title(title, fontweight="bold")
    ax.legend(title="task", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    out = Path(path)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
