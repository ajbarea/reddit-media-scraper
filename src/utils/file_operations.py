"""File and directory operation utilities with comprehensive type checking."""

import os
import re
from pathlib import Path
from typing import Dict, Final, FrozenSet, List, Optional, Union
from urllib.parse import urlparse

# Type aliases for better readability
PathLike = Union[str, os.PathLike[str]]
FileExtension = str
URLString = str

# Constants for supported file extensions
SUPPORTED_IMAGE_EXTENSIONS: Final[FrozenSet[str]] = frozenset(
    {"jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff", "tif"}
)

SUPPORTED_VIDEO_EXTENSIONS: Final[FrozenSet[str]] = frozenset(
    {"mp4", "webm", "avi", "mov", "mkv", "flv", "wmv", "m4v"}
)

SUPPORTED_EXTENSIONS: Final[FrozenSet[str]] = (
    SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS
)

# Extension normalization mapping
EXTENSION_MAPPING: Final[Dict[str, str]] = {
    "jpeg": "jpg",
    "tiff": "tif",
}

DEFAULT_EXTENSION: Final[str] = "jpg"

# URL validation pattern
URL_PATTERN: Final[re.Pattern[str]] = re.compile(r"^https?://[^\s]+$")


class FileOperationError(Exception):
    """Custom exception for file operation errors."""

    def __init__(self, message: str, path: Optional[PathLike] = None) -> None:
        """Initialize FileOperationError.

        Args:
            message: Error message
            path: Optional path that caused the error
        """
        super().__init__(message)
        self.path = path


def validate_path(path: PathLike) -> Path:
    """Validate and normalize a file system path.

    Args:
        path: Path to validate

    Returns:
        Validated Path object

    Raises:
        FileOperationError: If path is invalid
        TypeError: If path is not a valid path type
    """
    if not isinstance(path, (str, os.PathLike)):
        raise TypeError(f"Path must be str or PathLike, got {type(path).__name__}")

    try:
        # Check for potential security issues (path traversal) before resolving
        path_str = str(path)
        if ".." in path_str:
            raise FileOperationError(
                f"Path contains parent directory references: {path}", path
            )

        normalized_path = Path(path).resolve()
        return normalized_path

    except (OSError, ValueError) as e:
        raise FileOperationError(f"Invalid path: {path}. Error: {e}", path) from e


def validate_url(url: URLString) -> bool:
    """Validate if a string is a properly formatted URL.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid

    Raises:
        TypeError: If url is not a string
    """
    if not isinstance(url, str):
        raise TypeError(f"URL must be a string, got {type(url).__name__}")

    if not url.strip():
        return False

    return bool(URL_PATTERN.match(url.strip()))


def create_folder(path: PathLike) -> None:
    """Create directory if it doesn't exist with comprehensive error handling.

    Args:
        path: Directory path to create

    Raises:
        FileOperationError: If directory creation fails
        TypeError: If path is not a valid path type

    Example:
        >>> create_folder("/path/to/directory")
        >>> create_folder(Path("/path/to/directory"))
    """
    if not isinstance(path, (str, os.PathLike)):
        raise TypeError(f"Path must be str or PathLike, got {type(path).__name__}")

    try:
        validated_path = validate_path(path)
        validated_path.mkdir(parents=True, exist_ok=True)

    except OSError as e:
        raise FileOperationError(
            f"Failed to create directory '{path}': {e}", path
        ) from e


def get_file_extension(url: URLString) -> FileExtension:
    """Determine file extension from URL with comprehensive validation.

    Args:
        url: URL to analyze

    Returns:
        File extension (normalized, e.g., 'jpg', 'png', 'mp4') or default 'jpg'

    Raises:
        TypeError: If url is not a string

    Example:
        >>> get_file_extension("https://example.com/image.jpeg")
        'jpg'
        >>> get_file_extension("https://example.com/video.mp4")
        'mp4'
        >>> get_file_extension("https://example.com/unknown")
        'jpg'
    """
    if not isinstance(url, str):
        raise TypeError(f"URL must be a string, got {type(url).__name__}")

    if not url.strip():
        return DEFAULT_EXTENSION

    try:
        # Parse URL to handle query parameters and fragments properly
        parsed_url = urlparse(url.strip())
        path_part = parsed_url.path

        if not path_part:
            return DEFAULT_EXTENSION

        # Extract filename from path
        filename = Path(path_part).name

        if not filename or filename == "." or filename == "..":
            return DEFAULT_EXTENSION

        # Extract extension
        parts = filename.split(".")
        if len(parts) < 2:
            return DEFAULT_EXTENSION

        raw_extension = parts[-1].lower().strip()

        if not raw_extension:
            return DEFAULT_EXTENSION

        # Normalize extension (e.g., jpeg -> jpg)
        normalized_extension = EXTENSION_MAPPING.get(raw_extension, raw_extension)

        # Return normalized extension if supported, otherwise default
        if normalized_extension in SUPPORTED_EXTENSIONS:
            return normalized_extension

        return DEFAULT_EXTENSION

    except (ValueError, AttributeError):
        # If URL parsing fails, fall back to simple string manipulation
        return _fallback_extension_extraction(url)


def _fallback_extension_extraction(url: str) -> FileExtension:
    """Fallback method for extension extraction using simple string operations.

    Args:
        url: URL string

    Returns:
        File extension or default
    """
    try:
        # Extract the part of the URL after the last slash
        filename_part = url.split("/")[-1]
        # Remove query parameters from the filename part before splitting by '.'
        filename_part = filename_part.split("?")[0]

        parts = filename_part.split(".")
        if len(parts) > 1:
            raw_ext = parts[-1].lower().strip()
            normalized_ext = EXTENSION_MAPPING.get(raw_ext, raw_ext)

            if normalized_ext in SUPPORTED_EXTENSIONS:
                return normalized_ext

        return DEFAULT_EXTENSION

    except (IndexError, AttributeError):
        return DEFAULT_EXTENSION


def get_supported_extensions() -> Dict[str, List[str]]:
    """Get all supported file extensions organized by type.

    Returns:
        Dictionary with 'image' and 'video' keys containing lists of extensions

    Example:
        >>> extensions = get_supported_extensions()
        >>> print(extensions['image'])
        ['jpg', 'png', 'gif', ...]
    """
    return {
        "image": sorted(SUPPORTED_IMAGE_EXTENSIONS),
        "video": sorted(SUPPORTED_VIDEO_EXTENSIONS),
        "all": sorted(SUPPORTED_EXTENSIONS),
    }


def is_supported_extension(extension: str) -> bool:
    """Check if a file extension is supported.

    Args:
        extension: File extension to check (with or without leading dot)

    Returns:
        True if extension is supported

    Raises:
        TypeError: If extension is not a string

    Example:
        >>> is_supported_extension("jpg")
        True
        >>> is_supported_extension(".mp4")
        True
        >>> is_supported_extension("xyz")
        False
    """
    if not isinstance(extension, str):
        raise TypeError(f"Extension must be a string, got {type(extension).__name__}")

    # Remove leading dot if present
    clean_ext = extension.lstrip(".").lower().strip()

    # Normalize extension
    normalized_ext = EXTENSION_MAPPING.get(clean_ext, clean_ext)

    return normalized_ext in SUPPORTED_EXTENSIONS


def get_file_type(extension: str) -> Optional[str]:
    """Get file type category for a given extension.

    Args:
        extension: File extension without dot

    Returns:
        'image', 'video', or None if unsupported

    Example:
        >>> get_file_type('jpg')
        'image'
        >>> get_file_type('mp4')
        'video'
    """
    extension = extension.lower()

    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    elif extension in SUPPORTED_VIDEO_EXTENSIONS:
        return "video"
    else:
        return None


def get_project_root_path() -> str:
    """Get the project root directory path.

    Returns:
        Absolute path to the project root directory

    Example:
        >>> root = get_project_root_path()
        >>> print(root)  # /path/to/project/root
    """
    # Get the directory containing this file (src/utils/)
    current_file_dir = os.path.dirname(os.path.realpath(__file__))
    # Go up two levels: utils -> src -> project_root
    return os.path.dirname(os.path.dirname(current_file_dir))
