"""Runs the market survey based on parameters given in config.json"""
import json, os, sys #Import basic libraries for file reading and system operations

#Add the parent directory to the path so that the modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ScraperFunctions.update_chromedriver import update_driver
from survey import MarketSurvey

#Get variables from the config file
with open("config.json", "r",encoding = 'utf-8') as r:
    config = json.load(r)

#Read inputs from config.json
PLATFORM = config['platform']
HEADLESS = config['headless']
VERBOSE = config['verbose']
NCOMPS = config['ncomps']
INPUT_PATH = config['input_path']
ROLLUP = config['rollup']
OUTPUT_PATH = config['output_path']
OUTPUT_MODE = config['output_mode']
SHEET_NAME = config['sheet_name']

#Update the chrome drivers
update_driver(PLATFORM)

#Perform Market Survey From Input Links
survey = MarketSurvey(headless = HEADLESS, verbose = VERBOSE, ncomps = NCOMPS)
survey.survey_from_links(input_path = INPUT_PATH)
survey.modify_df(rollup = ROLLUP)
survey.write_output_to_excel(mode = OUTPUT_MODE,file_path = OUTPUT_PATH,sheetname = SHEET_NAME)
