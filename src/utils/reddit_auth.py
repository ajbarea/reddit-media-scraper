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
    # Create fresh credentials
    token_path = os.path.join(dir_path, token_file)

    print("Loading Reddit credentials...")
    creds = create_token()

    # Save credentials for future use
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
        print("Testing Reddit connection...")
        print("✅  Authentication successful!")
        return reddit, creds

    except Exception as e:
        error_msg = f"Authentication failed: {e}"
        print(f"\n❌ {error_msg}")
        print("\n🔍 Troubleshooting steps:")
        print("1. Verify your Reddit app configuration:")
        print("   - Go to: https://www.reddit.com/prefs/apps")
        print("   - Make sure your app type is 'script' (not 'web app')")
        print("   - Copy the correct Client ID and Client Secret")
        print("\n2. Check your credentials:")
        print(f"   - Username: {creds.get('username', 'NOT SET')}")
        print(
            f"   - Client ID: {creds.get('client_id', 'NOT SET')[:8] if creds.get('client_id') else 'NOT SET'}..."
        )
        print(
            f"   - Client Secret: {'SET' if creds.get('client_secret') else 'NOT SET'}"
        )
        print(f"   - Password: {'SET' if creds.get('password') else 'NOT SET'}")
        print("\n3. Common issues:")
        print("   - If you have 2FA enabled, use an app-specific password")
        print("   - Make sure there are no extra spaces in your .env file")
        print("   - Try creating a new Reddit app if the current one doesn't work")
        print("   - Ensure your Reddit account is verified")

        # Delete the token file so we don't use bad credentials next time
        if os.path.exists(token_path):
            os.remove(token_path)
            print("\n🗑️  Removed cached credentials file")

        raise RuntimeError(error_msg) from e
