"""Reddit authentication utilities."""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv


def create_token() -> Dict[str, str]:
    """Load Reddit API credentials from environment variables.

    Returns:
        Dictionary containing Reddit API credentials

    Raises:
        SystemExit: If any required credentials are missing
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
        print(f"Missing credentials in .env file: {', '.join(missing_creds)}")
        print("Please check your .env file and ensure all Reddit credentials are set.")
        exit(1)

    # Convert to Dict[str, str] since we've verified all values are not None
    return {key: str(value) for key, value in creds.items()}
