import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_scores(scores_path: Path) -> list[float]:
    scores = []

    with scores_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if "score" not in reader.fieldnames:
            raise RuntimeError(f"Missing required column 'score' in {scores_path}")

        for row in reader:
            try:
                scores.append(float(row["score"]))
            except Exception:
                continue

    return sorted(scores, reverse=True)


def plot_scores(sorted_scores: list[float], output_path: Path):
    
    x_values = np.arange(1, len(sorted_scores) + 1)
    y_values = np.asarray(sorted_scores)

    no_person = y_values == -1
    identity_person = (y_values != -1) & (y_values >= 1.25*y_values[y_values != -1].mean())
    detected_person = (y_values != -1) & ~(y_values >= 1.25*y_values[y_values != -1].mean())

    plt.figure(figsize=(10, 6))
    plt.scatter(x_values[identity_person],y_values[identity_person],s=14,label="likely to contain the identity person")
    plt.scatter(x_values[detected_person],y_values[detected_person],s=14,label="photos with at least one low-score person, use with caution")
    plt.scatter(x_values[no_person],y_values[no_person],s=14,label="values of -1 hold no person, probably landscape photos")
    
    non_empty_scores = np.flatnonzero(y_values > -1)
    empty_scores = np.flatnonzero(y_values == -1)
    if len(non_empty_scores) > 0 and len(empty_scores) > 0:
        boundary_x = (x_values[non_empty_scores[-1]] + x_values[empty_scores[0]]) / 2
        fraction = 100 - boundary_x/y_values.size * 100
        plt.axvline(
            boundary_x,
            linestyle="--",
            color="black",
            linewidth=1,
            label=f"cutoff; {fraction:.0f}% is probably landscape",
        )

    plt.xlabel("Photo number")
    plt.ylabel("Score")
    plt.title("Score; sorted, decreasing order")
    plt.ylim([-1.1,1.1])
    plt.grid(False)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, format="svg")
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default="out/scores.csv")
    parser.add_argument("--out", default="out")
    parser.add_argument("--filename", default="L-curve.svg")
    args = parser.parse_args()

    scores_path = Path(args.scores)
    out_dir = Path(args.out)
    output_path = out_dir / args.filename

    if not scores_path.exists():
        raise RuntimeError(f"Missing scores file: {scores_path}. Run score.py first.")

    out_dir.mkdir(parents=True, exist_ok=True)

    sorted_scores = load_scores(scores_path)
    if not sorted_scores:
        raise RuntimeError(f"No valid scores found in {scores_path}")

    plot_scores(sorted_scores, output_path)

    print(f"Loaded scores: {len(sorted_scores)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
