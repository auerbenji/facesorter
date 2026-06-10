import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


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
    x_values = list(range(1, len(sorted_scores) + 1))

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, sorted_scores)
    plt.xlabel("Photo rank after sorting")
    plt.ylabel("Score")
    plt.title("Face sorter score curve")
    plt.grid(True)
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
