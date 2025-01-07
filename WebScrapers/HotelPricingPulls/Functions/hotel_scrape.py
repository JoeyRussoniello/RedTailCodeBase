import re
from datetime import datetime,timedelta
from io import StringIO
from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging
import concurrent.futures

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

#Headers for requests to reduce likelihood of response termination
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
today = datetime.today()

def expand_df(df1,df2):
    """runs pd.concat safelly to control for empty dataframes

    Args:
        df1 (pd.DataFrame|None): First Dataframe, possibly null
        df2 (pd.Dataframe|None): Second Dataframe

    Returns:
        pd.DataFrame|None: Concatenated Dataframe
    """
    if df1 is None or df1.empty:
        return df2
    else:
        return pd.concat([df1,df2])

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
    """The main function of the module, gets the table of pricing data (uncleaned) from
    a website given a target url. Uses the mozilla agent from headers, with some other
    settings to decrease the likelihood of request termination.

    Args:
        target_url (str): The link that will be used to send an HTML request
        date (str): formatted date to be inserted into the table

    Returns:
        pd.DataFrame|None: Either the resulting table if one is found, otherwise returns None
    """
    resp = requests.get(target_url, headers = headers)
    if resp.status_code != 200:
        logging.warning(f'Response status: {resp.status_code}')
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.find_all('table')
    
    #The if split forces not to crash if no rating div is found (usually on bad HTML loads)
    rating_div = soup.find('div',class_ = 'ac4a7896c7')
    if rating_div is None:
        rating = None
    else:
        rating = rating_div.text.strip().split(' ')[1]

    df = pd.DataFrame()
    for table in tables:
        if is_correct_table(table):
            df = pd.read_html(StringIO(str(table)))[0]
            df["Rating"] = rating
            df['Date'] = date
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
def get_data(url_structure,days_out, prop):
    checkin_date = (today + timedelta(days = days_out)).strftime('%Y-%m-%d')
    checkout_date = (today + timedelta(days = days_out + 1)).strftime('%Y-%m-%d')
    new_url = update_booking_dates(url_structure,checkin_date,checkout_date)
    logging.info(f'Gathering data for: {prop}, {checkin_date}')
    df = extract_table(new_url,checkin_date)
    cleaned = clean_df(df)
    return cleaned
def get_n_days_out(url_structure,hwv_prop,competitor,n):
    df = pd.DataFrame()
    for i in range(1,n+1):
        try:
            new_df = get_data(url_structure,i,competitor)
            df = expand_df(df,new_df)
        except requests.exceptions.ConnectionError or requests.exceptions.ChunkedEncodingError:
            logging.error("Request failed, continuing with iteration.")
            continue
    df['HWV Property'] = hwv_prop
    df['Competitor'] = competitor
    return df
def get_n_days_from_csv(input_path, n, num_workers=5):
    output = pd.DataFrame()
    memo = {}
    logging.info(f"Initializing data pull for: {today.strftime('%m-%d-%Y')}")
    input_df = pd.read_csv(input_path)

    def process_row(row):
        hwv_prop = row['HWV Prop']
        competitor = row['Competitor']
        url_structure = row['URL Structure']
        logging.info(f"Initializing Search for: {hwv_prop} - {competitor}")

        if competitor in memo:
            logging.info(f"Using memoized data for competitor: {competitor}")
            return memo[competitor]
        else:
            df = get_n_days_out(url_structure, hwv_prop, competitor, n)
            memo[competitor] = df
            return df

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_row, row) for _, row in input_df.iterrows()]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                output = expand_df(output, result)
            except Exception as e:
                logging.error(f"Error processing row: {e}")

    return output