"""Media parsing utilities for extracting media URLs from HTML content."""

from typing import Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag


def parse_html_for_media(
    url: str, headers: Dict[str, str]
) -> Tuple[Optional[str], Optional[str]]:
    """Parse HTML page for og:video or og:image meta tags.

    Args:
        url: URL to parse
        headers: Request headers

    Returns:
        Tuple of (media_url, file_extension) or (None, None) if not found

    Example:
        >>> headers = {"User-Agent": "my-app/1.0"}
        >>> url, ext = parse_html_for_media("https://example.com/post", headers)
        >>> if url:
        ...     print(f"Found media: {url} with extension: {ext}")
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        og_video_tag = soup.find("meta", property="og:video")
        og_image_tag = soup.find("meta", property="og:image")

        if og_video_tag and isinstance(og_video_tag, Tag):
            try:
                content = og_video_tag.get("content")
                if content:
                    return str(content), "mp4"
            except (AttributeError, TypeError):
                pass

        if og_image_tag and isinstance(og_image_tag, Tag):
            try:
                content = og_image_tag.get("content")
                if content:
                    return str(content), None
            except (AttributeError, TypeError):
                pass

        return None, None
    except (requests.exceptions.RequestException, Exception):
        return None, None


def get_accept_header(file_extension: str, media_url: str) -> str:
    """Get appropriate Accept header based on file extension and URL.

    Args:
        file_extension: File extension (e.g., 'mp4', 'jpg', 'gif')
        media_url: Media URL to analyze

    Returns:
        Accept header value for HTTP requests

    Example:
        >>> get_accept_header("mp4", "https://example.com/video.mp4")
        'video/*, */*'
        >>> get_accept_header("jpg", "https://example.com/image.jpg")
        'image/*'
    """
    media_url_lower = media_url.lower()

    if (
        file_extension == "mp4"
        or ".mp4" in media_url_lower
        or file_extension == "webm"
        or ".webm" in media_url_lower
    ):
        return "video/*, */*"
    elif file_extension == "gif" or ".gif" in media_url_lower:
        return "image/gif, image/*"
    else:
        return "image/*"
