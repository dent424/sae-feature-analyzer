"""Download files from Google Drive directly to Modal volume.

This script runs a Modal function that downloads files from Google Drive
directly to your Modal volume, avoiding the need to download locally first.

Usage:
    python gdrive_to_modal.py <file_id> <filename>

Example:
    # Get the file ID from the Google Drive share link:
    # https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing
    #                              ^^^^^^^^^^^
    #                              This is the file ID

    python gdrive_to_modal.py 1ABC123xyz mexican_national_sae_features_e32_k32_lr0_0003-final.h5
"""

import modal
import argparse

app = modal.App("gdrive-uploader")

# Image with gdown for Google Drive downloads
image = modal.Image.debian_slim(python_version="3.10").pip_install("gdown")

# Reference the sae-data volume
volume = modal.Volume.from_name("sae-data", create_if_missing=True)


@app.function(
    image=image,
    volumes={"/data": volume},
    timeout=3600,  # 1 hour timeout for large files
)
def download_from_gdrive(file_id: str, filename: str) -> str:
    """Download a file from Google Drive directly to the Modal volume."""
    import gdown
    import os

    output_path = f"/data/{filename}"
    url = f"https://drive.google.com/uc?id={file_id}"

    print(f"Downloading from Google Drive...")
    print(f"  File ID: {file_id}")
    print(f"  Output: {output_path}")

    # Download using gdown
    gdown.download(url, output_path, quiet=False)

    # Verify the file exists and get size
    if os.path.exists(output_path):
        size_bytes = os.path.getsize(output_path)
        size_gb = size_bytes / (1024 ** 3)
        print(f"\nDownload complete!")
        print(f"  File size: {size_gb:.2f} GB ({size_bytes:,} bytes)")

        # Commit the volume to persist changes
        volume.commit()
        print("  Volume committed successfully.")
        return f"Success: {filename} ({size_gb:.2f} GB)"
    else:
        return f"Error: File was not created at {output_path}"


@app.function(image=image, volumes={"/data": volume})
def list_volume_contents() -> list[str]:
    """List all files in the sae-data volume."""
    import os

    files = []
    for f in os.listdir("/data"):
        path = f"/data/{f}"
        size = os.path.getsize(path)
        size_mb = size / (1024 ** 2)
        files.append(f"{f} ({size_mb:.1f} MB)")
    return files


@app.local_entrypoint()
def main(file_id: str = None, filename: str = None, list_files: bool = False):
    """Download a file from Google Drive to the Modal volume.

    Args:
        file_id: Google Drive file ID (from the share link)
        filename: Name to save the file as in the volume
        list_files: If True, list current volume contents instead
    """
    if list_files:
        print("Files in sae-data volume:")
        files = list_volume_contents.remote()
        for f in files:
            print(f"  {f}")
        return

    if not file_id or not filename:
        print("Usage: python gdrive_to_modal.py <file_id> <filename>")
        print("       python gdrive_to_modal.py --list-files")
        print()
        print("Example:")
        print("  python gdrive_to_modal.py 1ABC123xyz myfile.h5")
        print()
        print("To get the file ID from a Google Drive link:")
        print("  https://drive.google.com/file/d/1ABC123xyz/view")
        print("                              ^^^^^^^^^^^")
        print("                              This is the file ID")
        return

    result = download_from_gdrive.remote(file_id, filename)
    print(result)


if __name__ == "__main__":
    # Parse command line arguments for direct python execution
    parser = argparse.ArgumentParser(
        description="Download files from Google Drive to Modal volume"
    )
    parser.add_argument("file_id", nargs="?", help="Google Drive file ID")
    parser.add_argument("filename", nargs="?", help="Output filename in volume")
    parser.add_argument("--list-files", action="store_true", help="List volume contents")

    args = parser.parse_args()

    # Run via modal
    import subprocess
    import sys

    cmd = [sys.executable, "-m", "modal", "run", "gdrive_to_modal.py"]

    if args.list_files:
        cmd.extend(["--list-files"])
    elif args.file_id and args.filename:
        cmd.extend(["--file-id", args.file_id, "--filename", args.filename])
    else:
        cmd.extend(["--help"])

    subprocess.run(cmd)
