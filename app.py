# %%
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from selenium import webdriver
from pptx import Presentation
from typing import TypedDict
import pdb
import sys
import re
import time 

# %%

REGEX = re.compile("https:\\/\\/www.linkedin.com\\/in\\/[^\\/]+")

# get the urls to scrape
def get_urls() -> list[str]:
    urls = []
    url = " "
    while True:
        url = input("Enter url (leave empty for end): ")
        if REGEX.match(url):
            print("added url")
            urls.append(url)
        elif len(url) > 0:
            print("Url is not valid")
        else:
            break

    return urls


urls = get_urls()

# found no urls
if len(urls) == 0:
    print("no urls found")
    exit()


def setup_driver():
    options = webdriver.ChromeOptions()
    service = Service()
    return webdriver.Chrome(service=service, options=options)


driver = setup_driver()

# %%
def get_url(url):
    driver.get(url)
    print(f"visiting {url}")


def signin():
    input("Press enter when signed in: ")


# %%
class Experience(TypedDict):
    company: str
    roles: list[str]
    dates: list[str]


def scrape_single_exp(element: WebElement):
    title_link_ele = element.find_elements(By.TAG_NAME, "a")[1]
    lines = title_link_ele.text.splitlines()[::2]

    experience: Experience = {
        "company": lines[1].split("·")[0],
        "roles": [lines[0]],
        "dates": [lines[2].split("·")[0]],
    }

    return experience


def scrape_multi_exp(title_element: WebElement, exp_elements: WebElement):
    title_link_ele = title_element.find_elements(By.TAG_NAME, "a")[1]
    # print(title_link_ele.text)
    # print(title_link_ele)
    experience: Experience = {
        "company": title_link_ele.text.splitlines()[0].split("·")[0],
        "roles": [],
        "dates": [],
    }

    for exp_element in exp_elements:
        link_element = exp_element.find_element(By.TAG_NAME, "a")
        lines = link_element.text.splitlines()[::2]
        experience["roles"].append(lines[0])
        experience["dates"].append(lines[1].split("·")[0])

    return experience


def scrape_experience(element: WebElement) -> Experience:
    # find experience start
    # print(element.text[::2])

    edu_div = element.find_element(
        By.XPATH, ".//div[@data-view-name='profile-component-entity']"
    )

    # print(edu_div.text)

    # find multi experience start if it exists
    multi_exps = edu_div.find_elements(
        By.XPATH, ".//div[@data-view-name='profile-component-entity']"
    )
    if len(multi_exps) > 0:
        print(f"found {len(multi_exps)} sub experiences")
        return scrape_multi_exp(edu_div, multi_exps)
    else:
        print(f"found a sub experience")
        return scrape_single_exp(edu_div)


def scrape_experiences() -> list[Experience]:
    # find education section
    section = driver.find_element(By.XPATH, "//section[.//div[@id='experience']]")

    # find education items
    exp_list = section.find_element(By.TAG_NAME, "ul")
    exp_items = exp_list.find_elements(By.XPATH, "./li")

    print(f"found {len(exp_items)} main experiences")
    experiences: list[Experience] = []
    for exp in exp_items:
        experiences.append(scrape_experience(exp))

    return experiences

def print_experiences(experiences:list[Experience]):
    print("\nEXPERIENCES:")
    for exp in experiences:
        print(exp['company'])
        for sub_exp in zip(exp["roles"],exp["dates"]):
            print(sub_exp[0])
            print(sub_exp[1])

        print()

# %%
get_url(urls[0])
signin()


experiences = scrape_experiences()
print_experiences(experiences)

for index in range(1, len(urls)):
    get_url(urls[index])
    print("waiting ten seconds for page load")
    time.sleep(10)
    experiences = scrape_experiences()
    print_experiences(experiences)


# %%
# l = Presentation()

# %%
# driver.get("https://www.linkedin.com/in/jdunphy/")

# %%
hours=3
next_hours=3.5 - 5.0/60


