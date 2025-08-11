# Reddit Media Scraper

## RIT Masters Software Engineering Coursework - Completed

A Python application for downloading images and videos from Reddit subreddits, developed as part of academic coursework at Rochester Institute of Technology. This project demonstrates advanced media detection, API integration, and AWS cloud services.

### Academic Context

This project was completed as part of the Masters Software Engineering program at RIT, showcasing:

- **API Integration**: Reddit API authentication and data retrieval
- **Media Processing**: Multi-format media detection and download capabilities
- **Cloud Integration**: AWS S3 storage and web interface implementation
- **Software Engineering Practices**: Type safety, testing, configuration management
- **Error Handling**: Robust exception handling and logging

### Features

- **Multi-format Support**: Downloads images (JPG, PNG, GIF, WebP) and videos (MP4, WebM)
- **Smart Media Detection**: Parses HTML pages using Open Graph tags for embedded media
- **Configurable Settings**: Customizable download behavior through configuration files
- **Robust Error Handling**: Comprehensive error handling and logging system
- **AWS Integration**: Optional S3 upload functionality with web interface
- **Type Safety**: Full type hints and MyPy support for code reliability
- **Testing**: Comprehensive test suite using pytest

### Quick Start

1. **Clone and Setup**:

   ```bash
   git clone https://github.com/ajbarea/reddit-media-scraper.git
   cd reddit-media-scraper
   python -m venv .venv
   .venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Add your Reddit API credentials
   - Configure AWS settings (optional)

3. **Run the Application**:

   ```bash
   python -m src.main
   ```

### Project Structure

```text
reddit-media-scraper/
├── src/                    # Source code modules
│   ├── main.py            # Application entry point
│   ├── config.py          # Configuration management
│   └── utils/             # Utility modules
├── data/                  # Data and downloads
├── frontend/              # Web interface
├── tests/                 # Test suite
├── docs/                  # Detailed documentation
└── requirements.txt       # Dependencies
```

### Technical Implementation

- **Language**: Python 3.13+ with type hints
- **API**: Reddit PRAW (Python Reddit API Wrapper)
- **Cloud**: AWS S3 integration for media storage
- **Testing**: pytest with coverage reporting
- **Code Quality**: MyPy, Black, isort, flake8
- **Configuration**: Environment-based configuration management

### Documentation

Comprehensive documentation including setup instructions, API configuration, and troubleshooting guides can be found in [`docs/README.md`](docs/README.md).

### Development Commands

```bash
# Run tests with coverage
pytest --cov=src

# Type checking
mypy src/

# Code formatting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

---

**Course Completion Status**: ✅ Completed  
**Institution**: Rochester Institute of Technology  
**Program**: Masters Software Engineering  
**Academic Year**: 2025
