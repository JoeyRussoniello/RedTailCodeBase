import re
from datetime import datetime,timedelta
from io import StringIO
from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

def expand_df(df1,df2):
    return df2 if df1.empty else pd.concat([df1,df2])
def update_booking_dates(url, checkin_date, checkout_date,):
    """
    Update the checkin and checkout dates in the given booking.com URL.

    Args:
    url (str): The original URL.
    checkin_date (str): The new check-in date in YYYY-MM-DD format.
    checkout_date (str): The new check-out date in YYYY-MM-DD format.

    Returns:
    str: The updated URL with new check-in and check-out dates.
    """
    url = re.sub(r'checkin=\d{4}-\d{2}-\d{2}', f'checkin={checkin_date}', url)
    url = re.sub(r'checkout=\d{4}-\d{2}-\d{2}', f'checkout={checkout_date}', url)
    return url
def is_correct_table(html_table_string):
    #Convert into a string IO object
    str_table = StringIO(str(html_table_string))
    #Read the table into a pandas dataframe
    df = pd.read_html(str_table)[0]
    #Check if the table has the correct columns
    cols = df.columns
    return "Today's price" in cols
def extract_table(target_url,date):
    resp = requests.get(target_url, headers = headers)
    if resp.status_code != 200:
        logging.warning(f'Response status: {resp.status_code}')
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.find_all('table')
    rating = soup.find('div',class_ = 'ac4a7896c7').text.strip().split(' ')[1]
    prop = soup.find('h2',class_ = 'd2fee87262').text.strip()
    
    df = pd.DataFrame()
    for table in tables:
        if is_correct_table(table):
            df = pd.read_html(StringIO(str(table)))[0]
            df["Rating"] = rating
            df['Date'] = date
            df['Competitor'] = prop
            break
    
    if df.empty:
        logging.warning("No valid table found, likely sold out")
        return 
    else:
        return df
def find_type_name(df):
    #It's possible to get values like "room type" or "apartment type", this accounts for that variance
    headers = df.columns
    for header in headers:
        if "type" in header.lower():
            return header

def get_room_name(txt):
    #Regex to get the words before the first digit
    pattern = r'^\D*'
    s = re.match(pattern,txt).group().strip()
    if 'Only' in s:
        s = s.partition("Only")[0].strip()
    return s

def clean_df(df):
    if df is None or df.empty:
        return
    #apply functions to clean df
    
    #Fix the structure of "Max Guests: 4" => 4
    guests = df["Number of guests"].apply(lambda x: x.split(": ")[1])

    
    pattern = r'(\d+)' #Get the first number from the string
    prices = df["Today's price"].apply(lambda x: re.search(pattern,x).group(0))
    
    #Adjust "Room Type" or "Apartment Type" to be consistent
    type_name = find_type_name(df)
    room_type = df[type_name].apply(get_room_name)
    
    rating = df['Rating']
    date = df['Date']
    
    new_df = pd.DataFrame([room_type,guests,prices,rating,date]).T
    new_df.columns = ['Room Type','Guests','Price','Rating','Check-in Date']
    new_df['Report Date'] = datetime.today().strftime('%m-%d-%Y')
    return new_df
def get_data(url_structure,days_out):
    checkin_date = (today + timedelta(days = days_out)).strftime('%Y-%m-%d')
    checkout_date = (today + timedelta(days = days_out + 1)).strftime('%Y-%m-%d')
    new_url = update_booking_dates(url_structure,checkin_date,checkout_date)
    logging.info(f'Gathering data for: {checkin_date}')
    df = extract_table(new_url,checkin_date)
    cleaned = clean_df(df)
    return cleaned
def get_month_out(url_structure,hwv_prop,competitor):
    df = pd.DataFrame()
    for i in range(1,31):
        df = expand_df(df,get_data(url_structure,i))
    df['HWV Property'] = hwv_prop
    df['Competitor'] = competitor
    return df


#Headers for requests to reduce likelihood of response termination
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
today = datetime.today()

input_df = pd.read_csv('hwv_compset.csv')
output = pd.DataFrame()
logging.info(f"Initializing data pull for: {today.strftime('%m-%d-%Y')}")
for _, row in input_df.iterrows():
    hwv_prop = row['HWV Prop']
    competitor = row['Competitor']
    url_structure = row['URL Structure']
    logging.info(f"Initializing Search for: {hwv_prop} - {competitor}")
    output = expand_df(output,get_month_out(url_structure,hwv_prop,competitor))

OUTPUT_PATH = 'output.csv'
output.to_csv(OUTPUT_PATH,index=False,header=False,mode='a')
logging.info(f'Data saved to {OUTPUT_PATH}')