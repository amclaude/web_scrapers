import re
import time
import os
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup



def setup_webdriver():

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  
    
    driver = webdriver.Chrome()
    return driver

def navigate_to_individual_search(driver):
    try:
    
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'flex')]/li"))
        )
        logging.info("Search tabs are loaded.")

        # Locate the 'Individual' tab by its text
        individual_tab = driver.find_element(By.XPATH, "//li[contains(., 'Individual')]")
        individual_tab.click()
        time.sleep(3) 
    except Exception as e:
        print(e)
        driver.quit()
       
def perform_crd_search(driver, crd_no):
        # Input box 2
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Firm Name or CRD/SEC# (optional)']"))
        )
        search_input.clear()  
        search_input.send_keys(crd_no) 
        # Search btn
        search_button = driver.find_element(By.XPATH, "//button[@aria-label='IndividualSearch']")
        search_button.click()
        time.sleep(5)  
        
        

def scrape_profile_links(driver):
    try:
        # Wait for the results element to be visible before extracting the data
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//bc-search-results-page"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Removed the original code here, since it doesn't work since each profile card doesn't contains the link to profile individual details
        # Since the url format look like this "https://brokercheck.finra.org/individual/summary/1979011" we can just directly get all crd no. and create the url
        # This line will find and select all the crd no. present on the page since the default number of profiles per page is 12 we should get 12 crd nos
        crd_nos = soup.select("investor-tools-individual-search-result-template span:-soup-contains('CRD#:') + *")

        # Build the url
        base_url = "https://brokercheck.finra.org/individual/summary/"
        # Add the base url for each extracted crd nos.
        profile_links = [base_url + no.text.strip() for no in crd_nos]

        print("Found new profiles!")
        
        return profile_links
    except Exception as e:
        print(e)
        return []

def go_to_next_page(driver):
    try:
        # Removed the original code here since finding the element and directly clicking it with .click() method produces "Element not interactable" error
        # But for some reason using waiting and clicking the next button using javascript works.
        # Check if there is a next button
        is_disabled = driver.execute_script("""
            var button = document.querySelector("investor-tools-pager div div:nth-child(4) button");
            if (button) { 
                return button.disabled; 
            } else {
                return false;
            }
        """)
        if not is_disabled:
            # Wait time to fully load the element to the DOM
            time.sleep(5)
            # Click the elements
            driver.execute_script('document.querySelector("investor-tools-pager div div:nth-child(4) button").click();')
            # Added some wait time so the individual profiles can be loaded in the DOM
            time.sleep(5)
            return True 
        return False
    except Exception as e:
        return False

def scrape_crd(driver, crd_no):
    all_profiles = []
    perform_crd_search(driver, crd_no)
    
    page_count = 1
    while True:
        print(f"Current page: {page_count}")
        profiles = scrape_profile_links(driver)
        all_profiles.extend(profiles)

        has_next = go_to_next_page(driver)
        if not has_next:
            break
        page_count+=1
    print(f"Found a total of {len(all_profiles)} profiles for the search term {crd_no}")
    return all_profiles


def main():
    driver = setup_webdriver()
    try:

        driver.get("https://brokercheck.finra.org/")
        logging.info("Navigated to brokercheck.finra.org")
        time.sleep(5) 

       
        navigate_to_individual_search(driver)
        
        # You can open a list of brokerage and add it here
        crd_search_terms = [
            "100100"
        ]
        all_data = []

        for crd_no in crd_search_terms:
            print(f"Search Term: {crd_no}")
            profile_links = scrape_crd(driver, crd_no)
            # Create the crd Info dictionary
            crd_infos = [{
                "CRD Search Term": crd_no,
                "Profile CRD No.": link.split("/")[-1], # Get the crd no from the profile link
                "Profile URL": link            
            } for link in profile_links]
            # Add the extracted info the all_data list
            all_data.extend(crd_infos)
        print("========= Finished =========")
        print(f"Found a total of {len(all_data)} profiles")
        df = pd.DataFrame(all_data)
        # Create a folder for storage of data
        path = "sample_data"
        # Check if path "sample_data" exists
        if not os.path.exists(path):
            os.mkdir(path)
        
        # Create the filename
        filename = os.path.join(path, "brokercheck_finra_org_output.csv")

        df.to_csv(filename, index=False)

    except Exception as e:
        driver.quit()

if __name__ == "__main__":
    main()