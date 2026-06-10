# Face sorter

Minimal local workflow to find photos that likely contain a target person's face.

There are two options for installation
1) conda with facesorter.yml
2) pip with requirements.txt

## 1. Create the environment

### Option A: pip with `requirements.txt`

Use this option if you want a standard Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Option B: conda with 'facesorter.yml' 1. Create the environment

```bash
conda env create -f facesorter.yml
conda activate facesorter
```

## 2. Required folder structure

There are three folders necessary to run the scripts

```text
root/
  calibration/
  data/
  out/
```
create the folders via

```bash
mkdir calibration data out
```

### Folders

- `calibration/`: paste reference photos of the target person here
- `data/`: photos to score
- `out/`: generated outputs with respect to score

Supported image formats for data folder:

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
Note that this identity is a personalized identity vector that may be stored for future use.

### Step 2: Score all images

```bash
python score.py --data data --out out
```

Note that a personalized identity vector may be used
```bash
python score.py --data data --out out --identity out/identity_Person.npz
```

this creates

```text
out/scores.csv
```
the scoring file containing score, number of people on photo, scoring ok / not ok information.
This is the expensive step. It shows a progress bar with `it/s` and a `runtime estimate`

### Step 3: Generate a scoring visualization 'L-curve'

Run

```bash
python visualize.py --data data --out out
```
to get a visual impression of the scored data.
Compare your visualization to the `L-curve.svg` in the repository.
Changes in the slope's curve indicate a drop in confidence.
Try to match your treshold cutoffs to changes in the L-cuves slope to disect confidence regions.
For the attached `.svg` file this translates to the following findings:
Photos with scores from `0.8` to `0.4` hold triple-A grade curated face recognition data.
Photos with scores from `0.4` to `0.2` hold some positives but are noisy with fale positives.
Photos with scores from `0.2` to `0.0 ` hold many false positives.
Values of `-1` mean there is no face recognition indication that this is typically a landscape photo.
Depending on the quality of your `calibration.npz` file your scoring may vary.
The curve, however, should look similar.

### Step 4: Export by threshold

```bash
python export_threshold.py --data data --scores out/scores.csv --out out --threshold 0.52 --clear
```

Creates:

```text
out/threshold_0.52/
```

You may also run a threshold window, carving out confidence region
```bash
python export_threshold.py --data data --scores out/scores.csv --out out --threshold 0.50 --max 0.70 --clear
```

## Note on custom folder names

Folder names can be changed. Example:

```bash
python score.py --data input --out results
python export_threshold.py --data input --scores results/scores.csv --out results --threshold 0.52 --clear
```
