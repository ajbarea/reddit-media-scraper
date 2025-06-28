"""Reddit authentication utilities."""

import os
from dotenv import load_dotenv


def create_token():
    """Load Reddit API credentials from environment variables.

    Returns:
        dict: Dictionary containing Reddit API credentials

    Raises:
        SystemExit: If any required credentials are missing
    """
    # Load environment variables from .env file
    load_dotenv()

    creds = {
        "client_id": os.getenv("REDDIT_CLIENT_ID"),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
        "user_agent": os.getenv("REDDIT_USER_AGENT"),
        "username": os.getenv("REDDIT_USERNAME"),
        "password": os.getenv("REDDIT_PASSWORD"),
    }

    # Check if all credentials are loaded
    missing_creds = [key for key, value in creds.items() if not value]
    if missing_creds:
        print(f"Missing credentials in .env file: {', '.join(missing_creds)}")
        print("Please check your .env file and ensure all Reddit credentials are set.")
        exit(1)

    return creds
