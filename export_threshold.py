import argparse
import csv
import shutil
from pathlib import Path


def safe_threshold_name(threshold: float) -> str:
    return f"threshold_{threshold:.2f}"


def copy_file_preserve_structure(source: Path, data_dir: Path, target_root: Path):
    relative_path = source.relative_to(data_dir)
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data")
    parser.add_argument("--scores", default="out/scores.csv")
    parser.add_argument("--out", default="out")
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data)
    scores_path = Path(args.scores)
    out_dir = Path(args.out)

    if not scores_path.exists():
        raise RuntimeError(f"Missing scores file: {scores_path}. Run score.py first.")

    target_root = out_dir / safe_threshold_name(args.threshold)

    if args.clear and target_root.exists():
        shutil.rmtree(target_root)

    target_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    considered = 0
    missing = 0

    with scores_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            considered += 1

            try:
                score = float(row["score"])
            except Exception:
                continue

            if row.get("status") != "ok":
                continue

            if score < args.threshold:
                continue

            source = data_dir / row["file"]

            if not source.exists():
                missing += 1
                continue

            copy_file_preserve_structure(source, data_dir, target_root)
            copied += 1

    print(f"Threshold: {args.threshold:.2f}")
    print(f"Considered rows: {considered}")
    print(f"Copied files: {copied}")
    print(f"Missing source files: {missing}")
    print(f"Output: {target_root}")


if __name__ == "__main__":
    main()