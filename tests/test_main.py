"""Tests for the Reddit Image Scraper main functionality."""

import os
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Add project root to sys.path to allow importing src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.main import main
    from src.utils.file_operations import (
        FileOperationError,
        create_folder,
        get_file_extension,
        get_file_type,
        get_project_root_path,
        get_supported_extensions,
        is_supported_extension,
        validate_path,
        validate_url,
    )
    from src.utils.media_download import download_media, save_media_file
    from src.utils.media_parsing import get_accept_header, parse_html_for_media
    from src.utils.reddit_auth import authenticate_reddit, create_token
    from src.utils.subreddit_processor import load_subreddit_list, process_subreddit
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

    def test_create_folder_invalid_type(self):
        """Test folder creation with invalid path type."""
        with pytest.raises(TypeError):
            create_folder(123)  # type: ignore  # Invalid type for testing

    def test_validate_path_success(self, tmp_path):
        """Test successful path validation."""
        from pathlib import Path

        result = validate_path(str(tmp_path))
        assert isinstance(result, Path)

    def test_validate_path_invalid_type(self):
        """Test path validation with invalid type."""
        with pytest.raises(TypeError):
            validate_path(123)  # type: ignore  # Invalid type for testing

    def test_validate_path_security_check(self):
        """Test path validation prevents directory traversal."""
        with pytest.raises(FileOperationError):
            validate_path("../../../etc/passwd")

    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com/path") is True

    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        assert validate_url("not-a-url") is False
        assert validate_url("") is False
        assert validate_url("   ") is False

    def test_validate_url_invalid_type(self):
        """Test URL validation with invalid type."""
        with pytest.raises(TypeError):
            validate_url(123)  # type: ignore  # Invalid type for testing

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = get_supported_extensions()
        assert "image" in extensions
        assert "video" in extensions
        assert "all" in extensions
        assert "jpg" in extensions["image"]
        assert "mp4" in extensions["video"]
        assert "jpg" in extensions["all"]

    @pytest.mark.parametrize(
        "extension,expected",
        [
            ("jpg", True),
            (".jpg", True),
            ("mp4", True),
            (".mp4", True),
            ("xyz", False),
            ("", False),
        ],
    )
    def test_is_supported_extension(self, extension, expected):
        """Test extension support checking."""
        assert is_supported_extension(extension) is expected

    def test_is_supported_extension_invalid_type(self):
        """Test extension support checking with invalid type."""
        with pytest.raises(TypeError):
            is_supported_extension(123)  # type: ignore  # Invalid type for testing

    @pytest.mark.parametrize(
        "extension,expected",
        [
            ("jpg", "image"),
            ("mp4", "video"),
            ("xyz", None),
        ],
    )
    def test_get_file_type(self, extension, expected):
        """Test file type categorization."""
        assert get_file_type(extension) == expected

    def test_get_project_root_path(self):
        """Test getting project root path."""
        root_path = get_project_root_path()
        assert isinstance(root_path, str)
        assert len(root_path) > 0

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
            ("https://example.com/image.tiff", "tif"),  # Test normalization
            ("https://example.com/image.bmp", "bmp"),
            ("https://example.com/image.webp", "webp"),
            ("https://example.com/video.avi", "avi"),
            ("https://example.com/video.mov", "mov"),
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
            ("https://example.com/file.jpg#fragment", "jpg"),  # URL with fragment
            ("", "jpg"),  # Empty URL fallback
        ],
    )
    def test_get_file_extension(self, url, expected):
        """Test file extension detection for various URLs."""
        assert get_file_extension(url) == expected

    def test_get_file_extension_invalid_type(self):
        """Test file extension detection with invalid type."""
        with pytest.raises(TypeError):
            get_file_extension(123)  # type: ignore  # Invalid type for testing


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

        with pytest.raises(ValueError):
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

        with pytest.raises(ValueError):
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
        result = get_accept_header(file_extension, media_url)
        assert result == expected_header

    @patch("builtins.open", new_callable=mock_open)
    def test_save_media_file_success(self, mock_file):
        """Test successful media file saving."""
        content = b"fake_media_data"
        result = save_media_file(
            content, "/test/path/", "testsubreddit", "id123", "jpg"
        )

        assert result is True
        mock_file.assert_called_once_with("/test/path/testsubreddit-id123.jpg", "wb")

    def test_save_media_file_empty_content(self):
        """Test media file saving with empty content."""
        result = save_media_file(b"", "/test/path/", "testsubreddit", "id123", "jpg")
        assert result is False

    def test_save_media_file_none_content(self):
        """Test media file saving with None content."""
        result = save_media_file(None, "/test/path/", "testsubreddit", "id123", "jpg")
        assert result is False

    @patch("src.utils.media_parsing.requests.get")
    @patch("src.utils.media_parsing.BeautifulSoup")
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

        result = parse_html_for_media(
            "https://example.com/page", {"User-Agent": "test"}
        )

        assert result == ("https://example.com/video.mp4", "mp4")

    @patch("src.utils.media_parsing.requests.get")
    @patch("src.utils.media_parsing.BeautifulSoup")
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

        result = parse_html_for_media(
            "https://example.com/page", {"User-Agent": "test"}
        )

        assert result == ("https://example.com/image.jpg", None)

    @patch("src.utils.media_parsing.requests.get")
    def test_parse_html_for_media_network_error(self, mock_requests):
        """Test HTML parsing with network error."""
        mock_requests.side_effect = Exception("Network error")

        result = parse_html_for_media(
            "https://example.com/page", {"User-Agent": "test"}
        )

        assert result == (None, None)

    @patch("src.utils.media_parsing.requests.get")
    @patch("src.utils.media_parsing.BeautifulSoup")
    def test_parse_html_for_media_no_og_tags(self, mock_soup, mock_requests):
        """Test HTML parsing when no og:video or og:image tags are found."""
        mock_response = MagicMock()
        mock_response.content = b"<html></html>"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response

        mock_soup_instance = MagicMock()
        mock_soup.return_value = mock_soup_instance
        mock_soup_instance.find.return_value = None

        result = parse_html_for_media(
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

    @patch("src.utils.reddit_auth.praw.Reddit")
    @patch("src.utils.reddit_auth.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.utils.reddit_auth.os.path.exists")
    def test_authenticate_reddit_existing_token(
        self, mock_exists, mock_file, mock_pickle_load, mock_reddit, mock_credentials
    ):
        """Test authentication with existing token file."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = mock_credentials
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.user.me.return_value = None
        mock_reddit.return_value = mock_reddit_instance

        reddit, creds = authenticate_reddit("/test/path", "token.pickle")

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

    @patch("src.utils.reddit_auth.praw.Reddit")
    @patch("src.utils.reddit_auth.create_token")
    @patch("src.utils.reddit_auth.pickle.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.utils.reddit_auth.os.path.exists")
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

        reddit, creds = authenticate_reddit("/test/path", "token.pickle")

        mock_create_token.assert_called_once()
        mock_pickle_dump.assert_called_once()
        assert reddit == mock_reddit_instance
        assert creds == mock_credentials

    @patch("src.utils.reddit_auth.praw.Reddit")
    @patch("src.utils.reddit_auth.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.utils.reddit_auth.os.path.exists")
    def test_authenticate_reddit_invalid_credentials(
        self, mock_exists, mock_file, mock_pickle_load, mock_reddit
    ):
        """Test authentication with invalid credentials."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = {}  # Empty credentials

        with pytest.raises(ValueError):
            authenticate_reddit("/test/path", "token.pickle")

    @patch("src.utils.reddit_auth.praw.Reddit")
    @patch("src.utils.reddit_auth.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.utils.reddit_auth.os.path.exists")
    def test_authenticate_reddit_authentication_failure(
        self, mock_exists, mock_file, mock_pickle_load, mock_reddit, mock_credentials
    ):
        """Test authentication failure during Reddit connection."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = mock_credentials
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.user.me.side_effect = Exception("Authentication failed")
        mock_reddit.return_value = mock_reddit_instance

        with pytest.raises(RuntimeError):
            authenticate_reddit("/test/path", "token.pickle")

    @patch("src.utils.media_download.save_media_file")
    @patch("src.utils.file_operations.get_file_extension")
    @patch("src.utils.media_parsing.get_accept_header")
    @patch("src.utils.media_download.requests.get")
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

        success, extension = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", True
        )

        assert success is True
        assert extension == "jpg"
        mock_requests.assert_called_once()
        mock_save_file.assert_called_once()

    @patch("src.utils.media_download.parse_html_for_media")
    @patch("src.utils.media_download.save_media_file")
    @patch("src.utils.media_download.get_file_extension")
    @patch("src.utils.media_download.get_accept_header")
    @patch("src.utils.media_download.requests.get")
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

        success, extension = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", False
        )

        assert success is True
        assert extension == "mp4"
        mock_parse_html.assert_called_once()
        mock_save_file.assert_called_once()

    @patch("src.utils.media_parsing.parse_html_for_media")
    def test_download_media_indirect_url_no_media_found(
        self, mock_parse_html, mock_credentials
    ):
        """Test media download when no media found in HTML."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/page"
        mock_submission.id = "test123"

        mock_parse_html.return_value = (None, None)

        success, extension = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", False
        )

        assert success is False
        assert extension is None

    @patch("src.utils.media_download.requests.get")
    def test_download_media_network_error(self, mock_requests, mock_credentials):
        """Test media download with network error."""
        mock_submission = MagicMock()
        mock_submission.url = "https://example.com/image.jpg"
        mock_submission.id = "test123"

        mock_requests.side_effect = Exception("Network error")

        success, extension = download_media(
            mock_submission, mock_credentials, "/test/path/", "testsubreddit", True
        )

        assert success is False
        assert extension is None

    @patch("src.utils.subreddit_processor.download_media")
    def test_process_subreddit(self, mock_download_media, mock_credentials):
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
        # Mock download_media to return (success, extension) tuples
        mock_download_media.side_effect = [(True, "jpg"), (True, "png"), (True, "gif")]

        # Mock the print function to avoid output during tests
        with patch("builtins.print"):
            process_subreddit(
                reddit=mock_reddit,
                creds=mock_credentials,
                sub="testsubreddit",
                media_path="/test/path/",
                post_search_amount=3,
                subreddit_limit=100,
                safety_limit=100,
                supported_media_formats=["jpg", "png", "gif"],
            )

        assert mock_download_media.call_count == 3

    @patch("src.main.load_subreddit_list")
    @patch("src.main.process_subreddit")
    @patch("src.main.authenticate_reddit")
    @patch("src.main.create_folder")
    def test_main_function(
        self,
        mock_create_folder,
        mock_authenticate_reddit,
        mock_process_subreddit,
        mock_load_subreddit_list,
        mock_credentials,
    ):
        """Test main function execution."""
        mock_reddit = MagicMock()
        mock_authenticate_reddit.return_value = (mock_reddit, mock_credentials)
        mock_load_subreddit_list.return_value = ["testsubreddit", "food"]

        main()

        mock_create_folder.assert_called_once()
        mock_authenticate_reddit.assert_called_once()
        mock_load_subreddit_list.assert_called_once()
        assert mock_process_subreddit.call_count == 2  # Two subreddits in list


class TestSubredditProcessor:
    """Test subreddit processing utilities."""

    def test_load_subreddit_list_success(self, tmp_path):
        """Test successful loading of subreddit list."""
        # Create a test CSV file
        test_csv = tmp_path / "test_subreddits.csv"
        test_csv.write_text("programming\npics\n\nfood\n")  # Include empty line

        result = load_subreddit_list(str(test_csv))

        assert result == ["programming", "pics", "food"]
        assert len(result) == 3

    def test_load_subreddit_list_empty_file(self, tmp_path):
        """Test loading from empty subreddit list file."""
        test_csv = tmp_path / "empty.csv"
        test_csv.write_text("")

        result = load_subreddit_list(str(test_csv))

        assert result == []

    def test_load_subreddit_list_whitespace_handling(self, tmp_path):
        """Test subreddit list handles whitespace correctly."""
        test_csv = tmp_path / "whitespace.csv"
        test_csv.write_text("  programming  \n\npics\n   \nfood   \n")

        result = load_subreddit_list(str(test_csv))

        assert result == ["programming", "pics", "food"]
