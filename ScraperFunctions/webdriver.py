#Webscraper selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

class WebDriver:
    """
    A helpful object to reduce tedious syntax in selenium programming
    
    Notably, allows for a wait parameter to be passed to the find_element_by_id and find_element_by_class methods
    
    Self.memory defaults to a list, but can be specified as a different data structure
    
    <headless>: boolean to determine whether to opened page will be visible
    <memory_structure>: a data structure to hold values for later use
    """
    def __init__(self,headless = False,memory_structure = []):
        service =  Service(executable_path=r"C:\Users\mruss\projects\redtail\chromedriver.exe")
        if not headless:
            self.driver = webdriver.Chrome(service=service)
        else:
            options = Options()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
            self.driver = webdriver.Chrome(service=service,options= options)
        self.memory = memory_structure
    
    #Allows for the use of the 'with' statement
    def __enter__(self):
        return self
    def __exit__(self,exception_type, exception_value, traceback):
        self.close()
        if exception_type is not None:
            traceback.print_exception(exception_type, exception_value, traceback)
        return True
    
    def get(self,url):
        self.driver.get(url)
    
    def get_current_link(self):
        return self.driver.current_url
    
    def find_element_by_id(self,id,wait = None):
        if wait:
            WebDriverWait(self.driver, wait).until(EC.presence_of_element_located((By.ID, id)))
        return self.driver.find_element(By.ID,id)
    
    def find_element_by_css(self,class_name,wait = False):
        if wait:
            WebDriverWait(self.driver, wait).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        return self.driver.find_element(By.CSS_SELECTOR,class_name)
    
    def find_elements_by_id(self,id,wait = None):
        if wait:
            WebDriverWait(self.driver, wait).until(EC.presence_of_element_located((By.ID, id)))
        return self.driver.find_elements(By.ID,id)
    
    def find_elements_by_css(self,class_name,wait = None):
        if wait:
            WebDriverWait(self.driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, class_name)))
        return self.driver.find_elements(By.CLASS_NAME,class_name)
    
    def hold_values(self,values):
        self.memory.append(values)
    
    def get_memory(self):
        return self.memory

    def close(self):
        self.driver.quit()
        logging.info("WebDriver Closed")
    