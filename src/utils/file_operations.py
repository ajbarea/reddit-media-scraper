"""File and directory operation utilities."""

import os


def create_folder(path):
    """Create directory if it doesn't exist.

    Args:
        path (str): Directory path to create
    """
    os.makedirs(path, exist_ok=True)


def get_file_extension(url):
    """Determine file extension from URL.

    Args:
        url (str): URL to analyze

    Returns:
        str: File extension (jpg, png, or default jpg)
    """
    # Extract the part of the URL after the last slash
    filename_part = url.split("/")[-1]
    # Remove query parameters from the filename part before splitting by '.'
    filename_part = filename_part.split("?")[0]

    parts = filename_part.split(".")
    if len(parts) > 1:
        ext = parts[-1].lower()
        if ext == "jpeg":
            return "jpg"  # Standardize jpeg to jpg
        if ext in ["jpg", "png", "gif", "mp4", "webm"]:
            return ext

    # Default to jpg if no common extension is found or if there's no explicit extension.
    # The calling function (download_media) has more context if URL was from an <og:video> tag.
    return "jpg"
