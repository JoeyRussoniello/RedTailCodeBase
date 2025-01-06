import logging, os
import pandas as pd
import Functions.hotel_scrape as hs

#Ensure that the python file is running in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Configure logging to standard
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

OUTPUT_PATH = 'output.csv'
output = hs.get_n_days_from_csv('hwv_compset.csv',30)
output.to_csv(OUTPUT_PATH,index=False,header=False,mode='a')
logging.info(f'Data saved to {OUTPUT_PATH}')