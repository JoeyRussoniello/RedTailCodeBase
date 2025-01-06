#Import necessary libraries
import sys, os, time, logging #Standard imports
from datetime import datetime #For getting the current year
import pandas as pd #For writing csv files, and parsing a list of dictionaries
from selenium.webdriver.common.keys import Keys #To send 

#Ensure we are in the correct working directory, and get the scraper functions out of the parent directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

#Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

#Take user inputs in a non-programmer friendly way to configure program setup
def int_input(str_prompt):
    while True:
        try:
            var = int(input(str_prompt))
            if var > 0:
                return var
            else:
                logging.info("Input must be positive.")
        except ValueError:
            logging.error("Invalid Input. Please enter a number")
while True:
    TARGET_AREA = input("Enter the target area (in format City, State): ")
    if ',' in TARGET_AREA:
        CSV_LABEL = TARGET_AREA.split(',')[0]
        break
    else:
        logging.error("No Comma found in Area Name")

N_COMPS = int_input("How many competitors would you like to find?: ")
N_DAYS = int_input("How many days out would you like to gather data for?: ")

while True:
    headless_response = input("Would you like the web-browser to be displayed on your machine? (y/n): ").lower().strip()
    if headless_response not in ['y','n']:
        logging.warning("Answer should either be 'y' or 'n'")
    else:
        HEADLESS = headless_response == 'n' #True results in no web browser dispplay
        break


#Import the custom scraper functions
from ScraperFunctions.webdriver import WebDriver
from ScraperFunctions.update_chromedriver import update_driver
import Functions.hotel_scrape as hs
from Functions.plot_pricing import get_graphs, read_pricing
#Update the chromedriver on import?
update_driver('win64')

def get_starting_point(year):
    return f'https://www.booking.com/searchresults.html?ss=Honolulu&ssne=Honolulu&ssne_untouched=Honolulu&efdco=1&label=gen173nr-1FCAEoggI46AdIM1gEaIgCiAEBmAExuAEXyAEM2AEB6AEB-AECiAIBqAIDuALP0-G7BsACAdICJGQ2M2Y2YTBlLWUxZWQtNDUxNi1hMzdlLTM5NTIwNzkxMmE3ZdgCBeACAQ&aid=304142&lang=en-us&sb=1&src_elem=sb&src=index&dest_id=20030916&dest_type=city&checkin={year + 1}-01-01&checkout={year + 1}-01-02&group_adults=2&no_rooms=1&group_children=0'
def get_link_data(webdriver,url, sleep_time):
    """Gets the competitor description necessary to pass a file to main.py

    Args:
        webdriver (WebDriver): An active WebDriver object
        url (str): The input url of the compeitor (may change when opened)

    Returns:
        (str,str,str): The opened version of the input_link, the hotel name, 
        and hotel address found on booking.com
    """
    #Pass the link to booking.com to ensure validity
    webdriver.get(url)
    #Get the hotel name
    time.sleep(sleep_time) #Wait just a little bit to let the page load and not get stale elements
    hotel_name = webdriver.find_element_by_css("h2.d2fee87262.pp-header__title",wait = 10).text
    hotel_address = webdriver.find_element_by_css("div.a53cbfa6de.f17adf7576").text
    if '\n' in hotel_address:
        hotel_address = hotel_address.partition('\n')[0] 
    new_link = webdriver.get_current_link()
    return new_link,hotel_name, hotel_address

def get_compset(Property_Name,TARGET_AREA,N_COMPS,HEADLESS):
    #Get the current year
    today = datetime.today()
    year = today.year
    starting_point = get_starting_point(year)
    #Initialize a webdriver object that uses a list to track a list of usable booking.com links for competitors
    #with WebDriver(headless = False, memory_structure = pd.DataFrame()) as webdriver:
    with WebDriver(headless = HEADLESS, memory_structure = []) as webdriver:
        webdriver.get(starting_point)

        search_bar = webdriver.find_element_by_id(':rh:',wait = 10)
        #Delete the placeholder text in the search bar
        while search_bar.get_attribute('value') != '':
            search_bar.send_keys(Keys.CONTROL + "a")
            search_bar.send_keys(Keys.DELETE)
            time.sleep(1)
        #Enter the target area into the search bar
        search_bar.send_keys(TARGET_AREA)
        time.sleep(2) #Wait for the keys to load, otherwise it will default to Las Vegas lol
        search_bar.submit()

        time.sleep(5) #Wait 5 seconds to make sure the page loads
        #NOTE: Tracking down the class name, to check for updates doesn't work here, because the launch page will have links as well

        #Get the first N_COMPS hotels
        hotel_links = webdriver.find_elements_by_css('a.a78ca197d0',wait = 10)
        usable_links = [link.get_attribute('href') for link in hotel_links]

        links_seen = set()
        counter = 0
        for link in usable_links:
            if counter == N_COMPS:
                break
            elif link not in links_seen:
                links_seen.add(link)
                new_link,hotel_name, hotel_address = get_link_data(webdriver,link,sleep_time = 5)
                data = {
                    'HWV Prop': Property_Name,
                    'Competitor': hotel_name,
                    'URL Structure': new_link,
                    'Address': hotel_address
                }
                webdriver.hold_values(data)
                counter += 1
            else:
                continue

        #Write the compset to a csv file
        df = pd.DataFrame(webdriver.memory)
        df.to_csv(OUTPUT_FILE,index = False, header = True)
        logging.info(f'Compset written to: {OUTPUT_FILE}')
        return df

#COMPSET PATH FOR READING AND WRITING
OUTPUT_FILE = os.path.join("Acquisitions",CSV_LABEL + "_compset.csv")

#Get the compset for the area specified in above CONSTANTS, uses a selenium browser to input and js render content
df = get_compset(CSV_LABEL,TARGET_AREA,N_COMPS,HEADLESS)

#Scrape the pricing for the compset using bs4 and the requests module
pricing = hs.get_n_days_from_csv(OUTPUT_FILE,N_DAYS)
#Write the pricing to a csv file for future reference
pricing.to_csv(os.path.join("Acquisitions",CSV_LABEL + "_pricing.csv"),index=False,header=True,mode='a')
logging.info(f'Pricing saved to {os.path.join("Acquisitions",CSV_LABEL + "_pricing.csv")}')

#Calculate the graphs for the new compset
get_graphs(read_pricing(pricing),CSV_LABEL,save_graphs = True, display = False, plot_changes = False)
logging.info(f'Graphs saved to Plots Directory')