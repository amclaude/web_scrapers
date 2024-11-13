# Scraper for https://www.famousbirthdays.com/
import time
import os
import json
from fake_useragent import UserAgent
from requests import Session
from selectolax.parser import HTMLParser

def get_headers():
    # Random headers
    return {
        "User-Agent": UserAgent().random,
        "Referer": "https://www.google.com"
    }

def parse_profile(content):
    # This method parses the profiles found in the site
    # Create a dictionary to store the extracted profile content
    profile = {}
    # Initialize Selectolax parse
    tree = HTMLParser(content)
    # Extracts the full name
    full_name = tree.css_first("h1 span.bio-module__first-name")
    profile["Full name"] = full_name.text().strip()

    # Extracts the profession of the profile
    profession = tree.css_first("p.bio-module__profession a")
    profile["Profession"] = profession.text().strip()
    # Extracts the images/profile in the carousel
    profile_pictures = tree.css("div.profile-pictures-carousel__slide img")
    profile['Profile Pictures'] = []
    # Process each tags and get the src/image link
    for image in profile_pictures:
        # Check if the image has an src attributes else just process the next one on the list
        if image.attributes.get("src"):
            # Append the images
            profile["Profile Pictures"].append(image.attributes.get("src"))
    # Extracts the "div" tag or the container that contains the profile's Birthday, Birth sign, birthplace and age
    attributes = tree.css_first("div.bio-module__person-attributes")
    # Exctracts the attributes base on its position as a children
    birthday = attributes.css_first("p:first-child span:last-child")
    profile["Birthday"] = birthday.text().strip()
    birth_sign = attributes.css_first("p:nth-child(2) span a")
    profile['Birth sign'] = birth_sign.text().strip()
    birth_place = attributes.css_first("p:nth-child(3) span a")
    profile['Birthplace'] = birth_place.text().strip()
    age = attributes.css_first("p:last-child span a")
    profile['Age'] = age.text().strip()
    
    # Extracts the about titles
    about_module = tree.css("div.about div.about-module h2")
    # Extracts the descriptions 
    p_tags = tree.css("div.about div.about-module p")
    # this will work provided that each description tags for each title is sorrounded in one "p" tag
    for idx, title in enumerate(about_module):
        try:
            key = title.text().strip()  
            value = p_tags[idx].text().strip()
            profile[key] = value
        except Exception as e:
            pass
    # Returns the profile
    return profile

def scrape_url(url):
    # Starts the request Session
    session = Session()
    # Get the html of the profile url
    response = session.get(url, headers=get_headers())
    if response:
        # Return the content
        return parse_profile(response.content)
    return None

def main():
    # Just added the list of profiles, From what I checked on the site you can get the list of profiles by searching
    # For example if you search tiktok, you can probably search for tiktokstars with the url:
    # https://www.famousbirthdays.com/profession/tiktokstar.html
    # There are other variations for this url you can check the urls when searching
    urls = [
        "https://www.famousbirthdays.com/people/ashley-barnes-tiktokstar.html",
        "https://www.famousbirthdays.com/people/cinna.html",
        "https://www.famousbirthdays.com/people/salish-matter.html",
        "https://www.famousbirthdays.com/people/harper-zilmer.html"
    ]
    # Storage for each profiles
    all_data = []
    # Loops through each profile
    for url in urls:
        # Use the method to extract the url
        profile = scrape_url(url)
        # Just add the newly extracted data to the lists
        all_data.append(profile)

    # Create a folder for storage of data
    path = "sample_data"
    # Check if path "sample_data" exists
    if not os.path.exists(path):
        os.mkdir(path)
    
    # Create the filename
    filename = os.path.join(path, "famousbirthdays_com_output.json")

    # Save the profiles
    with open(filename, "w") as file:
        file.write(json.dumps(all_data, indent=4))


    
if __name__ == "__main__":
    main()