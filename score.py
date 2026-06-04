import argparse
import csv
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from insightface.app import FaceAnalysis
from tqdm import tqdm


register_heif_opener()

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".heic", ".heif", ".hif"}


def load_image_rgb(path: Path) -> np.ndarray:
    """
    Loads JPG/HEIF/HIF as RGB numpy array.
    Applies EXIF orientation.
    """
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        return np.array(img)


def rgb_to_bgr(img_rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)


def iter_images(folder: Path):
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def best_identity_score(face_embeddings: list[np.ndarray], identity_embeddings: np.ndarray) -> float:
    """
    Both InsightFace embeddings are normalized.
    Cosine similarity is therefore dot product.
    We compare every detected face against every reference face.
    """
    if not face_embeddings:
        return -1.0

    best = -1.0
    for emb in face_embeddings:
        scores = identity_embeddings @ emb
        local_best = float(np.max(scores))
        best = max(best, local_best)

    return best


def load_existing_scores(scores_path: Path) -> set[str]:
    """
    Barebone resume support:
    if scores.csv already exists, skip paths already present.
    """
    done = set()
    if not scores_path.exists():
        return done

    with scores_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            done.add(row["file"])
    return done


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data")
    parser.add_argument("--out", default="out")
    parser.add_argument("--identity", default="out/identity.npz")
    parser.add_argument("--det-size", type=int, default=640)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_dir = Path(args.out)
    identity_path = Path(args.identity)
    scores_path = out_dir / "scores.csv"

    out_dir.mkdir(parents=True, exist_ok=True)

    if not identity_path.exists():
        raise RuntimeError(f"Missing identity profile: {identity_path}. Run calibrate.py first.")

    identity = np.load(identity_path, allow_pickle=True)
    identity_embeddings = identity["embeddings"].astype(np.float32)

    image_paths = list(iter_images(data_dir))
    if not image_paths:
        raise RuntimeError(f"No images found in {data_dir}")

    already_done = load_existing_scores(scores_path) if args.resume else set()

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(args.det_size, args.det_size))

    write_header = not scores_path.exists() or not args.resume

    mode = "a" if args.resume else "w"
    with scores_path.open(mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file",
                "score",
                "num_faces",
                "status",
                "error",
            ],
        )

        if write_header:
            writer.writeheader()

        for path in tqdm(image_paths, desc="Scoring"):
            relative_path = str(path.relative_to(data_dir))

            if relative_path in already_done:
                continue

            try:
                img_rgb = load_image_rgb(path)
                img_bgr = rgb_to_bgr(img_rgb)
                faces = app.get(img_bgr)

                face_embeddings = [
                    np.asarray(face.normed_embedding, dtype=np.float32)
                    for face in faces
                ]

                score = best_identity_score(face_embeddings, identity_embeddings)

                writer.writerow(
                    {
                        "file": relative_path,
                        "score": f"{score:.6f}",
                        "num_faces": len(faces),
                        "status": "ok",
                        "error": "",
                    }
                )

            except Exception as e:
                writer.writerow(
                    {
                        "file": relative_path,
                        "score": "-1.000000",
                        "num_faces": 0,
                        "status": "error",
                        "error": str(e),
                    }
                )

    print(f"Saved scores: {scores_path}")


if __name__ == "__main__":
    main()