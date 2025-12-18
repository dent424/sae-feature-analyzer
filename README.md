# SAE Feature Analyzer

Analyze Sparse Autoencoder (SAE) features extracted from GPT-2 activations on 432K Mexican restaurant Yelp reviews.

This tool generates comprehensive JSON reports for each SAE feature, including:
- Activation statistics (rate, mean, max)
- Top tokens where the feature fires
- Strongest activation examples with context
- Co-activation patterns (features that fire together)
- Position distribution (where in reviews the feature fires)
- Activation distribution (percentiles, skewness, kurtosis)
- Example contexts for top tokens

---

## Before You Start

### What You Need to Know

**Python** is a programming language. You don't need to write any Python code - you'll just run commands that use Python scripts we've already written.

**Terminal** (also called "Command Prompt" on Windows) is where you type commands. It's a text-based way to tell your computer what to do.

**Modal** is a cloud computing service. Instead of running computations on your computer, Modal runs them on powerful servers with GPUs. This is free for small usage.

### Opening a Terminal

- **Windows**: Press the Windows key, type `cmd`, and press Enter. Or search for "Command Prompt" or "PowerShell".
- **Mac**: Press Cmd+Space, type `Terminal`, and press Enter.
- **Linux**: Press Ctrl+Alt+T, or search for "Terminal" in your applications.

### Check if Python is Installed

In your terminal, type:
```
python --version
```

**What you should see:** Something like `Python 3.10.12` or `Python 3.11.4`

**If you see an error** like "python not found":
- **Windows**: Try `py --version` instead. Windows often uses `py` instead of `python`.
- **If still not found**: Install Python from https://www.python.org/downloads/ (choose version 3.10 or 3.11)

---

## Quick Start

### Step 1: Open a terminal and navigate to this folder

First, you need to "navigate" to the folder containing these files. This means telling the terminal which folder to work in.

```
cd path/to/sae-feature-analyzer
```

**What `cd` means:** "change directory" - it moves you into a folder.

**How to find the path:**
- **Windows**: Open the folder in File Explorer, click in the address bar, and copy the path. It looks like `C:\Users\YourName\Downloads\sae-feature-analyzer`
- **Mac**: Open the folder in Finder, right-click the folder, hold Option, and click "Copy as Pathname"

**Example (Windows):**
```
cd C:\Users\YourName\Downloads\sae-feature-analyzer
```

**Example (Mac/Linux):**
```
cd /Users/YourName/Downloads/sae-feature-analyzer
```

### Step 2: Install the required packages

```
pip install -r requirements.txt
```

**What this does:** `pip` is Python's package manager. This command downloads and installs all the software libraries needed to run the analyzer. It may take a few minutes.

**What you should see:** Lots of text scrolling by, ending with "Successfully installed..."

**If you get "pip not found":** Try `python -m pip install -r requirements.txt` instead.

### Step 3: Set up Modal

```
modal setup
```

**What this does:** Connects your computer to Modal's cloud servers. A browser window will open where you can create a free account or log in.

**What you should see:** A message saying "Web authentication finished successfully!" or similar.

**If you get "modal not found":** Try `python -m modal setup` instead.

### Step 4: Upload the data files

Follow the instructions in [DATA_SETUP.md](DATA_SETUP.md) to upload the required data files to Modal's servers.

This is a one-time setup. For the large 9GB file, use `gdrive_to_modal.py` to transfer directly from Google Drive.

### Step 5: Test that everything works

```
python -m modal run modal_interpreter.py::test_interpreter
```

**What this does:** Runs a quick test to verify all the data files are accessible and the code works.

**What you should see:** Several test messages, ending with `=== All tests passed! ===`

**Don't worry about:** Yellow or red warning text during the test - this is normal. Just look for "All tests passed" at the end.

### Step 6: Analyze some features!

```
python batch_analyze.py 16751
```

**What this does:** Analyzes SAE feature #16751 and saves the results.

**What you should see:** Progress messages, then "Done! Results in output/"

**Where to find results:** Look in the `output` folder for `feature_16751.json`

---

## Usage Examples

### Analyze a single feature

```
python batch_analyze.py 16751
```

Results are saved to `output/feature_16751.json`

### Analyze multiple features

```
python batch_analyze.py 16751 20379 11328
```

This analyzes three features. Results: `feature_16751.json`, `feature_20379.json`, `feature_11328.json`

### Analyze a range of features

```
python batch_analyze.py 16000-16010
```

This analyzes features 16000, 16001, 16002, ... 16010 (11 features total).

### Analyze features from a file

If you have a list of feature numbers in a text file (one per line):

```
python batch_analyze.py features.txt
```

**How to create the file:**

1. Open Notepad (Windows) or TextEdit (Mac)
2. Type one feature number per line:
   ```
   16751
   20379
   11328
   ```
3. Save as `features.txt` in this folder

### Understanding the command

```
python batch_analyze.py 16751
```

Breaking this down:
- `python` - Run the Python interpreter
- `batch_analyze.py` - The script file to run
- `16751` - The feature number to analyze (you can list multiple)

### Additional options

**Re-analyze a feature** (even if output already exists):
```
python batch_analyze.py 16751 --force
```

**Save to a different folder:**
```
python batch_analyze.py 16751 --output-dir my_results/
```

---

## Output Format

Each feature produces a JSON file (`output/feature_{number}.json`). JSON is a text format that organizes data - you can open it in any text editor.

The file contains:

```json
{
  "feature_idx": 16751,
  "stats": {
    "total_activations": 7761,
    "mean_when_active": 0.0476,
    "max_activation": 0.2297,
    "activation_rate": 0.0776
  },
  "top_tokens": {
    "tokens": [
      {"token": " the", "count": 1844, "mean_activation": 0.043},
      {"token": " my", "count": 1528, "mean_activation": 0.045}
    ]
  },
  "top_activations": {
    "activations": [
      {
        "context": "I have never in **my** life...",
        "active_token": " my",
        "activation": 0.2233
      }
    ]
  },
  "coactivation": {
    "coactivated_features": [
      {"feature_idx": 1234, "count": 500, "percent": 25.0}
    ]
  },
  "position_distribution": {
    "bins": [
      {"label": "early", "count": 150, "percent": 15.0}
    ],
    "mean_position": 0.42
  },
  "activation_distribution": {
    "percentiles": {"p50": 0.025, "p90": 0.08, "p99": 0.15},
    "skewness": 2.1,
    "kurtosis": 8.5
  },
  "top_token_contexts": {
    "tokens": [
      {
        "token": " my",
        "count": 1528,
        "contexts": [
          {"context": "...**my**...", "feature_activations": [0, 0.22, 0]}
        ]
      }
    ]
  }
}
```

---

## Common Issues

### "python not found" or "python is not recognized"

- **Windows**: Try using `py` instead of `python`:
  ```
  py batch_analyze.py 16751
  ```
- **Still not working**: Install Python from https://www.python.org/downloads/

### "modal not found" or "modal is not recognized"

Use `python -m modal` instead of just `modal`:
```
python -m modal setup
python -m modal run modal_interpreter.py::test_interpreter
```

### "pip not found"

Try:
```
python -m pip install -r requirements.txt
```

### Red or yellow text during tests

This is usually fine! Modal and Python often print warnings in color. Look for the final message - if it says "All tests passed!" you're good.

### "Volume not found" or "File not found"

You need to upload the data files first. See [DATA_SETUP.md](DATA_SETUP.md).

### Tests fail repeatedly

1. Check that all data files are uploaded (see DATA_SETUP.md)
2. Try running the test again - Modal sometimes has delays on first run
3. Make sure filenames match exactly (they're case-sensitive)

### Analysis is slow

The first run is always slower because Modal needs to start up its servers. Subsequent runs are faster.

---

## Known Interesting Features

| Feature | Description |
|---------|-------------|
| 16751 | Emphatic expressions ("never in my life") |
| 20379 | Lexical patterns (gum/gumbo) |
| 11328 | Formatted lists (bullets, numbered) |

---

## License

MIT
