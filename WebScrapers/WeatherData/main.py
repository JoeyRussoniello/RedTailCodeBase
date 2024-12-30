import requests 
import logging
import re
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

today = datetime.today()
# Format the date as YYYY MM DD
formatted_date = today.strftime("%m/%d/%Y")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

def get_weather(area,url):
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, 'html.parser')
    div = soup.find('div', id='wt-3d') #Find the div with the weather info
    txt  = div.find_all('p')[0].text #The first paragraph contains the weather info
    pattern = r'(.+?)\.(\d+)\s/\s(\d+)' #Regex to split the string
    test = re.match(pattern,txt).groups() #Match the regex
    weather = {
        'Area': area,
        'Weather': test[0],
        'High Temperature (F)': test[1],
        'Low Temperature (F)': test[2],
        'Date': formatted_date
    }
    return weather

_input = pd.read_csv('setup.csv')
output = []
for (index, row) in _input.iterrows():
    try:
        weather = get_weather(row['Location'],row['Url'])
        output.append(weather)
        logging.info(f"Weather data found for {row['Location']}")
    except:
        logging.warning(f"Check url validity: {row['Url']}")
        logging.error(f"Error Gathering Data for {row['Location']}")

df = pd.DataFrame(output)
output_path = 'weather.csv'
df.to_csv(output_path,index=False,mode='a',header=False)
logging.info(f"Data written to {output_path}")