"""Main Reddit Image Scraper application."""

import praw
import requests
import os
import pickle

from src.utils.reddit_auth import create_token
from src.utils.file_operations import create_folder, get_file_extension
from src.config import (
    POST_SEARCH_AMOUNT,
    TOKEN_FILE,
    SUB_LIST_FILE,
    IMAGES_FOLDER,
    SUBREDDIT_LIMIT,
    SAFETY_LIMIT,
    SUPPORTED_IMAGE_FORMATS,
)


def authenticate_reddit(dir_path):
    """Authenticate with Reddit API.

    Args:
        dir_path (str): Project root directory path

    Returns:
        praw.Reddit: Authenticated Reddit instance
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


def download_image(submission, creds, image_path, sub):
    """Download a single image from a Reddit submission.

    Args:
        submission: Reddit submission object
        creds (dict): Reddit API credentials
        image_path (str): Path to save images
        sub (str): Subreddit name

    Returns:
        bool: True if image was downloaded successfully, False otherwise
    """
    try:
        # Use proper headers for downloading Reddit images
        headers = {"User-Agent": creds["user_agent"], "Accept": "image/*"}

        # Download image with proper error handling
        response = requests.get(submission.url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        if response.content and len(response.content) > 0:
            # Determine file extension from URL
            file_extension = get_file_extension(submission.url)

            # Save the raw image data directly without processing
            filename = f"{image_path}{sub}-{submission.id}.{file_extension}"

            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"data/downloads/{submission.id}.{file_extension}")
            return True
        else:
            print(f"  Empty response content: {submission.url}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"  Network error downloading {submission.url}: {e}")
        return False
    except Exception as e:
        print(f"  Unexpected error with {submission.url}: {e}")
        return False


def process_subreddit(reddit, creds, sub, image_path):
    """Process a single subreddit and download images.

    Args:
        reddit: Authenticated Reddit instance
        creds (dict): Reddit API credentials
        sub (str): Subreddit name
        image_path (str): Path to save images
    """
    subreddit = reddit.subreddit(sub)
    print(f"\nDownloading images from r/{sub}...")
    count = 0
    posts_checked = 0

    # Keep searching until we find POST_SEARCH_AMOUNT images
    for submission in subreddit.new(limit=SUBREDDIT_LIMIT):
        posts_checked += 1

        # Break if we've found enough images
        if count >= POST_SEARCH_AMOUNT:
            break

        # Skip if we've checked too many posts (safety limit)
        if posts_checked > SAFETY_LIMIT:
            print(f"  Reached safety limit of {SAFETY_LIMIT} posts checked")
            break

        # Check if URL contains supported image formats
        url_lower = submission.url.lower()
        if any(fmt in url_lower for fmt in SUPPORTED_IMAGE_FORMATS):
            print(f"  [{count + 1}/{POST_SEARCH_AMOUNT}] {submission.url}", end=" -> ")

            if download_image(submission, creds, image_path, sub):
                count += 1

    print(f"✔️  Complete: saved {count} images (scanned {posts_checked} posts)")


def main():
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
