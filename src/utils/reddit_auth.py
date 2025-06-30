"""Reddit authentication utilities."""

import os
import pickle
from typing import Dict, List, Optional, Tuple

import praw
from dotenv import load_dotenv


def create_token() -> Dict[str, str]:
    """Load Reddit API credentials from environment variables.

    Returns:
        Dictionary containing Reddit API credentials

    Raises:
        ValueError: If any required credentials are missing
    """
    # Load environment variables from .env file
    load_dotenv()

    creds: Dict[str, Optional[str]] = {
        "client_id": os.getenv("REDDIT_CLIENT_ID"),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
        "user_agent": os.getenv("REDDIT_USER_AGENT"),
        "username": os.getenv("REDDIT_USERNAME"),
        "password": os.getenv("REDDIT_PASSWORD"),
    }

    # Check if all credentials are loaded
    missing_creds: List[str] = [key for key, value in creds.items() if not value]
    if missing_creds:
        error_msg = f"Missing credentials in .env file: {', '.join(missing_creds)}"
        print(error_msg)
        print("Please check your .env file and ensure all Reddit credentials are set.")
        raise ValueError(error_msg)

    # Convert to Dict[str, str] since we've verified all values are not None
    return {key: str(value) for key, value in creds.items()}


def authenticate_reddit(
    dir_path: str, token_file: str
) -> Tuple[praw.Reddit, Dict[str, str]]:
    """Authenticate with Reddit API using token file for persistence.

    Args:
        dir_path: Project root directory path
        token_file: Name of the token pickle file

    Returns:
        Tuple of authenticated Reddit instance and credentials

    Raises:
        ValueError: If credentials are missing or invalid
        RuntimeError: If authentication fails
    """
    # Get token file to log into reddit
    token_path = os.path.join(dir_path, token_file)
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    else:
        creds = create_token()
        with open(token_path, "wb") as pickle_out:
            pickle.dump(creds, pickle_out)

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
        error_msg = "Missing or invalid Reddit credentials"
        print(f"Error: {error_msg}")
        print("Please check your .env file and ensure all Reddit credentials are set.")
        print(
            "If you don't have a .env file, copy .env.example to .env and fill in your credentials."
        )
        raise ValueError(error_msg)

    try:
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
        error_msg = f"Authentication failed: {e}"
        print(error_msg)
        print("Please check your Reddit credentials:")
        print("1. Make sure your username and password are correct")
        print("2. Verify your Client ID and Client Secret from:")
        print("   https://www.reddit.com/prefs/apps")
        print("3. If you have 2FA enabled, you may need to use an app password")
        print("4. Make sure your Reddit app type is set to 'script'")
        raise RuntimeError(error_msg) from e
