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
    url_lower = url.lower()
    if ".jpg" in url_lower or ".jpeg" in url_lower:
        return "jpg"
    elif ".png" in url_lower:
        return "png"
    else:
        # Default to jpg if we can't determine
        return "jpg"
