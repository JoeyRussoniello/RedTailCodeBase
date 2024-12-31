import os, sys, requests, logging #Standard Imports
from io import StringIO #For reading HTML tables
from datetime import datetime, timedelta #For date manipulation
import pandas as pd #Reading HTML tables and exporting to csv
from bs4 import BeautifulSoup #For parsing HTML

#Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

#Add the parent directory to the path so that the modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ScraperFunctions.update_chromedriver import update_driver
from ScraperFunctions.webdriver import WebDriver

input_df = pd.read_csv("wunderground.csv") #Read the input file

#update_driver('win64') #Update the chromedriver

# Get weather data for one property
def get_weather(driver,area,url,formatted_date):
    driver.get(url)
    soup = driver.get_soup()
    tables = soup.find_all('table')
    table_html = str(tables[1])  # Convert the first table to a string
    df = pd.read_html(StringIO(table_html))[0]  # Read the HTML table into a DataFrame
    df.dropna(axis=0,how='all',inplace=True) #Drop the extra NULL rows
    #Insert area name and report date
    df.insert(0,'Area',area) 
    df.insert(1,'Date',formatted_date)
    return df

#Get weather data for all input properties for the given date
def get_weather_for_date(driver,date):
    url_date = date.strftime("%Y-%m-%d")
    formatted_date = date.strftime("%m/%d/%Y")
    df = pd.DataFrame()
    for (_, row) in input_df.iterrows():
        area = row['Location']
        url = row['Url Header'] + url_date #Cocatenate the url header with the date
        try:
            weather_df = get_weather(driver,area,url,formatted_date)
        except IndexError:
            logging.error(f"No tables found on page {url}, continuing to next prop")
            continue
        #Concatenate the dataframes
        df = weather_df if df.empty else pd.concat([df,weather_df])
        logging.info(f"Retrieved Weather Data for: {area} - {url_date}")
    return df

def get_n_days_weather(driver,n_days,starting_date):
    """Get weather data for n preivious data starting from starting_date

    Args:
        driver (Webdriver): a WebDriver object
        n_days (int): Number of days to scrape data for 
        starting_date (datetime): A datetime date
    """
    date = starting_date
    for i in range(n_days):
        date = date - timedelta(days=1)
        df = get_weather_for_date(driver,date)
        
        df.to_csv("wunderground_output.csv",index=False,mode='a',header=False)
        logging.info("Saved {date.strftime('%m/%d/%Y')} to wunderground_output.csv")

report_date = datetime.now() - timedelta(days=1) #Get the date of the previous day

with WebDriver(headless = True,memory_structure = None) as driver:
    df = get_weather_for_date(driver,report_date)
    df.to_csv('wunderground_output.csv',index=False,mode='a',header = False)