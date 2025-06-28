"""Tests for the Reddit Image Scraper main functionality."""

import pytest
from unittest.mock import patch, MagicMock, mock_open

from src.utils.file_operations import create_folder, get_file_extension
from src.utils.reddit_auth import create_token
from src.main import authenticate_reddit, download_image


class TestFileOperations:
    """Test file operations utilities."""

    def test_create_folder_success(self, tmp_path):
        """Test successful folder creation."""
        test_path = tmp_path / "test_folder"
        create_folder(str(test_path))
        assert test_path.exists()

    def test_create_folder_nested(self, tmp_path):
        """Test nested folder creation."""
        test_path = tmp_path / "nested" / "folder" / "structure"
        create_folder(str(test_path))
        assert test_path.exists()

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://example.com/image.jpg", "jpg"),
            ("https://example.com/image.jpeg", "jpg"),
            ("https://example.com/image.JPG", "jpg"),
            ("https://example.com/image.JPEG", "jpg"),
            ("https://example.com/image.png", "png"),
            ("https://example.com/image.PNG", "png"),
            ("https://example.com/unknown.xyz", "jpg"),
            ("https://example.com/noextension", "jpg"),
        ],
    )
    def test_get_file_extension(self, url, expected):
        """Test file extension detection for various URLs."""
        assert get_file_extension(url) == expected


class TestRedditAuth:
    """Test Reddit authentication utilities."""

    @patch("src.utils.reddit_auth.load_dotenv")
    @patch("src.utils.reddit_auth.os.getenv")
    def test_create_token_success(self, mock_getenv, mock_load_dotenv):
        """Test successful token creation with all credentials."""
        mock_getenv.side_effect = lambda key: {
            "REDDIT_CLIENT_ID": "test_id",
            "REDDIT_CLIENT_SECRET": "test_secret",
            "REDDIT_USER_AGENT": "test_agent",
            "REDDIT_USERNAME": "test_user",
            "REDDIT_PASSWORD": "test_pass",
        }.get(key)

        result = create_token()

        mock_load_dotenv.assert_called_once()
        assert result["client_id"] == "test_id"
        assert result["client_secret"] == "test_secret"
        assert result["user_agent"] == "test_agent"
        assert result["username"] == "test_user"
        assert result["password"] == "test_pass"

    @patch("src.utils.reddit_auth.load_dotenv")
    @patch("src.utils.reddit_auth.os.getenv")
    def test_create_token_missing_credentials(self, mock_getenv, mock_load_dotenv):
        """Test token creation fails with missing credentials."""
        mock_getenv.return_value = None

        with pytest.raises(SystemExit):
            create_token()

    @pytest.mark.parametrize(
        "missing_key",
        [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USER_AGENT",
            "REDDIT_USERNAME",
            "REDDIT_PASSWORD",
        ],
    )
    @patch("src.utils.reddit_auth.load_dotenv")
    @patch("src.utils.reddit_auth.os.getenv")
    def test_create_token_partial_credentials(
        self, mock_getenv, mock_load_dotenv, missing_key
    ):
        """Test token creation fails when any single credential is missing."""
        credentials = {
            "REDDIT_CLIENT_ID": "test_id",
            "REDDIT_CLIENT_SECRET": "test_secret",
            "REDDIT_USER_AGENT": "test_agent",
            "REDDIT_USERNAME": "test_user",
            "REDDIT_PASSWORD": "test_pass",
        }
        del credentials[missing_key]  # Remove the key entirely
        mock_getenv.side_effect = lambda key: credentials.get(key)

        with pytest.raises(SystemExit):
            create_token()


class TestMainFunctionality:
    """Test main application functionality."""

    @pytest.fixture
    def mock_credentials(self):
        """Fixture providing mock Reddit credentials."""
        return {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "user_agent": "test_agent",
            "username": "test_user",
            "password": "test_pass",
        }

    @patch("src.main.praw.Reddit")
    @patch("src.main.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.main.os.path.exists")
    def test_authenticate_reddit_existing_token(
        self, mock_exists, mock_file, mock_pickle_load, mock_reddit, mock_credentials
    ):
        """Test authentication with existing token file."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = mock_credentials
        mock_reddit_instance = MagicMock()
        mock_reddit.return_value = mock_reddit_instance

        reddit, creds = authenticate_reddit("/test/path")

        mock_exists.assert_called_once()
        mock_pickle_load.assert_called_once()
        mock_reddit.assert_called_once_with(
            client_id="test_id",
            client_secret="test_secret",
            user_agent="test_agent",
            username="test_user",
            password="test_pass",
        )
        assert reddit == mock_reddit_instance
        assert creds == mock_credentials

    @patch("src.main.praw.Reddit")
    @patch("src.main.create_token")
    @patch("src.main.pickle.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.main.os.path.exists")
    def test_authenticate_reddit_new_token(
        self,
        mock_exists,
        mock_file,
        mock_pickle_dump,
        mock_create_token,
        mock_reddit,
        mock_credentials,
    ):
        """Test authentication with new token creation."""
        mock_exists.return_value = False
        mock_create_token.return_value = mock_credentials
        mock_reddit_instance = MagicMock()
        mock_reddit.return_value = mock_reddit_instance

        reddit, creds = authenticate_reddit("/test/path")

        mock_create_token.assert_called_once()
        mock_pickle_dump.assert_called_once()
        assert reddit == mock_reddit_instance
        assert creds == mock_credentials

    @patch("src.main.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_image_success(
        self, mock_file, mock_requests_get, mock_credentials
    ):
        """Test successful image download."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/image.jpg"
        mock_submission.id = "test123"

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        result = download_image(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit"
        )

        assert result is True
        mock_requests_get.assert_called_once_with(
            "https://example.com/image.jpg",
            headers={"User-Agent": "test_agent", "Accept": "image/*"},
            timeout=30,
        )
        mock_file.assert_called_once_with("/test/path/testsubreddit-test123.jpg", "wb")

    @patch("src.main.requests.get")
    def test_download_image_network_error(self, mock_requests_get, mock_credentials):
        """Test image download with network error."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/image.jpg"
        mock_submission.id = "test123"

        mock_requests_get.side_effect = Exception("Network error")

        result = download_image(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit"
        )

        assert result is False

    @patch("src.main.requests.get")
    def test_download_image_empty_content(self, mock_requests_get, mock_credentials):
        """Test image download with empty response content."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/image.jpg"
        mock_submission.id = "test123"

        mock_response = MagicMock()
        mock_response.content = b""
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        result = download_image(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit"
        )

        assert result is False
