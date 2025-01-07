#NOTE: Set the number of parallel workers you want here, more parellel workers greatly increases computation 
#speed, but also requires substantially more computing power

#Ex: on the initial 3 property compset, MAX_WORKERS = 1 took ~20 minutes ,but MAX_WORKERS = 8 took ~4
#MAX_WORKERS = 1 took ~10% of my machine's CPU, while 8 took ~40% when ran from bash
MAX_WORKERS = 8

import logging, os
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
output = hs.get_n_days_from_csv('hwv_compset.csv',30,num_workers = MAX_WORKERS)
output.to_csv(OUTPUT_PATH,index=False,header=False,mode='a')
logging.info(f'Data saved to {OUTPUT_PATH}')