from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import requests
from readability import Document

# this file is a test file and notes file on news scraping
# new todo for lewis --- make exit browser on end of scroll, or option to reuse browser to go to next link



# todo for lewis (unfinished list of all feeds on uk.finance.yahoo.com)
# scrape https://uk.finance.yahoo.com/
# scrape https://uk.finance.yahoo.com/topic/news/

# scrape https://uk.finance.yahoo.com/world-indices/

# scrape https://uk.finance.yahoo.com/topic/bank-of-england/
# scrape https://uk.finance.yahoo.com/topic/saving-spending/
# scrape https://uk.finance.yahoo.com/topic/small-business/
# scrape https://uk.finance.yahoo.com/topic/property/
# scrape https://uk.yahoo.com/topics/ipo-watch/
# scrape https://uk.finance.yahoo.com/work-management/
# scrape https://uk.finance.yahoo.com/industries/autos_transportation/  # could include table

# todo look at finance.yahoo.com/ and see if there is anything else that could be scraped


# todo realisation could make a webcrawler and webscraper, detects all news on a page, checks uniqueness (0,1)
# todo then checks if the news is relevant with AI
# todo then appends link to list to be reviewed by a human
# todo finally we have big long list of news websites that we can use in hydrant


# https://stackoverflow.com/questions/22702277/crawl-site-that-has-infinite-scrolling-using-python
# https://stackoverflow.com/questions/69046183/how-do-i-scrape-a-website-with-an-infinite-scroller
# https://csnotes.medium.com/web-scraping-infinite-scrolling-with-selenium-97f820d2e506
# https://duckduckgo.com/?q=python+how+to+webscrape+an+infinite+scroll+webpage&atb=v338-1&ia=web

default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}

blacklist = set([])

class NewsScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)

    def scrape_site_for_links(self, site_url: str, scroll_time: float):
        self.browser.get(site_url)
        time.sleep(1)
        while scroll_time > 0:
            self.browser.find_element(By.XPATH, "//body").send_keys(Keys.END)
            time.sleep(1)
            scroll_time -= 1

        links = BeautifulSoup(self.browser.page_source, "html.parser").find_all("a")

        # Get links out of content
        url_list = []
        for a_tag in links:
            try:
                url = a_tag["href"]
                if not len(url) < 2:
                    if not url.startswith("https"):
                        url_list.append(f"{site_url[:-1]}{url}")
                    else:
                        url_list.append(url)
            except KeyError:
                pass
        return url_list

    def close(self):
        self.browser.quit()


class YahooFinanceNewsScraper(NewsScraper):
    acceptedConsent = False

    def __init__(self):
        super().__init__()

    def accept_consent_cookies(self, site_url: str):
        self.browser.get(site_url)
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//button[@value='agree']").click()
        self.acceptedConsent = True

    def scrape_site_for_links(self, site_url: str, scroll_time: float):
        if not self.acceptedConsent:
            self.accept_consent_cookies(site_url)

        super().scrape_site_for_links(site_url, scroll_time)


def get_article_summary(url) -> str:
    response = requests.get(url, headers=default_headers)
    summary_html = Document(response.content).summary()
    soup = BeautifulSoup(summary_html, "html.parser")
    return clean_text(soup.get_text())


def clean_text(text):
    """
    Takes a string, performs several cleaning operations on it and removes any occurrences of the blacklist
    """
    text = re.sub(r'\n+', '\n', text)
    stripped_lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(stripped_lines)
    text = re.sub(r'\s+', ' ', text)
    for item in blacklist:
        text = text.replace(item, "")
    return text


def parse_blacklist(path):
    global blacklist
    # Read the entire content of the file
    file = open(path, "r")
    content = file.read()
    blacklist = sorted(re.findall(r'\"(.*?)\"', content), key=len, reverse=True)


# cnn = NewsScraper()
# print(cnn.scrape_site_for_links("https://edition.cnn.com/", 2))
# cnn.close()
# yahoo = YahooFinanceNewsScraper()
# yahoo.scrape_site_for_links("https://uk.finance.yahoo.com/topic/news/", 5)
# yahoo.close()

parse_blacklist("HydrantData/blacklist.txt")
print(get_article_summary("https://uk.finance.yahoo.com/news/live-ftse-european-stocks-us-inflation-figures-091031074.html"))
#print(get_article_summary("https://news.sky.com/story/bolton-vs-cheltenham-league-one-match-postponed-after-medical-emergency-in-crowd-13047434"))
