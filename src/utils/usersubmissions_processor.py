"""Processor for downloading media from a Reddit user's submissions."""

from typing import Dict, Optional, List, Tuple
import praw
from .media_download import download_media

import traceback

def process_user_submissions(
    reddit: praw.Reddit,
    username: str,
    creds: Dict[str, str],
    media_path: str,
    supported_media_formats: list,
    limit: int = 100
) -> List[Tuple[str, Optional[str]]]:
    """
    Download media from a Reddit user's submissions.

    Args:
        reddit: Authenticated PRAW Reddit instance
        username: Reddit username to process
        creds: Reddit API credentials (must include 'user_agent')
        media_path: Path to save media files
        supported_media_formats: List of allowed file extensions
        limit: Max number of submissions to process

    Returns:
        List of tuples (submission_id, file_extension) for successful downloads
    """
    print(f"\n[UserSubmissions] Starting processing for user: {username}")
    results = []
    try:
        redditor = reddit.redditor(username)
        print(f"[UserSubmissions] Got Redditor object for: {username}")
        submissions = redditor.submissions.new(limit=limit)
        for i, submission in enumerate(submissions, 1):
            print(f"[UserSubmissions] Processing submission {i}: {submission.id} - {submission.title}")
            url_lower = submission.url.lower()
            is_direct_media = any(f".{fmt}" in url_lower for fmt in supported_media_formats) if supported_media_formats else True
            try:
                success, ext = download_media(
                    submission,
                    creds,
                    media_path,
                    username,  # Use username as the 'sub' folder
                    is_direct_media,
                    supported_media_formats,
                )
                if success:
                    print(f"[UserSubmissions] Downloaded media for submission {submission.id} ({ext})")
                    results.append((submission.id, ext))
                else:
                    print(f"[UserSubmissions] No media downloaded for submission {submission.id}")
            except Exception as e:
                print(f"[UserSubmissions] Error processing submission {submission.id}: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"[UserSubmissions] Error processing user '{username}': {e}")
        traceback.print_exc()
    print(f"[UserSubmissions] Finished processing user: {username}")
    return results

"""Utility to load a list of Reddit usernames from a CSV file."""

def load_user_list(csv_path: str) -> list:
    """
    Load a list of Reddit usernames from a CSV file (one username per line).

    Args:
        csv_path: Path to the CSV file
    Returns:
        List of usernames as strings
    """
    user_list = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            for line in f:
                username = line.strip().split(",")[0]  # Only take the first column if CSV
                if username and not username.startswith("#"):  # Allow comments and skip blank lines
                    user_list.append(username)
    except Exception as e:
        print(f"[load_user_list] Error loading user list: {e}")
    return user_list
