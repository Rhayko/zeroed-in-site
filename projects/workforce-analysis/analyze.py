"""Build the synthetic workforce planning case study outputs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 8242026
DEPARTMENTS = ["Operations", "Sales", "Customer Support", "Technology"]


def build_dataset(seed: int = SEED, employees: int = 720) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    department = rng.choice(DEPARTMENTS, employees, p=[0.38, 0.22, 0.24, 0.16])
    level = rng.choice(["Associate", "Specialist", "Manager"], employees, p=[0.52, 0.36, 0.12])
    tenure_months = rng.integers(3, 145, employees)
    training_hours = np.clip(rng.normal(24, 10, employees), 0, 64).round(1)
    overtime_hours = np.clip(
        rng.normal(38, 15, employees)
        + np.where(department == "Operations", 10, 0)
        + np.where(department == "Customer Support", 5, 0),
        0,
        96,
    ).round(1)
    engagement = np.clip(
        78 - 0.18 * overtime_hours + 0.12 * training_hours + rng.normal(0, 8, employees),
        35,
        100,
    ).round(1)
    absence_days = np.clip(
        rng.poisson(3.2 + 0.025 * overtime_hours - 0.018 * engagement),
        0,
        18,
    )
    exit_logit = (
        -2.35
        + 0.025 * overtime_hours
        - 0.022 * (engagement - 65)
        - 0.008 * tenure_months
        + np.where(department == "Customer Support", 0.28, 0)
    )
    exit_probability = 1 / (1 + np.exp(-exit_logit))
    voluntary_exit = rng.binomial(1, exit_probability)

    frame = pd.DataFrame(
        {
            "employee_id": [f"EMP-{n:04d}" for n in range(1, employees + 1)],
            "department": department,
            "job_level": level,
            "tenure_months": tenure_months,
            "training_hours_2025": training_hours,
            "overtime_hours_q4": overtime_hours,
            "absence_days_2025": absence_days,
            "engagement_score": engagement,
            "voluntary_exit_2025": voluntary_exit,
        }
    )
    # Missing engagement values are deliberate and remain missing in analysis.
    missing = rng.choice(frame.index, size=29, replace=False)
    frame.loc[missing, "engagement_score"] = np.nan
    return frame


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    if confidence != 0.95:
        raise ValueError("this simple implementation supports a 95% interval")
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    spread = z * np.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
    return float(center - spread), float(center + spread)


def analyze(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {
        "employee_id",
        "department",
        "job_level",
        "tenure_months",
        "training_hours_2025",
        "overtime_hours_q4",
        "absence_days_2025",
        "engagement_score",
        "voluntary_exit_2025",
    }
    missing_columns = required - set(frame.columns)
    if missing_columns:
        raise ValueError(f"missing columns: {sorted(missing_columns)}")
    if frame["employee_id"].duplicated().any():
        raise ValueError("employee_id must be unique")
    if not set(frame["voluntary_exit_2025"].unique()).issubset({0, 1}):
        raise ValueError("voluntary_exit_2025 must be 0 or 1")

    by_department = (
        frame.groupby("department", observed=True)
        .agg(
            employees=("employee_id", "size"),
            exits=("voluntary_exit_2025", "sum"),
            overtime_hours_q4_mean=("overtime_hours_q4", "mean"),
            absence_days_mean=("absence_days_2025", "mean"),
            engagement_score_mean=("engagement_score", "mean"),
            engagement_scores_present=("engagement_score", "count"),
        )
        .reset_index()
    )
    by_department["turnover_rate"] = by_department["exits"] / by_department["employees"]

    exits = int(frame["voluntary_exit_2025"].sum())
    total = len(frame)
    ci_low, ci_high = wilson_interval(exits, total)
    exited_overtime = frame.loc[frame["voluntary_exit_2025"] == 1, "overtime_hours_q4"]
    stayed_overtime = frame.loc[frame["voluntary_exit_2025"] == 0, "overtime_hours_q4"]
    mean_exit = float(exited_overtime.mean())
    mean_stay = float(stayed_overtime.mean())
    var_exit = float(exited_overtime.var(ddof=1))
    var_stay = float(stayed_overtime.var(ddof=1))
    se_squared = var_exit / len(exited_overtime) + var_stay / len(stayed_overtime)
    t_statistic = (mean_exit - mean_stay) / math.sqrt(se_squared)
    degrees_freedom = se_squared**2 / (
        (var_exit / len(exited_overtime)) ** 2 / (len(exited_overtime) - 1)
        + (var_stay / len(stayed_overtime)) ** 2 / (len(stayed_overtime) - 1)
    )
    # With more than 100 observations per group, this normal approximation is close
    # to the two-sided Welch t-test p-value and keeps the project dependency-light.
    approximate_p = math.erfc(abs(t_statistic) / math.sqrt(2))

    report = {
        "provenance": "Synthetic data generated for portfolio demonstration; no real employees.",
        "seed": SEED,
        "employees": total,
        "voluntary_exits": exits,
        "turnover_rate": exits / total,
        "turnover_rate_wilson_95_ci": [ci_low, ci_high],
        "missing_engagement_scores": int(frame["engagement_score"].isna().sum()),
        "overtime_welch_t_test": {
            "exited_mean": mean_exit,
            "stayed_mean": mean_stay,
            "mean_difference": mean_exit - mean_stay,
            "t_statistic": t_statistic,
            "degrees_freedom": degrees_freedom,
            "approximate_two_sided_p_value": approximate_p,
            "interpretation_limit": "Association in a designed simulation; not a causal estimate or individual prediction.",
        },
    }
    return by_department, report


def save_chart(summary: pd.DataFrame, path: Path) -> None:
    import matplotlib.pyplot as plt

    ordered = summary.sort_values("turnover_rate")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    fig.patch.set_facecolor("#0b100d")
    ax.set_facecolor("#0b100d")
    ax.barh(ordered["department"], ordered["turnover_rate"] * 100, color="#b7ca8e")
    ax.set_xlabel("Voluntary exits (% of department)", color="#dfe8d7")
    ax.set_title("Synthetic 2025 turnover by department", color="#f4f7ef", loc="left")
    ax.tick_params(colors="#c4cfbc")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", color="#ffffff", alpha=0.12)
    fig.tight_layout()
    fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def run(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    frame = build_dataset()
    summary, report = analyze(frame)
    frame.to_csv(output / "workforce_records.csv", index=False)
    summary.to_csv(output / "department_summary.csv", index=False)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    save_chart(summary, output / "turnover-by-department.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/reference"))
    args = parser.parse_args()
    run(args.output)
