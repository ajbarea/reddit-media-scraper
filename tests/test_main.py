"""Tests for the Reddit Image Scraper main functionality."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add project root to sys.path to allow importing src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.utils.file_operations import create_folder, get_file_extension
    from src.utils.reddit_auth import create_token
    from src.main import (
        authenticate_reddit,
        download_media,
        _parse_html_for_media,
        _get_accept_header,
        _save_media_file,
        process_subreddit,
        main,
    )
except ImportError as e:
    raise ImportError(
        "Failed to import modules. Ensure the src directory is structured correctly and accessible."
    ) from e


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
            ("https://example.com/image.gif", "gif"),
            ("https://example.com/image.GIF", "gif"),
            ("https://example.com/image.mp4", "mp4"),
            ("https://example.com/video.webm", "webm"),
            (
                "https://example.com/unknown.xyz",
                "jpg",
            ),  # Fallback for unknown extension
            ("https://example.com/noextension", "jpg"),  # Fallback for no extension
            ("https://example.com/image.", "jpg"),  # Fallback for empty extension
            (
                "https://example.com/file?param=value.jpg",
                "jpg",
            ),  # URL with query parameters
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


class TestHelperFunctions:
    """Test helper functions in main module."""

    @pytest.mark.parametrize(
        "file_extension,media_url,expected_header",
        [
            ("mp4", "https://example.com/video.mp4", "video/*, */*"),
            ("webm", "https://example.com/video.webm", "video/*, */*"),
            ("gif", "https://example.com/image.gif", "image/gif, image/*"),
            ("jpg", "https://example.com/image.jpg", "image/*"),
            ("png", "https://example.com/image.png", "image/*"),
            (
                "jpg",
                "https://example.com/video.mp4",
                "video/*, */*",
            ),  # URL overrides extension
        ],
    )
    def test_get_accept_header(self, file_extension, media_url, expected_header):
        """Test Accept header generation for different media types."""
        result = _get_accept_header(file_extension, media_url)
        assert result == expected_header

    @patch("builtins.open", new_callable=mock_open)
    def test_save_media_file_success(self, mock_file):
        """Test successful media file saving."""
        content = b"fake_media_data"
        result = _save_media_file(
            content, "/test/path/", "testsubreddit", "id123", "jpg"
        )

        assert result is True
        mock_file.assert_called_once_with("/test/path/testsubreddit-id123.jpg", "wb")

    def test_save_media_file_empty_content(self):
        """Test media file saving with empty content."""
        result = _save_media_file(b"", "/test/path/", "testsubreddit", "id123", "jpg")
        assert result is False

    def test_save_media_file_none_content(self):
        """Test media file saving with None content."""
        result = _save_media_file(None, "/test/path/", "testsubreddit", "id123", "jpg")
        assert result is False

    @patch("src.main.requests.get")
    @patch("src.main.BeautifulSoup")
    def test_parse_html_for_media_og_video(self, mock_soup, mock_requests):
        """Test HTML parsing for og:video meta tag."""
        mock_response = MagicMock()
        mock_response.content = b"<html></html>"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response

        mock_soup_instance = MagicMock()
        mock_soup.return_value = mock_soup_instance

        # Create a mock that passes isinstance(tag, Tag)
        from bs4 import Tag

        mock_video_tag = MagicMock(spec=Tag)
        mock_video_tag.get.return_value = "https://example.com/video.mp4"

        def find_side_effect(tag, property=None, **kwargs):
            if tag == "meta" and property == "og:video":
                return mock_video_tag
            elif tag == "meta" and property == "og:image":
                return None
            return None

        mock_soup_instance.find.side_effect = find_side_effect

        result = _parse_html_for_media(
            "https://example.com/page", {"User-Agent": "test"}
        )

        assert result == ("https://example.com/video.mp4", "mp4")

    @patch("src.main.requests.get")
    @patch("src.main.BeautifulSoup")
    def test_parse_html_for_media_og_image(self, mock_soup, mock_requests):
        """Test HTML parsing for og:image meta tag."""
        mock_response = MagicMock()
        mock_response.content = b"<html></html>"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response

        mock_soup_instance = MagicMock()
        mock_soup.return_value = mock_soup_instance

        # Create a mock that passes isinstance(tag, Tag)
        from bs4 import Tag

        mock_image_tag = MagicMock(spec=Tag)
        mock_image_tag.get.return_value = "https://example.com/image.jpg"

        def find_side_effect(tag, property=None, **kwargs):
            if tag == "meta" and property == "og:video":
                return None
            elif tag == "meta" and property == "og:image":
                return mock_image_tag
            return None

        mock_soup_instance.find.side_effect = find_side_effect

        result = _parse_html_for_media(
            "https://example.com/page", {"User-Agent": "test"}
        )

        assert result == ("https://example.com/image.jpg", None)

    @patch("src.main.requests.get")
    def test_parse_html_for_media_network_error(self, mock_requests):
        """Test HTML parsing with network error."""
        mock_requests.side_effect = Exception("Network error")

        result = _parse_html_for_media(
            "https://example.com/page", {"User-Agent": "test"}
        )

        assert result == (None, None)

    @patch("src.main.requests.get")
    @patch("src.main.BeautifulSoup")
    def test_parse_html_for_media_no_og_tags(self, mock_soup, mock_requests):
        """Test HTML parsing when no og:video or og:image tags are found."""
        mock_response = MagicMock()
        mock_response.content = b"<html></html>"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response

        mock_soup_instance = MagicMock()
        mock_soup.return_value = mock_soup_instance
        mock_soup_instance.find.return_value = None

        result = _parse_html_for_media(
            "https://example.com/page", {"User-Agent": "test"}
        )

        assert result == (None, None)


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
        mock_reddit_instance.user.me.return_value = None
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
        mock_reddit_instance.user.me.return_value = None
        mock_reddit.return_value = mock_reddit_instance

        reddit, creds = authenticate_reddit("/test/path")

        mock_create_token.assert_called_once()
        mock_pickle_dump.assert_called_once()
        assert reddit == mock_reddit_instance
        assert creds == mock_credentials

    @patch("src.main.praw.Reddit")
    @patch("src.main.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.main.os.path.exists")
    def test_authenticate_reddit_invalid_credentials(
        self, mock_exists, mock_file, mock_pickle_load, mock_reddit
    ):
        """Test authentication with invalid credentials."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = {}  # Empty credentials

        with pytest.raises(SystemExit):
            authenticate_reddit("/test/path")

    @patch("src.main.praw.Reddit")
    @patch("src.main.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.main.os.path.exists")
    def test_authenticate_reddit_authentication_failure(
        self, mock_exists, mock_file, mock_pickle_load, mock_reddit, mock_credentials
    ):
        """Test authentication failure during Reddit connection."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = mock_credentials
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.user.me.side_effect = Exception("Authentication failed")
        mock_reddit.return_value = mock_reddit_instance

        with pytest.raises(SystemExit):
            authenticate_reddit("/test/path")

    @patch("src.main._save_media_file")
    @patch("src.main.get_file_extension")
    @patch("src.main._get_accept_header")
    @patch("src.main.requests.get")
    def test_download_media_direct_url_success(
        self,
        mock_requests,
        mock_get_accept_header,
        mock_get_extension,
        mock_save_file,
        mock_credentials,
    ):
        """Test successful media download from direct URL."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/image.jpg"
        mock_submission.id = "test123"

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response

        mock_get_extension.return_value = "jpg"
        mock_get_accept_header.return_value = "image/*"
        mock_save_file.return_value = True

        result = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", True
        )

        assert result is True
        mock_requests.assert_called_once()
        mock_save_file.assert_called_once()

    @patch("src.main._parse_html_for_media")
    @patch("src.main._save_media_file")
    @patch("src.main.get_file_extension")
    @patch("src.main._get_accept_header")
    @patch("src.main.requests.get")
    def test_download_media_indirect_url_success(
        self,
        mock_requests,
        mock_get_accept_header,
        mock_get_extension,
        mock_save_file,
        mock_parse_html,
        mock_credentials,
    ):
        """Test successful media download from indirect URL (HTML parsing)."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/page"
        mock_submission.id = "test123"

        mock_parse_html.return_value = ("https://example.com/video.mp4", "mp4")

        mock_response = MagicMock()
        mock_response.content = b"fake_video_data"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response

        mock_get_extension.return_value = (
            "mp4"  # Won't be called since extension is from HTML
        )
        mock_get_accept_header.return_value = "video/*, */*"
        mock_save_file.return_value = True

        result = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", False
        )

        assert result is True
        mock_parse_html.assert_called_once()
        mock_save_file.assert_called_once()

    @patch("src.main._parse_html_for_media")
    def test_download_media_indirect_url_no_media_found(
        self, mock_parse_html, mock_credentials
    ):
        """Test media download when no media found in HTML."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/page"
        mock_submission.id = "test123"

        mock_parse_html.return_value = (None, None)

        result = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", False
        )

        assert result is False

    @patch("src.main.requests.get")
    def test_download_media_network_error(self, mock_requests, mock_credentials):
        """Test media download with network error."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/image.jpg"
        mock_submission.id = "test123"

        mock_requests.side_effect = Exception("Network error")

        result = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", True
        )

        assert result is False

    @patch("src.main.download_media")
    @patch("src.main.get_file_extension")
    def test_process_subreddit(
        self, mock_get_extension, mock_download_media, mock_credentials
    ):
        """Test processing a subreddit."""
        mock_reddit = MagicMock()
        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        # Create mock submissions
        mock_submission1 = MagicMock()
        mock_submission1.url = "https://example.com/image1.jpg"
        mock_submission1.id = "id1"

        mock_submission2 = MagicMock()
        mock_submission2.url = "https://example.com/image2.png"
        mock_submission2.id = "id2"

        mock_submission3 = MagicMock()
        mock_submission3.url = "https://example.com/image3.gif"
        mock_submission3.id = "id3"

        mock_subreddit.new.return_value = [
            mock_submission1,
            mock_submission2,
            mock_submission3,
        ]
        mock_download_media.side_effect = [True, True, True]
        mock_get_extension.side_effect = ["jpg", "png", "gif"]

        # Mock the print function to avoid output during tests
        with patch("builtins.print"):
            process_subreddit(
                mock_reddit, mock_credentials, "testsubreddit", "/test/path/"
            )

        assert mock_download_media.call_count == 3

    @patch("src.main.process_subreddit")
    @patch("src.main.authenticate_reddit")
    @patch("src.main.create_folder")
    @patch("builtins.open", new_callable=mock_open, read_data="testsubreddit\nfood\n")
    def test_main_function(
        self,
        mock_file,
        mock_create_folder,
        mock_authenticate_reddit,
        mock_process_subreddit,
        mock_credentials,
    ):
        """Test main function execution."""
        mock_reddit = MagicMock()
        mock_authenticate_reddit.return_value = (mock_reddit, mock_credentials)

        main()

        mock_create_folder.assert_called_once()
        mock_authenticate_reddit.assert_called_once()
        assert mock_process_subreddit.call_count == 2  # Two subreddits in CSV
