"""Batch analyze multiple SAE features.

Usage:
    python batch_analyze.py 16751 20379 11328
    python batch_analyze.py features.txt
    python batch_analyze.py 16751-16760  # Range syntax

Examples:
    # Analyze specific features
    python batch_analyze.py 16751 20379 11328

    # Analyze a range of features
    python batch_analyze.py 16000-16010

    # Analyze features from a file (one per line)
    python batch_analyze.py my_features.txt

    # Force re-analysis of existing files
    python batch_analyze.py 16751 --force

    # Custom output directory
    python batch_analyze.py 16751 --output-dir results/
"""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_feature_args(args: list[str]) -> list[int]:
    """Parse feature indices from various formats.

    Supports:
    - Individual numbers: 16751
    - Ranges: 16751-16760
    - Files with one feature per line: features.txt
    """
    features = []
    for arg in args:
        # Check if it's a range (contains hyphen but doesn't start with hyphen)
        if '-' in arg and not arg.startswith('-'):
            try:
                start, end = map(int, arg.split('-'))
                features.extend(range(start, end + 1))
            except ValueError:
                # Not a valid range, might be a file
                pass

        # Check if it's a file
        path = Path(arg)
        if path.exists() and path.is_file():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and line.isdigit():
                        features.append(int(line))
        else:
            # Try to parse as integer
            try:
                features.append(int(arg))
            except ValueError:
                print(f"Warning: Could not parse '{arg}' as feature index, file, or range")

    return features


def main():
    parser = argparse.ArgumentParser(
        description='Batch analyze SAE features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'features',
        nargs='+',
        help='Feature indices, ranges (e.g., 100-200), or file paths'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory (default: output/)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-analyze even if output file exists'
    )
    args = parser.parse_args()

    # Parse all feature arguments
    features = parse_feature_args(args.features)

    if not features:
        print("Error: No valid feature indices found")
        sys.exit(1)

    # Remove duplicates while preserving order
    seen = set()
    features = [f for f in features if not (f in seen or seen.add(f))]

    print(f"Analyzing {len(features)} feature(s)...")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Process each feature
    success_count = 0
    skip_count = 0
    fail_count = 0

    for i, feature_idx in enumerate(features):
        output_file = output_dir / f'feature_{feature_idx}.json'

        # Skip if exists (unless --force)
        if output_file.exists() and not args.force:
            print(f"[{i+1}/{len(features)}] Skipping feature {feature_idx} (output exists)")
            skip_count += 1
            continue

        print(f"[{i+1}/{len(features)}] Analyzing feature {feature_idx}...")

        result = subprocess.run(
            [
                sys.executable, '-m', 'modal', 'run',
                'modal_interpreter.py::analyze_feature_json',
                '--feature-idx', str(feature_idx),
                '--output-dir', str(output_dir)
            ],
            capture_output=False
        )

        if result.returncode == 0:
            success_count += 1
        else:
            print(f"  Warning: Feature {feature_idx} analysis may have failed")
            fail_count += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"Done! Results in {output_dir}/")
    print(f"  Analyzed: {success_count}")
    print(f"  Skipped:  {skip_count}")
    if fail_count > 0:
        print(f"  Failed:   {fail_count}")


if __name__ == '__main__':
    main()
