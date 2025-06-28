"""
Configuration file for Reddit Image Scraper

This file contains all configurable variables that are not sensitive credentials.
For Reddit API credentials, see .env file.
"""

# File and directory settings
TOKEN_FILE = "token.pickle"
SUB_LIST_FILE = "data/subreddits.csv"
IMAGES_FOLDER = "data/downloads"

# Reddit scraping settings
POST_SEARCH_AMOUNT = 3
SUBREDDIT_LIMIT = 100  # Maximum posts to check per subreddit
SAFETY_LIMIT = 100  # Maximum posts to check before giving up

# Image processing settings
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif"]
