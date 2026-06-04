import argparse
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


def largest_face(faces):
    if not faces:
        return None

    def area(face):
        x1, y1, x2, y2 = face.bbox
        return max(0, x2 - x1) * max(0, y2 - y1)

    return max(faces, key=area)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration", default="calibration")
    parser.add_argument("--out", default="out")
    parser.add_argument("--det-size", type=int, default=640)
    args = parser.parse_args()

    calibration_dir = Path(args.calibration)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    image_paths = list(iter_images(calibration_dir))
    if not image_paths:
        raise RuntimeError(f"No calibration images found in {calibration_dir}")

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(args.det_size, args.det_size))

    embeddings = []
    used_files = []
    skipped = []

    for path in tqdm(image_paths, desc="Calibrating"):
        try:
            img_rgb = load_image_rgb(path)
            img_bgr = rgb_to_bgr(img_rgb)
            faces = app.get(img_bgr)
            face = largest_face(faces)

            if face is None:
                skipped.append((str(path), "no_face"))
                continue

            emb = np.asarray(face.normed_embedding, dtype=np.float32)
            embeddings.append(emb)
            used_files.append(str(path))

        except Exception as e:
            skipped.append((str(path), f"error: {e}"))

    if len(embeddings) < 5:
        raise RuntimeError(
            f"Only {len(embeddings)} valid calibration faces found. "
            f"Use at least 5, better 10-30 clean single-person images."
        )

    embeddings = np.vstack(embeddings).astype(np.float32)

    identity_path = out_dir / "identity.npz"
    np.savez_compressed(
        identity_path,
        embeddings=embeddings,
        files=np.array(used_files),
        model_name="buffalo_l",
        det_size=args.det_size,
    )

    report_path = out_dir / "calibration_report.txt"
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"Used calibration images: {len(used_files)}\n")
        f.write(f"Skipped calibration images: {len(skipped)}\n\n")
        f.write("Used files:\n")
        for file in used_files:
            f.write(f"{file}\n")

        f.write("\nSkipped files:\n")
        for file, reason in skipped:
            f.write(f"{file}\t{reason}\n")

    print(f"Saved identity profile: {identity_path}")
    print(f"Saved report: {report_path}")
    print(f"Valid calibration faces: {len(used_files)}")


if __name__ == "__main__":
    main()