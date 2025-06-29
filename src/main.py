"""Main Reddit Image Scraper application."""

import praw
import praw.models
import requests
import os
import pickle
from typing import Dict, Tuple, Optional
from bs4 import BeautifulSoup, Tag

from src.utils.reddit_auth import create_token
from src.utils.file_operations import create_folder, get_file_extension
from src.config import (
    POST_SEARCH_AMOUNT,
    TOKEN_FILE,
    SUB_LIST_FILE,
    IMAGES_FOLDER,
    SUBREDDIT_LIMIT,
    SAFETY_LIMIT,
    SUPPORTED_MEDIA_FORMATS,
)


def authenticate_reddit(dir_path: str) -> Tuple[praw.Reddit, Dict[str, str]]:
    """Authenticate with Reddit API.

    Args:
        dir_path: Project root directory path

    Returns:
        Tuple of authenticated Reddit instance and credentials
    """
    # Get token file to log into reddit
    token_path = os.path.join(dir_path, TOKEN_FILE)
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    else:
        creds = create_token()
        with open(token_path, "wb") as pickle_out:
            pickle.dump(creds, pickle_out)

    try:
        print("Connecting to Reddit…")

        # Validate credentials before using them
        if not creds or not all(
            creds.get(key)
            for key in [
                "client_id",
                "client_secret",
                "user_agent",
                "username",
                "password",
            ]
        ):
            print("Error: Missing or invalid Reddit credentials")
            print(
                "Please check your .env file and ensure all Reddit credentials are set."
            )
            print(
                "If you don't have a .env file, copy .env.example to .env and fill in your credentials."
            )
            exit(1)

        reddit = praw.Reddit(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            user_agent=creds["user_agent"],
            username=creds["username"],
            password=creds["password"],
        )

        # Test the connection
        reddit.user.me()
        print("✅  Authentication successful!")
        return reddit, creds

    except Exception as e:
        print(f"Authentication failed: {e}")
        print("Please check your Reddit credentials:")
        print("1. Make sure your username and password are correct")
        print("2. Verify your Client ID and Client Secret from:")
        print("   https://www.reddit.com/prefs/apps")
        print("3. If you have 2FA enabled, you may need to use an app password")
        print("4. Make sure your Reddit app type is set to 'script'")
        exit(1)


def _parse_html_for_media(
    url: str, headers: Dict[str, str]
) -> Tuple[Optional[str], Optional[str]]:
    """Parse HTML page for og:video or og:image meta tags.

    Args:
        url: URL to parse
        headers: Request headers

    Returns:
        Tuple of (media_url, file_extension) or (None, None) if not found
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


def _get_accept_header(file_extension: str, media_url: str) -> str:
    """Get appropriate Accept header based on file extension and URL.

    Args:
        file_extension: File extension
        media_url: Media URL

    Returns:
        Accept header value
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


def _save_media_file(
    content: bytes, media_path: str, sub: str, submission_id: str, file_extension: str
) -> bool:
    """Save media content to file.

    Args:
        content: Media content
        media_path: Base path for media files
        sub: Subreddit name
        submission_id: Submission ID
        file_extension: File extension

    Returns:
        True if saved successfully, False otherwise
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
) -> bool:
    """Download a single media item from a Reddit submission.
    If not a direct media link, attempts to parse HTML for og:video or og:image tags.

    Args:
        submission: Reddit submission object
        creds: Reddit API credentials
        media_path: Path to save media
        sub: Subreddit name
        is_direct_media: True if the URL is identified as a direct media link.

    Returns:
        True if media was downloaded successfully, False otherwise
    """
    original_url: str = submission.url
    media_url_to_download: str = original_url
    file_extension: Optional[str] = None

    headers: Dict[str, str] = {"User-Agent": creds["user_agent"]}

    # Handle non-direct media URLs by parsing HTML
    if not is_direct_media:
        result = _parse_html_for_media(original_url, headers)
        if result == (None, None):
            return False
        parsed_url, parsed_extension = result
        if parsed_url is not None:
            media_url_to_download = parsed_url
            file_extension = parsed_extension

    # Determine file extension if not already set
    if not file_extension:
        file_extension = get_file_extension(media_url_to_download)

    # Set appropriate Accept header
    headers["Accept"] = _get_accept_header(file_extension, media_url_to_download)

    # Download the media content
    try:
        response = requests.get(media_url_to_download, headers=headers, timeout=30)
        response.raise_for_status()

        return _save_media_file(
            response.content, media_path, sub, submission.id, file_extension
        )

    except (requests.exceptions.RequestException, Exception):
        return False


def process_subreddit(
    reddit: praw.Reddit, creds: Dict[str, str], sub: str, media_path: str
) -> None:
    """Process a single subreddit and download media.

    Args:
        reddit: Authenticated Reddit instance
        creds: Reddit API credentials
        sub: Subreddit name
        media_path: Path to save media
    """
    subreddit = reddit.subreddit(sub)
    print(f"\nDownloading media from r/{sub}...")
    count = 0
    posts_checked = 0

    # Keep searching until we find POST_SEARCH_AMOUNT media items
    for submission in subreddit.new(limit=SUBREDDIT_LIMIT):
        posts_checked += 1

        # Break if we've found enough media items
        if count >= POST_SEARCH_AMOUNT:
            break

        # Skip if we've checked too many posts (safety limit)
        if posts_checked > SAFETY_LIMIT:
            print(f"  Reached safety limit of {SAFETY_LIMIT} posts checked")
            break

        url_lower = submission.url.lower()
        is_direct_media = any(f".{fmt}" in url_lower for fmt in SUPPORTED_MEDIA_FORMATS)

        # Try to download media (direct or parse HTML for indirect)
        if download_media(submission, creds, media_path, sub, is_direct_media):
            filename = f"{sub}-{submission.id}.{get_file_extension(submission.url)}"
            print(
                f"  [{count + 1}/{POST_SEARCH_AMOUNT}] {submission.url} -> data/downloads/{filename}"
            )
            count += 1

    print(f"✔️  Complete: saved {count} media items (scanned {posts_checked} posts)")


def main() -> None:
    """Main function to run the Reddit image scraper."""
    # Path to save images
    dir_path = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))
    )  # Go up to project root
    image_path = os.path.join(dir_path, f"{IMAGES_FOLDER}/")
    create_folder(image_path)

    # Authenticate with Reddit
    reddit, creds = authenticate_reddit(dir_path)

    # Process subreddits
    sub_list_path = os.path.join(dir_path, SUB_LIST_FILE)
    with open(sub_list_path, "r") as f_final:
        for line in f_final:
            sub = line.strip()
            if not sub:  # Skip empty lines
                continue
            process_subreddit(reddit, creds, sub, image_path)


if __name__ == "__main__":
    main()
