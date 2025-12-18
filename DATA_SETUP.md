# Data Setup for SAE Feature Analyzer

This guide explains how to upload the required data files to Modal.

## What is a Modal Volume?

A **volume** is cloud storage space on Modal's servers. Think of it like a folder in the cloud where your data files live. When Modal runs your analysis, it reads the data from this volume instead of from your computer.

**Why do we need this?** The analysis runs on Modal's servers (not your computer), so the data files need to be on Modal's servers too.

---

## Required Files

You need these four files uploaded to a Modal volume named `sae-data`:

| File | Size | Description |
|------|------|-------------|
| `sae_e32_k32_lr0.0003-final.pt` | ~604 MB | SAE model (the neural network weights) |
| `mexican_national_metadata.npz` | ~220 MB | Review texts and ratings |
| `mexican_national_sae_features_e32_k32_lr0_0003-final.h5` | ~9 GB | Precomputed feature activations |
| `review_token_positions.pkl` | ~258 MB | Token position mapping (optional*) |

*The last file is auto-generated on first run if missing, but having it saves 30-60 seconds.

**Total size: ~10 GB**

---

## Setup Steps

### Step 1: Create the Modal volume

Open your terminal (see README.md if you don't know how) and run:

```
modal volume create sae-data
```

**What this does:** Creates an empty storage space on Modal's servers named "sae-data".

**What you should see:**
```
Created volume 'sae-data' in environment 'main'.
```

**If you get "modal not found":** Try `python -m modal volume create sae-data` instead.

---

### Step 2: Upload the smaller files

First, navigate to the folder containing your data files. If the files are in your Downloads folder:

**Windows:**
```
cd C:\Users\YourName\Downloads
```

**Mac/Linux:**
```
cd ~/Downloads
```

Now upload the three smaller files (these usually work fine with direct upload):

```
modal volume put sae-data sae_e32_k32_lr0.0003-final.pt sae_e32_k32_lr0.0003-final.pt
```

**What this command means:**
- `modal volume put` - Upload a file to a volume
- `sae-data` - The volume name (where to upload)
- First filename - The file on your computer
- Second filename - What to name it on Modal (same name)

**What you should see:** A progress bar, then a success message.

Repeat for the other small files:

```
modal volume put sae-data mexican_national_metadata.npz mexican_national_metadata.npz
```

```
modal volume put sae-data review_token_positions.pkl review_token_positions.pkl
```

---

### Step 3: Upload the large H5 file (from Google Drive)

The 9GB file often fails with direct upload. Instead, use our helper script to transfer it directly from Google Drive to Modal (your computer doesn't need to download it first).

#### 3a. Get the Google Drive file ID

1. Go to Google Drive and find the H5 file
2. Right-click the file and select **"Share"** (or "Get link")
3. Make sure it's set to **"Anyone with the link can view"**
4. Copy the link. It looks like this:
   ```
   https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/view?usp=sharing
   ```
5. The **file ID** is the long string between `/d/` and `/view`:
   ```
   1AbCdEfGhIjKlMnOpQrStUvWxYz
   ```

#### 3b. Run the upload helper

Navigate back to the sae-feature-analyzer folder, then run:

```
python -m modal run gdrive_to_modal.py --file-id YOUR_FILE_ID --filename mexican_national_sae_features_e32_k32_lr0_0003-final.h5
```

Replace `YOUR_FILE_ID` with the actual file ID from step 3a.

**Example with a real file ID:**
```
python -m modal run gdrive_to_modal.py --file-id 1AbCdEfGhIjKlMnOpQrStUvWxYz --filename mexican_national_sae_features_e32_k32_lr0_0003-final.h5
```

**What this does:**
- Modal's servers download the file directly from Google Drive
- Saves it to your sae-data volume
- Your computer doesn't need to download the 9GB file!

**What you should see:** Download progress, then "Success" message with file size.

**This may take several minutes** - the file is large.

---

### Step 4: Verify everything uploaded

```
modal volume ls sae-data
```

Or use the helper script:

```
python -m modal run gdrive_to_modal.py --list-files
```

**What you should see:** All four files listed with their sizes:
```
sae_e32_k32_lr0.0003-final.pt (604.2 MB)
mexican_national_metadata.npz (220.1 MB)
mexican_national_sae_features_e32_k32_lr0_0003-final.h5 (8976.3 MB)
review_token_positions.pkl (258.4 MB)
```

---

### Step 5: Test the setup

Go back to the sae-feature-analyzer folder and run:

```
python -m modal run modal_interpreter.py::test_interpreter
```

**What you should see:** Several test messages, ending with `=== All tests passed! ===`

If this works, you're ready to analyze features!

---

## File Descriptions (Optional Reading)

### `sae_e32_k32_lr0.0003-final.pt`
PyTorch checkpoint containing the trained Sparse Autoencoder weights:
- Input dimension: 768 (GPT-2 hidden size)
- Expansion factor: 32
- Number of latents: 24,576
- Top-K sparsity: 32 active features per token

### `mexican_national_metadata.npz`
NumPy archive containing:
- `review_ids`: Unique identifiers for each review
- `texts`: Full review text
- `stars`: Star ratings (1-5)
- `useful`: Useful vote count
- `user_ids`: User identifiers
- `business_ids`: Business identifiers

### `mexican_national_sae_features_e32_k32_lr0_0003-final.h5`
HDF5 file with sparse activations for all 51.7M tokens:
- `z_idx[token]`: Array of 32 active feature indices per token
- `z_val[token]`: Array of 32 activation values per token
- `rev_idx[token]`: Review ID for each token position

### `review_token_positions.pkl`
Python pickle file mapping review IDs to their token positions in the H5 file.

---

## Troubleshooting

### "modal not found"

Use `python -m modal` instead:
```
python -m modal volume create sae-data
python -m modal volume put sae-data file.pt file.pt
```

### "Volume not found"

Make sure you created the volume first:
```
modal volume create sae-data
```

Check it exists:
```
modal volume list
```

### Upload times out or fails

For the large H5 file, use the Google Drive method in Step 3 above.

For smaller files, try again - network issues can cause temporary failures.

### "Permission denied" on Modal commands

Make sure you're logged in:
```
modal setup
```

### Google Drive download fails

Make sure the file sharing is set to "Anyone with the link can view". Private files won't work.

### File not found errors during analysis

Check all files are present:
```
modal volume ls sae-data
```

Filenames must match **exactly** (case-sensitive). The H5 filename in particular is long - make sure it's correct.

### Tests fail

1. Verify all four files are uploaded
2. Check filenames are exactly correct
3. Try the test again - Modal sometimes has startup delays
