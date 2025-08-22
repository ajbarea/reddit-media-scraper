"""
Configuration file for Reddit Image Scraper

This file contains all configurable variables that are not sensitive credentials.
For Reddit API credentials, see .env file.
"""

from typing import List

# File and directory settings
TOKEN_FILE: str = "token.pickle"
SUB_LIST_FILE: str = "data/subreddits.csv"
USER_LIST_FILE: str = "data/usersubmissions.csv"
IMAGES_FOLDER: str = "data/downloads"

# Reddit scraping settings
POST_SEARCH_AMOUNT: int = 10
SUBREDDIT_LIMIT: int = 100  # Maximum posts to check per subreddit
SAFETY_LIMIT: int = 100  # Maximum posts to check before giving up

# Media processing settings
SUPPORTED_MEDIA_FORMATS: List[str] = ["jpg", "jpeg", "png", "gif", "mp4", "webm"]

# For images only
# SUPPORTED_MEDIA_FORMATS: List[str] = ["jpg", "jpeg", "png", "gif"]
