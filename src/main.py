"""Main Reddit Image Scraper application."""

import os

from src.config import (
    IMAGES_FOLDER,
    POST_SEARCH_AMOUNT,
    SAFETY_LIMIT,
    SUB_LIST_FILE,
    SUBREDDIT_LIMIT,
    SUPPORTED_MEDIA_FORMATS,
    TOKEN_FILE,
)
from src.utils.file_operations import create_folder, get_project_root_path
from src.utils.reddit_auth import authenticate_reddit
from src.utils.subreddit_processor import load_subreddit_list, process_subreddit


def main() -> None:
    """Main function to run the Reddit image scraper."""
    # Use utility function to get project root path
    dir_path = get_project_root_path()
    image_path = os.path.join(dir_path, f"{IMAGES_FOLDER}/")
    create_folder(image_path)

    # Authenticate with Reddit
    reddit, creds = authenticate_reddit(dir_path, TOKEN_FILE)

    # Load and process subreddits
    sub_list_path = os.path.join(dir_path, SUB_LIST_FILE)
    subreddit_list = load_subreddit_list(sub_list_path)

    for sub in subreddit_list:
        process_subreddit(
            reddit=reddit,
            creds=creds,
            sub=sub,
            media_path=image_path,
            post_search_amount=POST_SEARCH_AMOUNT,
            subreddit_limit=SUBREDDIT_LIMIT,
            safety_limit=SAFETY_LIMIT,
            supported_media_formats=SUPPORTED_MEDIA_FORMATS,
        )


if __name__ == "__main__":
    main()
