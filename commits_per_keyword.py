import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from git import Repo
import itertools
import os
import re

# ----------------------------------------------------
# Convert YY.WW - datetime object
# ----------------------------------------------------
def week_to_date(week_code):
    if not week_code:
        return None
    try:
        yy, ww = week_code.split(".")
        yy = int(yy)
        ww = int(ww)
        year = 2000 + yy if yy < 50 else 1900 + yy
        return datetime.strptime(f"{year}-W{ww:02d}-1", "%G-W%V-%u")
    except Exception:
        print(f"Invalid week format: {week_code}. Must be YY.WW (example: 23.05).")
        return None

# ====================================================
# Global bar width
# ====================================================
def compute_global_width(dates, max_width=15, min_width=2):
    if len(dates) < 2:
        return max_width
    deltas = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    min_delta = min(deltas)
    return max(min(min_delta * 0.6, max_width), min_width)


# ----------------------------------------------------
# Plot commits per keyword per week/month
# ----------------------------------------------------
def plot_commits(keywords, repo_paths, branches,
                 week_from=None, week_to=None):

    # -----------------------------------------
    # Parse keywords from quotes
    # -----------------------------------------
    if isinstance(keywords, str):
        keywords = re.findall(r'"([^"]+)"', keywords)

    keywords = [k.lower() for k in keywords]

    if not keywords:
        print('No valid keywords provided. Use quotes like: "bug" "fix" "UI"')
        return

    if isinstance(repo_paths, str):
        repo_paths = [r.strip() for r in repo_paths.replace(",", " ").split() if r.strip()]
    if isinstance(branches, str):
        branches = [b.strip() for b in branches.replace(",", " ").split() if b.strip()]

    if not repo_paths or not branches:
        print("No repositories or branches provided.")
        return

    week_colors = itertools.cycle([
        "skyblue", "blue", "cyan", "navy", "deepskyblue",
        "orange", "red", "coral", "darkred", "gold",
        "green", "lime", "darkgreen",
        "purple", "violet", "magenta"
    ])

    month_colors = itertools.cycle([
        "skyblue", "blue", "cyan", "navy", "deepskyblue",
        "orange", "red", "coral", "darkred", "gold",
        "green", "lime", "darkgreen",
        "purple", "violet", "magenta"
    ])

    start_dt = week_to_date(week_from)
    end_dt = week_to_date(week_to)

    plot_data = []

    # ----------------------------------------------------
    # Process each repo and branch
    # ----------------------------------------------------
    for repo_path in repo_paths:
        repo_name = os.path.basename(repo_path.rstrip("/\\"))

        try:
            repo = Repo(repo_path)
        except Exception:
            print(f"Could not open repository: {repo_path}")
            continue

        for branch in branches:
            try:
                commits = list(repo.iter_commits(branch))
            except Exception:
                print(f"Branch '{branch}' not found in repo '{repo_name}'. Skipping.")
                continue

            # -----------------------------------------
            # Filter commits by message keywords
            # -----------------------------------------
            matched_commits = []
            for c in commits:
                msg = c.message.lower()
                if any(k in msg for k in keywords):
                    matched_commits.append(c)

            if not matched_commits:
                print(f"No commits with keywords {keywords} in {repo_name}:{branch}")
                continue

            commit_dates = [
                datetime.fromtimestamp(c.committed_date)
                for c in matched_commits
            ]

            df = pd.DataFrame({"date": commit_dates})
            df["week"] = df["date"].dt.strftime("%G-%V")
            df["month"] = df["date"].dt.strftime("%Y-%m")
            df["week_date"] = df["date"].apply(
                lambda d: datetime.strptime(d.strftime("%G-W%V-1"), "%G-W%V-%u")
            )

            if start_dt:
                df = df[df["week_date"] >= start_dt]
            if end_dt:
                df = df[df["week_date"] <= end_dt]

            if df.empty:
                print(f"No commits in selected week range for {repo_name}:{branch}")
                continue

            commits_week = df.groupby("week").size()
            commits_month = df.groupby("month").size()

            week_dates = [
                datetime.strptime(
                    f"{w.split('-')[0]}-W{int(w.split('-')[1]):02d}-1",
                    "%G-W%V-%u"
                )
                for w in commits_week.index
            ]

            month_dates = [
                datetime.strptime(m + "-01", "%Y-%m-%d")
                for m in commits_month.index
            ]

            week_labels = [
                f"wk{w.split('-')[0][2:]}.{int(w.split('-')[1])}"
                for w in commits_week.index
            ]
            month_labels = [
                f"mo{m.split('-')[0][2:]}.{int(m.split('-')[1])}"
                for m in commits_month.index
            ]

            # Count unique authors of matched commits
            unique_authors = len({c.author.name for c in matched_commits})

            plot_data.append({
                "label": f"{repo_name}:{branch}",
                "week_dates": week_dates,
                "month_dates": month_dates,
                "commits_week": commits_week.values,
                "commits_month": commits_month.values,
                "week_labels": week_labels,
                "month_labels": month_labels,
                "week_label_with_total": (f"{repo_name}:{branch} (commits:{commits_week.sum()}, authors:{unique_authors})"),
                "month_label_with_total": (f"{repo_name}:{branch} (commits:{commits_month.sum()}, authors:{unique_authors})")
            })

    if not plot_data:
        print("No data to plot.")
        return

    all_week_dates = sorted({d for item in plot_data for d in item["week_dates"]})
    all_month_dates = sorted({d for item in plot_data for d in item["month_dates"]})

    all_week_labels = [
        f"wk{d.strftime('%G')[2:]}.{int(d.strftime('%V'))}"
        for d in all_week_dates
    ]
    all_month_labels = [
        f"mo{d.strftime('%Y')[2:]}.{int(d.strftime('%m'))}"
        for d in all_month_dates
    ]

    global_week_width = compute_global_width(all_week_dates)
    global_month_width = compute_global_width(all_month_dates)

    # ====================================================
    # Weekly plot
    # ====================================================
    plt.figure(figsize=(14, 6))
    bottom_week = {d:0 for d in all_week_dates}

    for item in plot_data:
        color = next(week_colors)
        heights = item["commits_week"]
        plt.bar(
            item["week_dates"],
            heights,
            width=global_week_width,
            alpha=0.8,
            color=color,
            bottom=[bottom_week[d] for d in item["week_dates"]],
            label=item["week_label_with_total"]
        )
        for idx, d in enumerate(item["week_dates"]):
            bottom_week[d] += heights[idx]

    plt.xticks(all_week_dates, all_week_labels, rotation=45, ha="right")
    plt.ylabel("Number of commits")

    # Build range text
    if not week_from and not week_to:
        range_text = " | All time"
    elif not week_from and week_to:
        range_text = f" | From start → wk{week_to}"
    elif week_from and not week_to:
        range_text = f" | wk{week_from} → Current week"
    else:  # both provided
        range_text = f" | wk{week_from} → wk{week_to}"

    plt.title(f"Commits per week containing keywords: {', '.join(keywords)}{range_text}")
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.legend()
    plt.tight_layout()

    safe_keywords = "_".join(k.replace(" ", "_") for k in keywords)
    week_filename = (
        f"commits_keywords_{safe_keywords}"
        + (f"_{week_from}_{week_to}" if week_from or week_to else "")
        + "_weeks.png"
    )
    plt.savefig(week_filename)
    print(f"Saved weekly plot as: {week_filename}")

    # ====================================================
    # Monthly plot
    # ====================================================
    plt.figure(figsize=(14, 6))
    bottom_month = {d:0 for d in all_month_dates}

    for item in plot_data:
        color = next(month_colors)
        heights = item["commits_month"]
        plt.bar(
            item["month_dates"],
            heights,
            width=global_month_width,
            alpha=0.8,
            color=color,
            bottom=[bottom_month[d] for d in item["month_dates"]],
            label=item["month_label_with_total"]
        )
        for idx, d in enumerate(item["month_dates"]):
            bottom_month[d] += heights[idx]

    plt.xticks(all_month_dates, all_month_labels, rotation=45, ha="right")
    plt.ylabel("Number of commits")
    plt.title(f"Commits per month containing keywords: {', '.join(keywords)}{range_text}")
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.legend()
    plt.tight_layout()

    month_filename = (
        f"commits_keywords_{safe_keywords}"
        + (f"_{week_from}_{week_to}" if week_from or week_to else "")
        + "_months.png"
    )
    plt.savefig(month_filename)
    print(f"Saved monthly plot as: {month_filename}")

# ----------------------------------------------------
# Main
# ----------------------------------------------------
if __name__ == "__main__":
    keywords = input('Enter keywords inside quotes (e.g. "misra" "bug" "fix"): ').strip()
    repos = input("Enter paths to git repos (comma or space separated): ").strip()
    branches = input("Enter branches (comma or space-separated): ").strip()
    week_from = input("Enter week-from (YY.WW, blank for none): ").strip()
    week_to = input("Enter week-to (YY.WW, blank for none): ").strip()

    plot_commits(keywords, repos, branches, week_from, week_to)
