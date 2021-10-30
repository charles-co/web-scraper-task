"""Scrape.py
"""
import argparse
from urllib.parse import urlencode

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from extract import Extract


class Scrape(webdriver.Chrome):
    """Scrape"""

    timeout = 3
    params = {
        "body_style": "station%20wagon",
        "distance": None,
        "exterior_color_id": "",
        "make": "",
        "miles_max": "100000",
        "miles_min": "0",
        "model": "",
        "page_size": "24",
        "price_max": "100000",
        "price_min": "0",
        "query": "",
        "requestingPage": "buy",
        "sort": "desc",
        "sort_field": "updated",
        "status": "active",
        "year_end": "2022",
        "year_start": "1998",
        "zip": None,
    }

    def __init__(self, radius, zipcode, teardown=True):

        self.params.update({"distance": radius, "zip": zipcode})
        url = f"https://www.tred.com/buy?{urlencode(self.params)}"
        self.teardown = teardown
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("headless")
        super(Scrape, self).__init__(options=options)
        self.maximize_window()
        self.get(url)
        self.execute_script(
            "document.querySelector(`section[id='cars']`).scrollIntoView({ behavior: 'smooth', block: 'start'});"
        )
        try:
            WebDriverWait(self, self.timeout).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "section#cars div.inventory.car-item")
                )
            )
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.quit()

    def __exit__(self, *args) -> None:
        if not self.teardown:
            self.quit()

    def crawl(self):
        """Crawls the wep page till the last item is fetched,
        then starts extracting information
        """
        agg_no_cars = list()
        while True:
            wrapper = self.find_element(By.CSS_SELECTOR, "section#cars")
            try:
                inventory = wrapper.find_element(
                    By.CSS_SELECTOR, "div.inventory.car-item"
                )
            except NoSuchElementException:
                print("No element found")
                self.quit()

            cars = inventory.find_elements(By.CSS_SELECTOR, "div[class='card']")
            if agg_no_cars == cars:

                # n o more cars to fetch
                break
            agg_no_cars = cars
            print("scrolling")

            # page works with infinite scroll,
            # script to continue scrolling to bottome of view
            self.execute_script(
                "document.querySelector(`section[id='cars']`).scrollIntoView({ behavior: 'smooth', block: 'end'});"
            )  # execute the js scroll
            try:
                WebDriverWait(self, 2).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "section#cars div[class='hide']")
                    )
                )
            except TimeoutException:
                pass
        Extract(agg_no_cars)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-z", "--zipcode", type=str, help="Optional zipcode", default=""
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=str,
        help="Optional radius",
        default="50",
        choices=[str(x) for x in range(25, 501, 25)],
    )
    args = parser.parse_args()
    Scrape(getattr(args, "radius"), getattr(args, "zipcode"), teardown=False).crawl()
