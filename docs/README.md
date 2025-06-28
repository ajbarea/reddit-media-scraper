# Reddit Image Scraper

[![Clarity Coders YouTube](https://i.imgur.com/sG7xxyc.png)](https://youtu.be/HubXt90MLfI)

## Create a reddit account

- Signup for a reddit account.
- Select the "Are you a developer? Create an app button" [on Reddit's app preferences page](https://reddit.com/prefs/apps).
- Give you program a name and a redirect URL(<http://localhost>).
- On the final screen note your client id and secret.

| Create Account | Access Developer | Name | ID and secret |
| --- | --- | --- | --- |
| ![Create Account](https://i.imgur.com/l5tWhOW.png) | ![Access Developer](https://i.imgur.com/Ir7Nqx6.png) | ![Name](https://i.imgur.com/1hoKGvH.png) | ![ID and secret](https://i.imgur.com/JmH5vBn.png) |

## Setup Environment File

Create a `.env` file in the root directory with your Reddit API credentials:

```properties
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=python:reddit-image-scraper:1.0 (by u/your_username)
REDDIT_USERNAME=your_username_here
REDDIT_PASSWORD=your_password_here
```

Replace the placeholder values with your actual Reddit API credentials obtained from the previous step.

## Setup Virtual Environment

Before running the script, it's recommended to set up a virtual environment to manage dependencies:

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run download script

Run from the src directory:

```bash
python src/main.py
```

- Add any subs you want to download to the data/subreddits.csv one per line.
- Run the main script from the src directory
- The first time you run the script it will ask you for details. Note you don't need to enter a user name or password if you don't plan on posting.
- The script will create a token.pickle file so you don't have to enter them again. If you mess up your credentials just delete the pickle file and it will ask for them again.
- The script will create an images folder and fill it with images it finds.

## Configuration

The application uses two configuration files:

- **`.env`**: Contains private Reddit API credentials (client ID, secret, username, password)
- **`config.py`**: Contains all other configurable settings like:
  - Number of posts to search (`POST_SEARCH_AMOUNT`)
  - Supported image formats
  - File and folder names
  - Image processing settings

You can modify `config.py` to customize the scraper's behavior without touching the main code.

## Need more help?

- YouTube [Clarity Coders](https://www.youtube.com/claritycoders)
- Chat with me! [Discord](https://discord.gg/cAWW5qq)

[![Discord](https://img.shields.io/discord/709518323720912956?label=Discord&logo=discord&logoColor=ffffff&labelColor=7289DA&color=2c2f33)](https://discord.gg/cAWW5qq)
