from urllib.request import urlopen
from calendar import Calendar, monthrange
from datetime import datetime, timedelta
import re
import pandas as pd
from email_sender import send_email
from tqdm import tqdm

def scrapper(target_month, duration):
    current_year = datetime.date.today().year
    month_cal = list(Calendar().itermonthdates(current_year, target_month))
    results = {}
    
    for date in tqdm(month_cal):
        start_day = date.day
        start_month = date.month
        n_days = monthrange(current_year, start_month)[1]

        if start_day + duration > n_days:
            end_day = -(n_days - start_day - duration)
            end_month = start_month + 1
        else:
            end_day = start_day + duration
            end_month = start_month

        #print(f"Start Date: {start_day}. Start Month:{start_month}. End Day:{end_day}. End Month: {end_month}")

        url = f"https://vacancesessipit.com/en/search/?start_date={start_month}%2F{start_day}%2F{current_year}&end_date={end_month}%2F{end_day}%2F{current_year}&tabs=terrain-de-camping&sortby=price&emplacement%5B%5D=mer-et-monde&equipment_type=0&longueur_type=0&equipment_services=0&equipment_damperage=0&services%5B%5D=vue-sur-le-fleuve"
        date_key = f"{start_day}/{start_month}-{end_day}/{end_month}"
        # urlopen will get an encoded HTTP response
        page = urlopen(url)

        # The read method will get a sequence of bytes that represents the source code of the website
        # The decode method will decode the response using utf-8 encoding 
        html = page.read().decode("utf-8")

        # Uses the RegEx to find a specified tag
        # The * character stands for 0 or any instance of the character before. "ab*c" will find strings starting with a, ending with c, with b or not in between
        # The . character stands for any character. "a.c" will find any strings starting with a, ending with c and only ONE character in between
        # The .* stands for a repetition of any character. "a.*b" will find strings starting with a, ending with c, and any repetition of characters in between
        name_pattern = '<h2 class="std_card--title">.*</h2>'
        price_pattern = '<div class="std_card--price-p">.*</div>'

        campsite_names = re.findall(name_pattern, html)
        campsite_prices = re.findall(price_pattern, html)

        data_dict = {}

        # Extract the campsite name and price from the matching strings and assigns values to a dictionary
        for i in range(len(campsite_names)):
            i_start = campsite_names[i].find(">") + 1
            i_end = campsite_names[i].find("</")
            key = campsite_names[i][i_start:i_end]
    
            i_start = campsite_prices[i].find(">") + 1
            i_end = campsite_prices[i].find("$")
            value = "$" + campsite_prices[i][i_start:i_end]
    
            data_dict[key] = value
            results[date_key] = data_dict
            
    df = pd.DataFrame.from_dict(results)
    df.to_csv("available_days.csv")

scrapper(9,2)
send_email("available_days.csv")