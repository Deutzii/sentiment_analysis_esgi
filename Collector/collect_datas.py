from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from basic_functions import (
    collect_urls,
    collect_reviews,
    stack_products_list,
    aggregate_urls,
    aggregate_reviews,
    stack_reviews_list,
    retreive_urls,
    save_as_input_file
)

import pandas as pd
import csv
import time
import os

def main():
    # Create list containing lists of product listing urls
    urls = ["https://www.dermstore.com/skin-care.list",
            "https://www.dermstore.com/hair-care.list",
            "https://www.dermstore.com/makeup.list"
            ]

    # Create path
    PATH = Service(os.path.join(os.curdir, 'chromedriver.exe'))

    # Add options to avoid being detected as a bot
    OPTIONS = Options()

    # User agent
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
    OPTIONS.add_argument(f'user-agent={user_agent}')

    # Disable unnecessary functionality causing message error in the console
    OPTIONS.add_argument("--disable-extensions --disable-gpu --disable-dev-shm-usage --disable")
    OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Closing some unnecessary pop-ups
    OPTIONS.add_argument("--no-first-run --no-service-autorun --password-store=basic")

    # Start in full-screen with a defined window size
    OPTIONS.add_argument("window-size=1920,1080")
    OPTIONS.add_argument("start-maximised")

    # Hide some bot related stuff to increase stealthiness
    OPTIONS.add_argument('--disable-blink-features=AutomationControlled')
    OPTIONS.add_experimental_option('useAutomationExtension', False)
    OPTIONS.add_experimental_option("excludeSwitches", ['enable-automation'])

    # Headless
    OPTIONS.add_argument("--headless")

    # Set the driver
    driver = webdriver.Chrome(service=PATH, options=OPTIONS)

    # Collect Urls
    products_list = collect_urls(driver, urls)
    #print(products_list)
    #stack_products_list(products_list)

    print("[LOG] Collecting reviews ..")
    # Collect Reviews
    res = collect_reviews(driver, products_list)

    #print(res)

    # Create dataframe and integrate the datas inside the dataframe
    df = pd.DataFrame([item for sublist in res for item in sublist],
                      columns=['review_url_src', 'review_stars', 'review_title', 'review_thoughts',
                                    'review_author', 'review_date', 'review_verified', 'review_tup',
                                    'review_tdown', 'review_collected_date'])

    # df.to_csv()
    #df.to_csv('input.csv', sep=';', index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)

    save_as_input_file(df)


if __name__ == "__main__":
    main()
            



