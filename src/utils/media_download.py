"""Media download utilities for handling Reddit media downloads."""

from typing import Dict, Optional, Tuple

import praw.models
import requests

from .file_operations import get_file_extension
from .media_parsing import get_accept_header, parse_html_for_media


def save_media_file(
    content: Optional[bytes],
    media_path: str,
    sub: str,
    submission_id: str,
    file_extension: str,
) -> bool:
    """Save media content to file.

    Args:
        content: Media content bytes
        media_path: Base path for media files
        sub: Subreddit name
        submission_id: Reddit submission ID
        file_extension: File extension (e.g., 'jpg', 'mp4')

    Returns:
        True if saved successfully, False otherwise

    Example:
        >>> content = b"fake_image_data"
        >>> success = save_media_file(content, "/downloads/", "pics", "abc123", "jpg")
        >>> if success:
        ...     print("File saved successfully")
    """
    if not content or len(content) == 0:
        return False

    try:
        filename = f"{media_path}{sub}-{submission_id}.{file_extension}"
        with open(filename, "wb") as f:
            f.write(content)
        return True
    except Exception:
        return False


def download_media(
    submission: praw.models.Submission,
    creds: Dict[str, str],
    media_path: str,
    sub: str,
    is_direct_media: bool,
    supported_media_formats: Optional[list] = None,
) -> Tuple[bool, Optional[str]]:
    """Download a single media item from a Reddit submission.

    If not a direct media link, attempts to parse HTML for og:video or og:image tags.

    Args:
        submission: Reddit submission object
        creds: Reddit API credentials containing user_agent
        media_path: Path to save media files
        sub: Subreddit name
        is_direct_media: True if the URL is identified as a direct media link
        supported_media_formats: List of supported file extensions to filter by

    Returns:
        Tuple of (success, file_extension) where success is True if media was downloaded successfully,
        and file_extension is the actual extension used for saving

    Example:
        >>> # Mock submission object would be used in practice
        >>> creds = {"user_agent": "my-app/1.0"}
        >>> success, ext = download_media(submission, creds, "/downloads/", "pics", True)
        >>> if success:
        ...     print(f"Media downloaded successfully with extension: {ext}")
    """
    original_url: str = submission.url
    media_url_to_download: str = original_url
    file_extension: Optional[str] = None

    headers: Dict[str, str] = {"User-Agent": creds["user_agent"]}

    # Handle non-direct media URLs by parsing HTML
    if not is_direct_media:
        result = parse_html_for_media(original_url, headers)
        if result == (None, None):
            return False, None
        parsed_url, parsed_extension = result
        if parsed_url is not None:
            media_url_to_download = parsed_url
            file_extension = parsed_extension

    # Determine file extension if not already set
    if not file_extension:
        file_extension = get_file_extension(media_url_to_download)

    # Check if the file extension is supported (if supported_media_formats is provided)
    if supported_media_formats and file_extension not in supported_media_formats:
        return False, None

    # Set appropriate Accept header
    headers["Accept"] = get_accept_header(file_extension, media_url_to_download)

    # Download the media content
    try:
        response = requests.get(media_url_to_download, headers=headers, timeout=30)
        response.raise_for_status()

        success = save_media_file(
            response.content, media_path, sub, submission.id, file_extension
        )
        return success, file_extension if success else None

    except (requests.exceptions.RequestException, Exception):
        return False, None
