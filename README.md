# Face sorter

Minimal local workflow to find photos that likely contain a target person's face.

## 1. Create the environment

Use Python 3.12 and run

```bash
python --version
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 2. Required folder structure

There are three folders necessary to run the scripts

### Folders

- `calibration/`: paste reference photos of the target person here
- `data/`: photos to score
- `out/`: generated outputs with respect to score

create the folders via

```bash
mkdir calibration data
```
and paste your files accordinly.
`out` is automatically created when running `calibration.py` or `score.py`



### Supported image formats for data folder:

```text
.jpg, .jpeg, .heic, .heif, .hif
```

## 3. Run scripts in order

### Step 1: Create identity profile

Use approx 10-20 photos of your target person as calibration data.
I used Apple Photos person library and selected front and side photos, with and without hat/cap, no sunglasses.

Run

```bash
python calibrate.py --calibration calibration --out out --identity identity_person.npz
```

yielding

```text
out/identity_person.npz
```

holding a 512-dimensional identity vector of the face of interest.

### Step 2: Score all images

Run

```bash
python score.py --data data --out out --identity out/identity_person.npz
```

yielding

```text
out/scores.csv
```
the scoring file contains [image_dir | score | number of people on photo | scoring ok / not ok]
This is the expensive step. While running, it shows a progress bar with `it/s` and a `runtime estimate`.

### Step 3: Generate a scoring visualization 'L-curve'

Run

```bash
python visualization.py --scores out/scores.csv --out out
```

yielding

```text
out/L-curve.svg
```

Compare your visualization to the `L-curve.svg` in the repository.
Changes in the slope's curve indicate a drop in confidence.
Try to match your treshold cut-off to changes in the L-cuves slope to disect confidence regions.
The attached 'L-curve.svg' in the repository holds information on how to interpret the score.

- Photos with scores from `0.8` to `0.4` typically hold triple-A grade identify photos.
- Photos with scores from `0.4` to `0.2` typically hold some positives but are noisy with fale positives.
- Photos with scores from `0.2` to `0.0` typically hold many false positives.
- Values of `-1` typically hold landscape photos

Depending on the quality of your `calibration.npz` file your scoring may vary.
The curve, however, should look similar.

### Step 4: Export by threshold

Run

```bash
python export_threshold.py --data data --scores out/scores.csv --out out --threshold 0.50 --clear
```

yielding

```text
out/threshold_0.50/
```

the folder with the extracted photos.

### Note
You may also run a threshold window, carving out confidence regions as indicated by the `L-curve.svg` by running
```bash
python export_threshold.py --data data --scores out/scores.csv --out out --threshold 0.50 --max 0.70 --clear
```