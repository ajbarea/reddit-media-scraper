"""Subreddit processing utilities for handling Reddit media scraping."""

from typing import Dict, List

import praw

from .media_download import download_media


def process_subreddit(
    reddit: praw.Reddit,
    creds: Dict[str, str],
    sub: str,
    media_path: str,
    post_search_amount: int,
    subreddit_limit: int,
    safety_limit: int,
    supported_media_formats: list,
) -> None:
    """Process a single subreddit and download media.

    Args:
        reddit: Authenticated Reddit instance
        creds: Reddit API credentials
        sub: Subreddit name
        media_path: Path to save media
        post_search_amount: Number of media items to download
        subreddit_limit: Maximum posts to check per subreddit
        safety_limit: Safety limit to prevent infinite loops
        supported_media_formats: List of supported media file extensions
    """
    subreddit = reddit.subreddit(sub)
    print(f"\nDownloading media from r/{sub}...")
    count = 0
    posts_checked = 0

    # Keep searching until we find POST_SEARCH_AMOUNT media items
    for submission in subreddit.new(limit=subreddit_limit):
        posts_checked += 1

        # Break if we've found enough media items
        if count >= post_search_amount:
            break

        # Skip if we've checked too many posts (safety limit)
        if posts_checked > safety_limit:
            print(f"  Reached safety limit of {safety_limit} posts checked")
            break

        url_lower = submission.url.lower()
        is_direct_media = any(f".{fmt}" in url_lower for fmt in supported_media_formats)

        # Try to download media (direct or parse HTML for indirect)
        success, actual_extension = download_media(
            submission, creds, media_path, sub, is_direct_media, supported_media_formats
        )
        if success and actual_extension:
            filename = f"{sub}-{submission.id}.{actual_extension}"
            print(
                f"  [{count + 1}/{post_search_amount}] {submission.url} -> data/downloads/{filename}"
            )
            count += 1

    print(f"✔️  Complete: saved {count} media items (scanned {posts_checked} posts)")


def load_subreddit_list(sub_list_path: str) -> List[str]:
    """Load list of subreddits from CSV file.

    Args:
        sub_list_path: Path to the subreddit list file

    Returns:
        List of subreddit names (empty lines filtered out)
    """
    subreddits = []
    with open(sub_list_path, "r") as f:
        for line in f:
            sub = line.strip()
            if sub:  # Skip empty lines
                subreddits.append(sub)
    return subreddits
