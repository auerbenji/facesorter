# Face sorter

Minimal local workflow to find photos that likely contain a target person's face.

## 1. Create the environment

```bash
conda env create -f facesorter.yml
conda activate facesorter
```

## 2. Required folder structure

```text
root/
  calibration/
  data/
  out/

  calibrate.py
  score.py
  export_threshold.py
```

### Folders

- `calibration/`: clean reference photos of the target person.
- `data/`: photos to scan.
- `out/`: generated outputs.

Supported image formats:

```text
.jpg
.jpeg
.heic
.heif
.hif
```

## 3. Run order

### Step 1: Create identity profile

Use approx 10-20 photos of your target person as calibration data.
I used Apple Photos person library and selected front and side photos, with and without hat/cap, no sunglasses.

```bash
python calibrate.py --calibration calibration --out out
```

Creates:

```text
out/identity.npz
```

### Step 2: Score all images

```bash
python score.py --data data --out out
```

Creates:

```text
out/scores.csv
```

This is the expensive step. It shows a progress bar with `it/s`.

Runtime estimate:

```text
remaining_minutes = remaining_items / iterations_per_second / 60
```

### Step 3: Export by threshold

```bash
python export_threshold.py --data data --scores out/scores.csv --out out --threshold 0.52 --clear
```

Creates:

```text
out/threshold_0.52/
```

Run this step repeatedly with different thresholds:

```bash
python export_threshold.py --data data --scores out/scores.csv --out out --threshold 0.50 --clear
python export_threshold.py --data data --scores out/scores.csv --out out --threshold 0.45 --clear
```

Higher threshold means fewer, stricter matches. Lower threshold means more matches, with more false positives.

## 4. Custom folder names

Folder names can be changed. Example:

```bash
python score.py --data input --out results
python export_threshold.py --data input --scores results/scores.csv --out results --threshold 0.52 --clear
```
