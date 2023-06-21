import random
import time
import glob
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import date as dt
import pandas as pd

def check_if_lastPage_exist(driver, css_selector):
    try:
        driver.find_element(By.CSS_SELECTOR, css_selector)
    except:
        print("Last page reached.")
        pass
    return True

def check_if_element_exist(d, className):
    try:
        d.find_element(By.CLASS_NAME, className)
    except:
        return False
    return True


def collect_urls(driver, urls):
    # Define current page
    current_page = 1
    # Create list of lists (url, name, rating_star, rating_nb_reviews, price)
    products_info = []

    print("[LOG] Begin collecting Product URLs.")

    # Iterate all urls
    for url in urls:
        driver.get(url)
        driver.page_source.encode('utf-8')
        time.sleep(random.randint(1, 3))
        try:
            # Reject cookie
            rejectCookieButton = driver.find_element(By.ID, "onetrust-reject-all-handler")
            rejectCookieButton.click()
            print("[LOG] Rejecting Cookies.")
        except:
            pass

        time.sleep(random.randint(1,5))
        #nextpg_css_selector = 'div[class="responsiveProductListPage_bottomPagination-above-description"] nav[class="responsivePaginationPages"] ul[class="responsivePageSelectors"] li button[class*="paginationNavigationButtonNext"]'
        #nextpg_exist = check_if_lastPage_exist(driver, nextpg_css_selector)
        while True:
            try:
                # Scrap each page
                product_cards = driver.find_elements(By.CSS_SELECTOR, 'div[class="productListProducts"] '
                                                                      'ul[class="productListProducts_products"] '
                                                                'li[class*="productListProducts_product"]')
                for product in product_cards:
                    try:
                        url = product.find_element(By.CSS_SELECTOR, 'div[class="productBlock_itemDetails_wrapper"] '
                                                                    'a[class="productBlock_link"]').get_attribute('href')
                    except:
                        pass
                    try:
                        name = product.find_element(By.CSS_SELECTOR, 'div[class="productBlock_itemDetails_wrapper"] '
                                                                     'a[class="productBlock_link"] '
                                                                     'div[class="productBlock_title"] '
                                                                     'h3[class="productBlock_productName"]'
                                                    ).get_attribute('innerText')
                    except:
                        pass
                    try:
                        rating = str(product.find_element(By.CSS_SELECTOR, 'div[class="productBlock_itemDetails_wrapper"] '
                                                                       'span[class="productBlock_rating_container"] '
                                                                       'span[class="productBlock_rating"] '
                                                                       'span[class*="visually-hidden"]'
                                                          ).get_attribute('innerText'))
                        rating_star = rating.split(' ')[0]
                        rating_nb_reviews = rating.split(' ')[2]
                    except:
                        pass
                    try:
                        price = str(product.find_element(By.CSS_SELECTOR, 'div[class="productBlock_itemDetails_wrapper"] '
                                                                      'div[class="productBlock_priceBlockWrapper"] div '
                                                                      'div span[class*="productBlock_priceValue"]'
                                                         ).get_attribute('innerText'))
                    except:
                        pass
                    print((url, name, rating_star, rating_nb_reviews, price))
                    products_info.append((url, name, rating_star, rating_nb_reviews, price))
                print(f"[LOG] Page {current_page} done.")

                # Stop at x page
                if current_page == 5:
                    break
                else:
                    current_page += 1

                try:
                    nextpg = driver.find_element(By.CSS_SELECTOR,
                                                 'div[class="responsiveProductListPage_bottomPagination-above-description"] '
                                                 'nav[class="responsivePaginationPages"] ul[class="responsivePageSelectors"] '
                                                 'li button[class*="paginationNavigationButtonNext"]')
                    nextpg.click()
                    time.sleep(random.randint(1, 5))
                except:
                    print("[LOG] End of product list page.")
                    break
            except:
                assert AssertionError("Error product cards not found")
                break
    # Convert list of lists to a pandas DataFrame
    df = pd.DataFrame(products_info)

    # Drop duplicates from the DataFrame
    unique_df = df.drop_duplicates()

    # Convert the DataFrame back to a list of lists
    aggregated_list = unique_df.values.tolist()
    return aggregated_list


def collect_reviews(driver, products_info):
    res = []
    print("[LOG] Begin collecting datas.")
    for product_info in products_info:

        if int(product_info[3]) > 15:

            current_url = product_info[0]
            driver.get(current_url)
            time.sleep(random.randint(1, 3))
            try:
                rejectCookieButton = driver.find_element(By.ID, "onetrust-reject-all-handler")
                rejectCookieButton.click()
            except:
                pass

            try:
                try:
                    time.sleep(random.randint(1, 5))
                    # See all the reviews page
                    reviewsButton = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "See all reviews"))
                    )
                    reviewsButton.click()
                except:
                    print("[LOG] No reviews button")
                    pass

                # Check if next page exist
                #nextPageExist = check_if_lastPage_exist(driver, 'button[class="athenaProductReviews_paginationNav-next"]')

                while True:
                    try:
                        # Scrap all the information on each page
                        comments = driver.find_elements(By.CLASS_NAME, "athenaProductReviews_review")
                        for comment in comments:
                            try:
                                review_title = comment.find_element(By.CLASS_NAME, "athenaProductReviews_reviewTitle"
                                                                    ).get_attribute('innerText').strip()
                            except:
                                pass
                            try:
                                review_stars = str(comment.find_element(By.CLASS_NAME, "athenaProductReviews_schemaRatingValue"
                                                                        ).get_attribute('innerHTML')).strip()
                            except:
                                pass
                            try:
                                review_thoughts = comment.find_element(By.CLASS_NAME, "athenaProductReviews_reviewContent"
                                                                       ).get_attribute('innerText').strip()
                            except:
                                pass
                            try:
                                review_date_tmp = comment.find_element(By.CLASS_NAME, 'athenaProductReviews_footerDateAndName')
                                review_date = review_date_tmp.find_elements(By.TAG_NAME, "span")[0].get_attribute(
                                    'innerText').strip()
                                review_author = review_date_tmp.find_elements(By.TAG_NAME, "span")[1].get_attribute(
                                    'innerText').strip()
                            except:
                                pass
                            try:
                                review_verified = str(check_if_element_exist(comment, "athenaProductReviews_footerVerified"))
                            except:
                                pass
                            try:
                                thumbsUpTxt = comment.find_element(By.CLASS_NAME, "athenaProductReviews_voteYes"
                                                                   ).get_attribute('innerText').strip()
                                review_tup = thumbsUpTxt[thumbsUpTxt.find('(') + 1:thumbsUpTxt.find(')')]
                            except:
                                pass
                            try:
                                thumbsDownTxt = comment.find_element(By.CLASS_NAME, "athenaProductReviews_voteNo"
                                                                     ).get_attribute('innerText').strip()
                                review_tdown = thumbsDownTxt[thumbsDownTxt.find('(') + 1:thumbsDownTxt.find(')')]
                            except:
                                pass

                            review_url_src = current_url
                            review_collected_date = dt.today().strftime('%Y-%m-%d')
                            res.append((review_url_src, review_stars, review_title, review_thoughts, review_author,
                                        review_date, review_verified, review_tup, review_tdown, review_collected_date))
                            # print("Title: " + title.text + "\nStars: " + stars.get_attribute("innerText") + "\nThoughts: " + thoughts.text + "\nPosted by: " + username.text + "\nOn: " + date.text + "\nVerified Purchase ?: " + str(verified) +"\n\n")
                        try:
                            nextPage = driver.find_element(By.CLASS_NAME, "athenaProductReviews_paginationNav-next")
                            nextPage.click()
                        except:
                            print("[LOG] End of review section page.")
                            break
                    except:
                        pass

            finally:
                # Notify when done
                print("[LOG] Task finished, all reviews on a product have been collected.")
                time.sleep(random.randint(1, 5))
        else:
            pass

    return res


def stack_products_list(products_list):
    url_path = os.path.join(os.curdir, 'urls')
    date_now = str(time.strftime('%Y_%m_%d_%H_%M_%S'))
    url_file_path = os.path.join(url_path, 'url_dump_' + date_now + '.txt')

    with open(url_file_path, 'w') as file:
        for item in products_list:
            file.write(str(item) + '\n')


def aggregate_tuples():
    """Gathers all the text files containing tuples from a specified folder.
    It aggregates them into a single text file.
    """

    print("[LOG] Start the aggregation of the tuples.")

    date_now = str(time.strftime('%Y_%m_%d_%H_%M_%S'))

    # Path to the folder containing the text files
    url_path = os.path.join(os.curdir, 'url')

    # Path to the output text file
    merged_urls_path = os.path.join(os.curdir, 'merged_urls')
    merged_url_res = os.path.join(merged_urls_path, 'merged_urls' + '.txt')

    # List to store the stacked tuples
    stacked_tuples = []

    # Iterate over each text file in the folder
    for file_path in glob.glob(os.path.join(url_path, '*.txt')):
        with open(file_path, 'r') as file:
            # Read each line in the text file
            for line in file:
                # Remove leading/trailing whitespace and newline characters
                line = line.strip()

                # Append the tuple to the stacked_tuples list
                stacked_tuples.append(eval(line))

    # Write the stacked tuples to the output text file
    with open(merged_url_res, 'w') as file:
        for tuple_data in stacked_tuples:
            file.write(str(tuple_data) + '\n')

    print("[LOG] The aggregation of the tuples is finished.")
