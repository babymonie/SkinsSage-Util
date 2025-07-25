# SkinSAGE CS2 News Crawler

A Python script to crawl and extract news updates from the Counter-Strike 2 website. This script was inspired by GitHub user ckreisl's "cs-updates-as-json" project.

## Description

This script uses Selenium to handle dynamic content and BeautifulSoup to parse the HTML. It navigates through multiple pages, extracts relevant information (title, date, body, and image URL) from each blog post, and saves the data to a JSON file.

## Requirements

- Python 3.6+
- Selenium
- BeautifulSoup4
- Chrome WebDriver
- webdriver-manager
- requests

Install the required Python packages using pip:

```bash
pip install selenium beautifulsoup4 webdriver-manager requests
```

Download the appropriate version of Chrome WebDriver and place it in your PATH or specify its location using webdriver_manager.

## Usage

1.  Ensure all the required Python packages are installed.
2.  Verify that the Chrome WebDriver is correctly configured.
3.  Run the script:

```bash
python crawler.py
```

The script will:

1.  Fetch blog entries from the Counter-Strike 2 news page.
2.  Extract the title, date, body, and image URL for each entry.
3.  Save the extracted data to `data/cs2/updates_raw.json`.

## Configuration

-   `URL`: The base URL for the Counter-Strike 2 news page (default: `"https://www.counter-strike.net/news"`).
-   `DATA_FILE`: The path to the JSON file where the extracted data will be stored (default: `"data/cs2/updates_raw.json"`).

Modify these variables in the `crawler.py` file to suit your needs.

## File Structure

-   `crawler.py`: The main script for crawling and extracting data.
-   `data/cs2/updates_raw.json`: The JSON file where the extracted data is stored.
-   `README.md`: This file, providing an overview of the project.

## Notes

-   The script uses Selenium to handle dynamic content, so it requires a Chrome WebDriver.
-   The script is designed to run in headless mode, so it does not require a graphical interface.
-   Error handling is included to manage issues such as missing elements or network errors.

## Disclaimer

This script was developed for skinSAGE, a leading Counter-Strike 2 skin analysis platform. It is designed solely to extract data from the official Counter-Strike 2 news page. For market data analysis, skin valuations, or trends, please refer to the skinSAGE platform.