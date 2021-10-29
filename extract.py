"""Extract.py
"""
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

executor = ThreadPoolExecutor(10)


class Extract(webdriver.Chrome):
    """Extract"""

    columns = {
        "name": "Name",
        "price": "Price",
        "options": "Vehicle Options",
        "summary": "Vehicle Summary",
    }

    def __init__(self, items: WebElement):

        print("beginning extraction...")

        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("headless")
        super(Extract, self).__init__(options=options)
        self.maximize_window()

        self.items = items
        self.df = pd.DataFrame(columns=self.columns.keys())
        self.extract()

    def extract(self):

        loop = asyncio.get_event_loop()
        for item in self.items:
            self.scrape(item, loop=loop)

        loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))

    def scrape(self, item, *, loop):
        executor = ThreadPoolExecutor(10)
        loop.run_in_executor(executor, self.scraper, item)

    def scraper(self, item):
        url = item.find_element(By.CSS_SELECTOR, ".card a").get_attribute("href")
        self.get(url)
        wrapper = self.find_element(By.CSS_SELECTOR, "#react .buyer .content-wrapper")
        try:
            price = wrapper.find_element(
                By.CSS_SELECTOR, "#header-box .price-box > h2"
            ).text
        except NoSuchElementException:
            price = "SOLD"

        tmp = wrapper.find_elements(
            By.CSS_SELECTOR, "div[class~='vdp-main'] .vdp-content .vdp-top > h1"
        )
        if len(tmp) > 1:
            title = " ".join(tmp[1].get_attribute("innerText").split()[1:])
        else:
            title = " ".join(tmp[0].get_attribute("innerText").split()[1:-2])
        summarries = wrapper.find_elements(
            By.CSS_SELECTOR, "#summary-table:nth-child(1) tbody tr"
        )[1:]
        summary_dict = dict()

        for summary in summarries:
            key = summary.find_element(By.TAG_NAME, "th").text[:-1]
            value = summary.find_element(By.TAG_NAME, "td").text.replace("\n", " ")
            summary_dict.update({key: value})
        try:
            options = (
                wrapper.find_element(By.CSS_SELECTOR, "#options-table")
                .find_element(By.TAG_NAME, "tbody")
                .find_elements(By.TAG_NAME, "tr")[1:]
            )
        except NoSuchElementException:
            options = []

        options_list = list()

        flag = False
        for option in options:

            try:
                if option.find_element(By.TAG_NAME, "th").text.lower() == "options":
                    flag = True
                    continue
                else:
                    flag = False
            except NoSuchElementException:
                pass

            if flag:
                options_list.append(option.find_element(By.TAG_NAME, "td").text)
        self.df = self.df.append(
            {
                "name": title,
                "price": price,
                "options": options_list,
                "summary": summary_dict,
            },
            ignore_index=True,
        )

        self.df.rename(columns=self.columns, inplace=True)
        self.df.to_excel("result.xlsx")
        print("succesfully saved !")
