# Reddit Media Scraper

A Python application for downloading images and videos from Reddit subreddits with advanced media detection and AWS S3 integration support.

## Features

- **Multi-format Support**: Downloads images (JPG, PNG, GIF, WebP, etc.) and videos (MP4, WebM, etc.)
- **Smart Media Detection**: Parses HTML pages to find embedded media using Open Graph tags
- **Configurable Settings**: Easily customize download behavior through configuration files
- **Robust Error Handling**: Comprehensive error handling and logging
- **AWS Integration**: Optional S3 upload functionality with web interface
- **Type Safety**: Full type hints and MyPy support
- **Testing**: Comprehensive test suite with pytest

## Prerequisites

Before using this Reddit media scraper, you'll need to set up the following:

### Reddit API Access

1. **Create a Reddit Account**: If you don't have one, sign up at [reddit.com](https://www.reddit.com)
2. **Create a Reddit App**:
   - Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Fill in the required fields:
     - **Name**: Your app name (e.g., "Media Scraper")
     - **Description**: Brief description of your app
     - **Redirect URI**: Use `http://localhost:8080` (required but not used)
   - Click "Create app"
3. **Note Your Credentials**:
   - **Client ID**: Found under your app name (short string)
   - **Client Secret**: The "secret" field (longer string)

### AWS Account (Optional)

If you plan to store media in AWS S3 or use other AWS services:

1. **Create an AWS Account**: Sign up at [aws.amazon.com](https://aws.amazon.com)
2. **Set Up IAM User** (recommended for security):
   - Go to AWS IAM Console
   - Create a new user with programmatic access
   - Attach appropriate policies (e.g., S3FullAccess if storing media)
   - Save your Access Key ID and Secret Access Key
3. **Set Up S3 Bucket** (if using S3 features):
   - Create a new S3 bucket for media storage
   - Configure bucket permissions for public read if needed

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/reddit-media-scraper.git
cd reddit-media-scraper
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit the `.env` file with your Reddit API credentials:

```properties
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=python:reddit-media-scraper:1.0 (by u/your_username)
REDDIT_USERNAME=your_username_here
REDDIT_PASSWORD=your_password_here

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=your_aws_region_here
AWS_S3_BUCKET=your_s3_bucket_name_here
```

### 4. Configure Subreddits

Edit `data/subreddits.csv` and add the subreddits you want to scrape (one per line):

```csv
earthporn
pics
funny
gifs
```

## Usage

### Basic Usage

Run the scraper from the project root:

```bash
python -m src.main
```

Or use the VS Code task:

- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
- Type "Tasks: Run Task"
- Select "Run Reddit Image Scraper"

### What the Script Does

1. **Authentication**: Loads credentials from `.env` file and authenticates with Reddit API
2. **Token Management**: Creates and saves a `token.pickle` file for session persistence
3. **Media Discovery**: Searches through subreddit posts for media content
4. **Smart Detection**: Identifies direct media links and parses HTML for embedded media
5. **Download**: Saves media files to `data/downloads/` with organized naming
6. **Progress Tracking**: Shows real-time download progress and statistics

### AWS S3 Upload (Optional)

If you've configured AWS credentials, you can use the web interface to upload downloaded media to S3:

1. Open `frontend/index.html` in your browser
2. Configure your AWS Cognito Identity Pool ID in the HTML file
3. Select and upload media files directly to your S3 bucket

## Configuration

The application uses multiple configuration files:

### Environment Variables (`.env`)

- **Reddit API**: Client ID, secret, username, password
- **AWS**: Access keys, region, S3 bucket name, Cognito pool ID

### Application Settings (`src/config.py`)

```python
# Media download settings
POST_SEARCH_AMOUNT = 3          # Media items to download per subreddit
SUBREDDIT_LIMIT = 100           # Maximum posts to check per subreddit
SAFETY_LIMIT = 100              # Safety limit to prevent infinite loops

# File and directory settings
IMAGES_FOLDER = "data/downloads" # Download directory
SUB_LIST_FILE = "data/subreddits.csv" # Subreddit list file

# Supported media formats
SUPPORTED_MEDIA_FORMATS = ["jpg", "jpeg", "png", "gif", "mp4", "webm"]
```

## Project Structure

```text
reddit-media-scraper/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── config.py            # Configuration settings
│   └── utils/
│       ├── __init__.py
│       ├── reddit_auth.py   # Reddit authentication utilities
│       └── file_operations.py # File and URL handling utilities
├── data/
│   ├── subreddits.csv       # List of subreddits to scrape
│   └── downloads/           # Downloaded media files
├── frontend/
│   └── index.html           # AWS S3 upload interface
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Test suite
├── docs/
│   └── README.md            # This file
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
└── token.pickle            # Reddit session token (auto-generated)
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_main.py
```

### Type Checking

```bash
# Run MyPy type checking
mypy src/

# Check specific file
mypy src/main.py
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Verify your Reddit credentials in `.env`
   - Check that your Reddit app type is set to "script"
   - Ensure 2FA is disabled or use an app password

2. **No Media Found**:
   - Check that subreddits exist and are accessible
   - Verify subreddit names in `data/subreddits.csv`
   - Some subreddits may have limited media content

3. **Download Failures**:
   - Check internet connection
   - Verify media URLs are accessible
   - Some media may be restricted or require authentication

4. **Permission Errors**:
   - Ensure write permissions to `data/downloads/` directory
   - Run with appropriate user permissions
