"""Analyze a reproducible synthetic sleep and performance study."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 9132026


def build_dataset(seed: int = SEED, participants: int = 96) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ids = [f"P-{n:03d}" for n in range(1, participants + 1)]
    baseline_speed = rng.normal(292, 24, participants)
    baseline_jump = rng.normal(45, 6, participants)
    rows = []
    for index, participant in enumerate(ids):
        order = "restricted-first" if index % 2 == 0 else "rested-first"
        for condition in ["Rested", "Restricted"]:
            sleep = rng.normal(7.65 if condition == "Rested" else 5.25, 0.45)
            reaction = baseline_speed[index] - 10.5 * (sleep - 6.5) + rng.normal(0, 11)
            jump = baseline_jump[index] + 0.85 * (sleep - 6.5) + rng.normal(0, 2.1)
            rows.append(
                {
                    "participant_id": participant,
                    "condition": condition,
                    "condition_order": order,
                    "sleep_hours": round(float(sleep), 2),
                    "reaction_time_ms": round(float(reaction), 1),
                    "countermovement_jump_cm": round(float(jump), 1),
                }
            )
    return pd.DataFrame(rows)


def analyze(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {
        "participant_id",
        "condition",
        "condition_order",
        "sleep_hours",
        "reaction_time_ms",
        "countermovement_jump_cm",
    }
    if required - set(frame.columns):
        raise ValueError("study file is missing required columns")
    counts = frame.groupby("participant_id").size()
    if not counts.eq(2).all() or frame.duplicated(["participant_id", "condition"]).any():
        raise ValueError("each participant must have one record per condition")
    if set(frame["condition"]) != {"Rested", "Restricted"}:
        raise ValueError("conditions must be Rested and Restricted")

    summary = (
        frame.groupby("condition", observed=True)
        .agg(
            sessions=("participant_id", "size"),
            sleep_hours_mean=("sleep_hours", "mean"),
            reaction_time_ms_mean=("reaction_time_ms", "mean"),
            reaction_time_ms_sd=("reaction_time_ms", "std"),
            jump_cm_mean=("countermovement_jump_cm", "mean"),
            jump_cm_sd=("countermovement_jump_cm", "std"),
        )
        .reset_index()
    )
    wide = frame.pivot(index="participant_id", columns="condition", values="reaction_time_ms")
    difference = wide["Restricted"] - wide["Rested"]
    sem = float(difference.std(ddof=1) / np.sqrt(len(difference)))
    t_statistic = float(difference.mean() / sem)
    # df=95. This fixed critical value is explicit and reproducible.
    margin = 1.985251 * sem
    paired_p = math.erfc(abs(t_statistic) / math.sqrt(2))
    pearson_r = float(np.corrcoef(frame["sleep_hours"], frame["reaction_time_ms"])[0, 1])
    fisher_z = math.atanh(pearson_r) * math.sqrt(len(frame) - 3)
    correlation_p = math.erfc(abs(fisher_z) / math.sqrt(2))
    slope, intercept = np.polyfit(frame["sleep_hours"], frame["reaction_time_ms"], 1)
    predicted = intercept + slope * frame["sleep_hours"]
    r_squared = 1 - np.sum((frame["reaction_time_ms"] - predicted) ** 2) / np.sum(
        (frame["reaction_time_ms"] - frame["reaction_time_ms"].mean()) ** 2
    )

    report = {
        "provenance": "Synthetic crossover study generated for portfolio demonstration; no real participants.",
        "seed": SEED,
        "participants": int(frame["participant_id"].nunique()),
        "sessions": len(frame),
        "paired_reaction_time_test": {
            "mean_restricted_minus_rested_ms": float(difference.mean()),
            "difference_95_ci_ms": [float(difference.mean() - margin), float(difference.mean() + margin)],
            "t_statistic": t_statistic,
            "degrees_freedom": len(difference) - 1,
            "approximate_two_sided_p_value": paired_p,
        },
        "sleep_reaction_correlation": {
            "pearson_r": pearson_r,
            "approximate_two_sided_p_value": correlation_p,
        },
        "simple_linear_regression": {
            "outcome": "reaction_time_ms",
            "predictor": "sleep_hours",
            "slope_ms_per_hour": float(slope),
            "intercept_ms": float(intercept),
            "r_squared": float(r_squared),
        },
        "interpretation_limit": "The effects were encoded in a simulation. Association and regression do not establish causation in observational data.",
    }
    return summary, report


def save_chart(frame: pd.DataFrame, path: Path) -> None:
    import matplotlib.pyplot as plt

    slope, intercept = np.polyfit(frame["sleep_hours"], frame["reaction_time_ms"], 1)
    x = np.linspace(frame.sleep_hours.min(), frame.sleep_hours.max(), 100)
    colors = frame.condition.map({"Rested": "#b7ca8e", "Restricted": "#70845c"})
    fig, ax = plt.subplots(figsize=(8, 4.8))
    fig.patch.set_facecolor("#0b100d")
    ax.set_facecolor("#0b100d")
    ax.scatter(frame.sleep_hours, frame.reaction_time_ms, c=colors, s=28, alpha=0.72, edgecolors="none")
    ax.plot(x, intercept + slope * x, color="#f2f5eb", linewidth=1.8)
    ax.set_title("Sleep and reaction time in the synthetic study", color="#f4f7ef", loc="left")
    ax.set_xlabel("Sleep in prior 24 hours")
    ax.set_ylabel("Reaction time (ms, lower is faster)")
    ax.tick_params(colors="#c4cfbc")
    ax.xaxis.label.set_color("#dfe8d7")
    ax.yaxis.label.set_color("#dfe8d7")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(color="#ffffff", alpha=0.10)
    fig.tight_layout()
    fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def run(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    frame = build_dataset()
    summary, report = analyze(frame)
    frame.to_csv(output / "performance_sessions.csv", index=False)
    summary.to_csv(output / "condition_summary.csv", index=False)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    save_chart(frame, output / "sleep-reaction-analysis.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/reference"))
    args = parser.parse_args()
    run(args.output)
