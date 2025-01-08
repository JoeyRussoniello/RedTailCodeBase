#NOTE: Set the number of parallel workers you want here, more parellel workers greatly increases computation 
#speed, but also requires substantially more computing power

#Ex: on the initial 3 property compset, MAX_WORKERS = 1 took ~20 minutes ,but MAX_WORKERS = 8 took ~4
#MAX_WORKERS = 1 took ~10% of my machine's CPU, while 8 took ~40% when ran from bash
MAX_WORKERS = 8

#NOTE: Output settings for local export
CSV_OUTPUT_PATH = 'output.csv'

import logging, os
from dotenv import load_dotenv
import argparse
import pandas as pd
import Functions.hotel_scrape as hs

#Read an argument flag from the script
parser = argparse.ArgumentParser(description = "Proccess some integers.")
parser.add_argument('--save',dest='save_to_csv',action = 'store_true',help = 'Save the file to CSV')
parser.set_defaults(save_to_csv = False)
#Ensure that the python file is running in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
SHAREPOINT_PATH = os.getenv('LOCAL_PATH_TO_SHAREPOINT', None) 
if SHAREPOINT_PATH is None:
    raise FileExistsError('LOCAL_PATH_TO_SHAREPOINT variable not found in .env file, ensure it is configured to save output to excel.')
#Get the final output path
EXCEL_OUTPUT_PATH = os.path.join(
    SHAREPOINT_PATH,
    'Corp-HWV - Revenue Management',
    'HWV',
    'Web Scrapers',
    'Compset_Pricing_Pulls.xlsx'
)
EXCEL_SHEETNAME = 'Data'



#Configure logging to standard
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

#Output results to csv (for static plots using plot_pricing module)
args = parser.parse_args()
if args.save_to_csv:
    output = hs.get_n_days_from_csv('hwv_compset.csv',30,num_workers = MAX_WORKERS)
    output.to_csv(CSV_OUTPUT_PATH,index=False,header=False,mode='a')
    logging.info(f'Data saved to csv file {CSV_OUTPUT_PATH}')
#And to excel (for power BI)
with pd.ExcelWriter(EXCEL_OUTPUT_PATH, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    # Append the new DataFrame to the existing sheet
    output.to_excel(
        writer, 
        sheet_name=EXCEL_SHEETNAME,
        index=False, 
        startrow=writer.sheets[EXCEL_SHEETNAME].max_row,
        header = False,
    )
    logging.info(f"Data saved to excel file - {EXCEL_OUTPUT_PATH}")
