
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time
import re

USER_LOGIN = '<YOUR LOGIN>'
USER_PASSWORD = '<YOUR_PASSWORD>'


def get_and_print_profile_info(driver, profile_url):
    driver.get(profile_url)        # this will open the link

    # Extracting data from page with BeautifulSoup
    src = driver.page_source

    # Now using beautiful soup
    soup = BeautifulSoup(src, 'lxml')

    # Extracting the HTML of the complete introduction box
    # that contains the name, company name, and the location
    intro = soup.find('div', {'class': 'pv-text-details__left-panel'})

    #print(intro)

    # In case of an error, try changing the tags used here.
    name_loc = intro.find("h1")

    # Extracting the Name
    name = name_loc.get_text().strip()
    # strip() is used to remove any extra blank spaces

    works_at_loc = intro.find("div", {'class': 'text-body-medium'})

    # this gives us the HTML of the tag in which the Company Name is present
    # Extracting the Company Name
    works_at = works_at_loc.get_text().strip()

    print("Name -->",  name,
          "\nWorks At -->", works_at)

    POSTS_URL_SUFFIX = 'recent-activity/all/'

    time.sleep(0.5)

    # Get current url from browser
    cur_profile_url = driver.current_url
    print(cur_profile_url)

    # Parse posts
    get_and_print_user_posts(driver, cur_profile_url + POSTS_URL_SUFFIX)


def get_and_print_user_posts(driver, posts_url):
    driver.get(posts_url)

    #Simulate scrolling to capture all posts
    SCROLL_PAUSE_TIME = 1.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # We can adjust this number to get more posts
    NUM_SCROLLS = 5

    for i in range(NUM_SCROLLS):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parsing posts
    src = driver.page_source

    # Now using beautiful soup
    soup = BeautifulSoup(src, 'lxml')
    # soup.prettify()

    posts = soup.find_all('li', class_='profile-creator-shared-feed-update__container')
    # print(posts)

    print(f'Number of posts: {len(posts)}')
    for post_src in posts:
        post_text_div = post_src.find('div', {'class': 'feed-shared-update-v2__description-wrapper mr2'})

        # if post_text_div is None:
        #     print(post_src)

        if post_text_div is not None:
            post_text = post_text_div.find('span', {'dir': 'ltr'})
        else:
            post_text = None

        # If post text is found
        if post_text is not None:
            post_text = post_text.get_text().strip()
            print(f'Post text: {post_text}')

        reaction_cnt = post_src.find('span', {'class': 'social-details-social-counts__reactions-count'})

        # If number of reactions is written as text
        # It has different class name
        if reaction_cnt is None:
            reaction_cnt = post_src.find('span', {'class': 'social-details-social-counts__social-proof-text'})

        if reaction_cnt is not None:
            reaction_cnt = reaction_cnt.get_text().strip()
            print(f'Reactions: {reaction_cnt}')

    return




if __name__ == '__main__':
    # start Chrome browser
    caps = DesiredCapabilities().CHROME

    caps['pageLoadStrategy'] = 'eager'

    driver = webdriver.Chrome()

    # Opening linkedIn's login page
    # NOTE: We need to turn of 2 step authentification
    driver.get("https://linkedin.com/uas/login")

    # waiting for the page to load
    time.sleep(3.5)

    # entering username
    username = driver.find_element(By.ID, "username")

    # In case of an error, try changing the element
    # tag used here.

    # Enter Your Email Address
    username.send_keys(USER_LOGIN)

    # entering password
    pword = driver.find_element(By.ID, "password")
    # In case of an error, try changing the element
    # tag used here.

    # Enter Your Password
    pword.send_keys(USER_PASSWORD)

    # Clicking on the log in button
    # Format (syntax) of writing XPath -->
    # //tagname[@attribute='value']
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    ### TEST for parsing page with posts
    # get_and_print_profile_info(driver, 'https://www.linkedin.com/in/mathurin-ache-11004218')

    # exit()

    # Open search page
    driver.get('https://www.linkedin.com/search/results/people/?keywords=data%20scientist&origin=CLUSTER_EXPANSION&sid=1gy')

    profile_urls = []

    NUM_PAGES_TO_PARSE = 12

    # Iterate over pages of search results
    # to collect profile urls
    for i in range(NUM_PAGES_TO_PARSE):
        search_result_links = driver.find_elements(By.CSS_SELECTOR, "div.entity-result__item a.app-aware-link")

        for link in search_result_links:
            href = link.get_attribute("href")
            if 'linkedin.com/in' in href:
                profile_urls.append(href)

        next_button = driver.find_element(By.CLASS_NAME,'artdeco-pagination__button--next')
        next_button.click()
        time.sleep(2)


    profile_urls = list(set(profile_urls))

    print(profile_urls)

    # Parse profile urls
    for profile_url in profile_urls:
        get_and_print_profile_info(driver, profile_url)
        time.sleep(2)

    # close the Chrome browser
    driver.quit()
