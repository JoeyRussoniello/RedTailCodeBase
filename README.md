# Red Tail Data Engineering
# Table of Contents
1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Usage](#usage)
4. [Configuration](#configuration)
    1. [Setting up the `.env` file](#setting-up-the-env-file)
    2. [Configuring a virutal environment](#setting-up-a-virtual-environment)
5. [Contributing](#contributing)
6. [Contact](#contact)

## Overview
The Redtail project is designed to facilitate web scraping using Selenium and BeautifulSoup. The project is currently organized into two main directories: `ScraperFunctions` and `WebScrapers`, but will change as more reusable classes develop.
#### **NOTE: All webscrapers were developed on a windows OS, and some have `\\` style paths left in the code. These are being gradually replaced with safer os.path.joins, but at the moment, some webscrapers may not function out-of-box on UNIX systems**

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

- `webdriver.py`: Contains the `WebDriver` class, which simplifies the use of Selenium WebDriver for web scraping. It includes methods for navigating web pages, finding elements with built-in EC delays, and passing Selenium content to BeautifulSoup.
- `update_chromedriver.py`: Contains the `update_chromedriver` functions, which sends an HTML request, downloading the most recent version of *chromedriver.exe* in place, overwriting the existing chromedriver with the most recent version

### WebScrapers
This directory contains individual web scraper modules, each designed to scrape data from specific websites. The main components include:

- `MarketSurvey/main.py`: A module designed to scrape competitor data from *apartments.com*. It uses the `update_chromedriver` function from `update_chromedriver` to dynamically update the main chromedriver.exe file with each run, ensuring it stays functional dynamically
- `WeatherData`: A module designed to scrape data from various weather website. It leverages the `WebDriver` class for web scraping tasks using Selenium and bs4.
- `HotelPricingPulls`: A module designed to scrape pricing data from *booking.com*. It uses the requests module exclusively, with URL modification to send requests, without needing to render JS-loaded content
- `...`: Additional scraper modules for other websites.

## Usage
To easily download all repo code onto your local machine use:
```git
git clone https://github.com/JoeyRussoniello/RedTailCodeBase
cd RedTailCodeBase
```
Code will not run out-of-the-box unless the dependencies have all been successfully installed, and the `.env` file has properly configured. See [Configuration Instructions](#configuration) for details

Each web scraper module can be run individually, and scheduled as tasks. For example, to run `MarketSurvey`, use the following command:

```sh
cd WebScrapers/MarketSurvey
python main.py
```

## Configuration

### Setting Up the `.env` File

To configure the project, you need to create a `.env` file in the root directory of the project. This file will store environment-specific variables such as paths and credentials. 

#### Example `.env` File

Here is an example of what your `.env` file should look like:

```properties
CHROMEDRIVER_PATH=C:\path\to\your\chromedriver
LOCAL_PATH_TO_SHAREPOINT="C:\Users\youruser\Red Tail Residential\"
```
With an updating path to your chromedriver, and local sharepoint reference instead of the placeholder variable.

Both of these variables must be included in a `.env` file in order for the webscrapers to work properly
1. **CHROMEDRIVER_PATH**: The local path to your downloaded repo. This will tell the programs where to download and update the chromedriver
2. **LOCAL_PATH_TO_SHAREPOINT**: The local path to your Red Tail Residential Sharepoint File. This path is then used to save webscraping outputs to excel files in the comapny sharepoint, instead of just on a local machine.
If these variables are not properly set up, you should get a helpful `FileExists` error from the program that tells you exactly which variable has been incorrectly setup

**Important:** Do not commit your `.env` file to the repository. It should be included in your `.gitignore` file to keep sensitive information secure.

#### Ignoring `.env` with git
Make sure your `.env` file is listed in a `.gitignore` file to prevent it from being committed to the repository. Your `.gitignore` file should include
```properties
.env
.gitignore
.venv/
```
As well as any large output csv files to avoid overpacking the repository.

### Setting Up a Virtual Environment
It is recommended to use a virtual environment to manage dependencies. Follow these steps to create and activate a virtual environment

1. Create a Virtual Environment
```bash 
python -m venv .venv
```
2. Activate the Virtual Environment
- On Windows:
```bash
.\.venv\Scripts\activate
```
- On macOS, linux, and UNIX systems:
```bash
source .venv/bin/activate
```
3. Install Dependencies
With the virtual environment activated, install the required dependencies using the `requirements.txt` file
```bash
pip install -r requirements.txt
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact
For any questions or inquiries, please contact the project maintainer at [jrussoniello@highwaywest.com](mailto:jrussoniello@highwaywest.com).
