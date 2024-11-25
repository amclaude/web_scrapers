import os
import json
import urllib.parse
import uuid

import pandas as pd
from requests import Session
from fake_http_header import FakeHttpHeader


def create_form_data(search_term):
    # Random client id
    client_id = str(uuid.uuid4())
    # URL encoded search term
    url_search_term = search_term.lower().replace(" ", "-")
    # Base data dictionary
    data = {
        "actionsHistory": "[]",
        "referrer": f"https://www.drhorton.com/{url_search_term}",
        "analytics": {
            "clientId": client_id,
            "documentLocation": f"https://www.drhorton.com/{url_search_term}",
            "documentReferrer": f"https://www.drhorton.com/{url_search_term}",
            "pageId": ""
        },
        "visitorId": client_id,
        "isGuestUser": "false",
        "aq": "(@fz95xtemplatename67549==\"Community Landing\") (@fid67549<>\"\") ($qf(function:'dist(@fcoordinatesz32xlatitude67549, @fcoordinatesz32xlongitude67549, 27.90688, -84.07391)', fieldName: 'distance')) (@distance<450000)",
        "cq": "(@source==\"Coveo_web_index - 93DrHortonProd\") (@fcoordinatesz32xlatitude67549) (@fz95xlanguage67549==en) (@fz95xlatestversion67549==1)",
        "queryFunctions": "[]",
        "numberOfResults": "5000",
        "fieldsToInclude": [
            "@fcommunitythumbnail67549",
            "@factivationstate67549",
            "@factivationstatehez120x67549",
            "@faddress167549",
            "@famenitylist67549",
            "@famenitylistfordisplay67549",
            "@fbrand67549",
            "@fbrandlogo67549",
            "@fbrandlogoalt67549",
            "@fcallforprice67549",
            "@fcity67549",
            "fcoordinatesz32xlatitude67549",
            "@fcoordinatesz32xlongitude67549",
            "@fid67549",
            "@fismultigen67549",
            "@fmarketingname67549",
            "@fnumberofavailablehomes67549",
            "@fnumberofbathroomsmaz120x67549",
            "@fnumberofbathroomsmin67549",
            "@fnumberofbedroomsmaz120x67549",
            "@fnumberofbedroomsmin67549",
            "@fnumberofgaragesmaz120x67549",
            "@fnumberofgaragesmin67549",
            "@fnumberofstoriesmaz120x67549",
            "@fnumberofstoriesmin67549",
            "@fpricemin67549",
            "@flongprice67549",
            "@fpropertytype67549",
            "fsqftmaz120x67549",
            "@fsqftmin67549",
            "@fstate67549",
            "@fsysuri67549",
            "@furllink67549",
            "@fz122xip67549",
            "@fsalesofficephone67549",
            "fnumberofbathroomsmin67549",
            "@source",
            "@collection",
            "@urihash"
        ],
        "pipeline": "allresults",
        "searchHub": search_term,
    }

    # Correct encoding for `analytics`
    analytics_json = json.dumps(data["analytics"])
    data["analytics"] = analytics_json

    # URL-encode `fieldsToInclude` as a single JSON array
    data["fieldsToInclude"] = json.dumps(data["fieldsToInclude"])

    # URL-encode the entire payload
    encoded_payload = urllib.parse.urlencode(data)
    return encoded_payload

def scrape_data(state):
    url = "https://www.drhorton.com/coveo/rest/search/v2?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7B5E9EEC1C-A72B-4E84-9394-0F6CA1FD5DAA%7D%3Flang%3Den%26amp%3Bver%3D1&siteName=website"
    session = Session()
    response = session.post(url, data=create_form_data(state), headers=FakeHttpHeader().as_header_dict())
    if response.status_code == 200:
        data = response.json()
        base_url = "https://www.drhorton.com"
        return [ {"title": community.get('title'), "url": base_url + community['raw']['furllink67549']} for community in data['results']]
        

def main():
    states_of_america = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
        "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", 
        "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
        "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", 
        "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
        "New Hampshire", "New Jersey", "New Mexico", "New York", 
        "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
        "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
        "West Virginia", "Wisconsin", "Wyoming"
    ]
    # Instead of just specifying one state you can loop through the
    # list of states and one-by-one get the data for each state
    # Example:
    # all_data = list(map(scrape_data, states_of_america))
    # or just use a simple for loop or you can add concurrency if you have proxies to avoid blocking
    results = scrape_data("Florida")
    # Create a folder for storage of data
    path = "sample_data"
    # Check if path "sample_data" exists
    if not os.path.exists(path):
        os.mkdir(path)
    
    # Create the filename
    filename = os.path.join(path, "drhorton_com.csv")

    # Save the profiles
    df = pd.DataFrame(results)
    # na_rep="N/A" replaces the blank items with 'N/A'
    df.to_csv(filename,na_rep="N/A", index=False)
    print(f"Data is saved to path '{filename}'")




if __name__ == "__main__":
    main()
