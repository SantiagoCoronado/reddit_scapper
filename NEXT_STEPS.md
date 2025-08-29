# Next Steps for Reddit Scraper

## IMMEDIATE PRIORITIES

### 1. Input File Format Enhancement
- Remove the requirement for `.json` extension in the input
- Automatically handle file extension
- Add validation for valid filename characters

### 2. JSON File Processing
- Implement file splitting functionality based on:
  - Token count (for LLM processing)
  - Character limit
  - Custom size limits
- Add options for:
  - Maximum file size
  - Naming convention for split files
  - Custom split markers/delimiters

## MID-TERM GOALS

### Web UI Implementation
- Create a web interface using:
  - Frontend: React/Next.js
  - Backend: FastAPI/Flask
- Features to include:
  - Interactive form for search criteria
  - Real-time progress updates
  - Results preview
  - Download options for data in different formats (CSV, Excel)
  - Search history
  - Add search templates/presets
  - I feel lucky
  - Data visualization

## LONG-TERM VISION

### X/Twitter Integration
- Add X/Twitter scraping capabilities
- Features to consider:
  - Hashtag tracking
  - User timeline scraping
  - Engagement metrics
  - Cross-platform analytics
  - Topic correlation between platforms

