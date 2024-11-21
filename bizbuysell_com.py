# https://www.bizbuysell.com/businesses-for-sale/
import time
import os
import random
import pandas as pd
import json
from fake_useragent import UserAgent
from requests import Session
from selectolax.parser import HTMLParser
from seleniumbase import SB


def parse_listing(content):
    # Initialize HTML Parser
    tree = HTMLParser(content)
    # Create a storage for the listing info
    listing_info = {}

    title = tree.css_first("h1.bfsTitle")
    if title:
        listing_info["Title"] = title.text(strip=True)
    else:

        return None
    # Get the location
    detailed_info = tree.css_first("#ctl00_ctl00_Content_ContentPlaceHolder1_wideProfile_listingDetails_dlDetailedInformation")
    location = detailed_info.css_first("dd")
    # Checks if location is found
    if  location:
        # Splits the location 'San Francisco, CA' -> ['San Francisco', 'CA']
        location_text = location.text(strip=True).split(", ")
        city = location_text[0]
        state = location_text[1] if len(location_text) == 2 else "N/A"   
        # Save the city and location to the listing_info variable     
        listing_info["City"] = city
        listing_info["State"] = state
    # Gets all the 'p' tags for the prices, Since it's a hassle to get each of them
    prices = tree.css("div.financials div div.row p")
    # Loops to every tags
    for price_type in prices:
        # Split it into key, value 'Asking price: $128,000' -> Asking Price, $128,000
        key, value = price_type.text(strip=True).split(":")
        # Save into the listing info variable: listing_info['Asking Price'] = $128,000
        listing_info[key] = value
    return listing_info

def get_business_opportunities(max_page=10):
    # Variable to store the list of urls
    url_list = []
    # To keep track on the number of pages
    page_num = 1
    while True:
        url = "https://www.bizbuysell.com/businesses-for-sale/"
        # if the page num is not equal to 1 add the page number to url for pagination
        if page_num != 1:
            url += f"{page_num}/"
        # Initialize Seleniumbase
        with SB(uc=True, incognito=True) as sb:
            # Open the url
            sb.uc_open_with_reconnect(url, 2)
            sb.wait(2)
            if url != sb.get_current_url():
                break
            # Initialize HTML Parser
            tree = HTMLParser(sb.driver.page_source)
            # Get all the 'a' tags
            url_tags = tree.css("app-listing-diamond a")
            # loops to each found tag
            for tag in url_tags:
                # Check if tag is not None, and 'href' is not in the list, and if the url contains "Business Opportunity"
                if tag and tag.attributes['href'] not in url_list and "Business-Opportunity" in tag.attributes['href']:
                    url_list.append(tag.attributes['href'])
        # Stop the loops if it reaches the specified max page
        if page_num == max_page:
            break
        # Increase the page number
        page_num += 1
    return url_list

        


def main():
    # url = "https://www.bizbuysell.com/Business-Opportunity/vietnamese-restaurant-in-northern-virginia/2149488/"
    # Initialize the Seleniumbase
    with SB(uc=True, incognito=True) as sb:
        all_data = []
        # Get all the business url
        business_oppurtunities = get_business_opportunities(max_page=1)
        print(f"Found {len(business_oppurtunities)} business oppurtunities!")
        # Loops through all the businesses
        for business_url in business_oppurtunities:
            print(business_url)
            # Open the url
            sb.uc_open_with_reconnect(business_url, 2)
            # Parse the content 
            result = parse_listing(sb.driver.page_source)
            # If result is not None Append it
            if result:
                all_data.append(result)
                time.sleep(random.uniform(2, 3))
        print(f"Found a total of {len(all_data)} profiles")
        df = pd.DataFrame(all_data)
        # Create a folder for storage of data
        path = "sample_data"
        # Check if path "sample_data" exists
        if not os.path.exists(path):
            os.mkdir(path)
          
        # Create the filename
        filename = os.path.join(path, "bizbuysell_com_output.csv")

        # na_rep="N/A" replaces the blank items with 'N/A'
        df.to_csv(filename,na_rep="N/A", index=False)
            


if __name__ == "__main__":
    main()
    