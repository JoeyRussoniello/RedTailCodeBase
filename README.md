# Red Tail Data Engineering

## Overview
The Redtail project is designed to facilitate web scraping using Selenium and BeautifulSoup. The project is currently organized into two main directories: `ScraperFunctions` and `WebScrapers`, but will change as more reusable classes develop.

## Directory Structure

```
redtail/
├── ScraperFunctions/
│   ├── __init__.py
│   ├── webdriver.py
│   └── update_chromedriver.py
├── WebScrapers/
│   ├── MarketSurvey/
│   ├── WeatherData/
|   ├── HotelPricingPulls/
├── README.md
├── chromedriver.exe
└── requirements.txt
```

### ScraperFunctions
This directory contains utility functions and classes that are used to facilitate web scraping tasks. The main components include:

- `webdriver.py`: Contains the `WebDriver` class, which simplifies the use of Selenium WebDriver for web scraping. It includes methods for navigating web pages, finding elements, and extracting content using BeautifulSoup.

### WebScrapers
This directory contains individual web scraper modules, each designed to scrape data from specific websites. The main components include:

- `MarketSurvey/main.py`: A module designed to scrape competitor data from *apartments.com*. It uses the `update_chromedriver` function from `update_chromedriver` to dynamically update the main chromedriver.exe file with each run, ensuring it stays functional dynamically
- `WeatherData`: A module designed to scrape data from various weather website. It leverages the `WebDriver` class for web scraping tasks using Selenium and bs4.
- `...`: Additional scraper modules for other websites.

## Usage
To easily download all repo code onto your local machine use:
```git
git clone https://github.com/JoeyRussoniello/RedTailCodeBase
cd RedTailCodeBase
```

To use the web scrapers, you need to have the required dependencies installed. You can install them using the `requirements.txt` file:
```sh
pip install -r requirements.txt
```

Each web scraper module can be run individually, and scheduled as tasks. For example, to run `MarketSurvey`, use the following command:

```sh
cd WebScrapers/MarketSurvey
python python.py
```

#### **NOTE: All webscrapers were developed on a windows OS, and some have `\\` style paths left in the code. These are being gradually replaced with safer os.path.joins, but at the moment, some webscrapers may not function out-of-box on UNIX systems**

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact
For any questions or inquiries, please contact the project maintainer at [jrussoniello@highwaywest.com](mailto:jrussoniello@highwaywest.com).