import os
import json
import time
import redis
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By



class Scraper:
    BASE_URL = "https://dentalstall.com/shop/"

    def __init__(self, page_limit=5):
        self.page_limit = page_limit
        self.products = []
        self.setup_driver()
        self.setup_redis()

    def setup_driver(self):
        """Sets up Selenium WebDriver."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def setup_redis(self):
        """Initializes Redis connection."""
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def fetch_page(self, page_number, max_retries=3, initial_wait=3):
        """Loads the page using Selenium and retries if it fails."""
        url = f"{self.BASE_URL}page/{page_number}/"

        for attempt in range(max_retries):
            try:
                print(f" Fetching page {page_number}, Attempt {attempt + 1}/{max_retries}...")
                self.driver.get(url)
                time.sleep(5)

                for _ in range(5):
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)

                return self.driver.page_source

            except Exception as e:
                print(f"Error fetching page {page_number}: {e}")
                wait_time = initial_wait * (2 ** attempt) + 1
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        print(f" Failed to fetch page {page_number} after {max_retries} attempts.")
        return None

    # def parse_page(self, html):
    #     """Extracts product data and caches results in Redis."""
    #     soup = BeautifulSoup(html, "html.parser")
    #     product_cards = soup.find_all("div", class_="product-inner")

    #     print(f"Found {len(product_cards)} products on the page")

    #     for card in product_cards:
    #         title_tag = card.find("h2", class_="woo-loop-product__title")
    #         title = title_tag.text.strip() if title_tag else "No Title"

    #         price_tag = card.find("span", class_="woocommerce-Price-amount amount")
    #         price = price_tag.text.strip() if price_tag else "No Price"

    #         img_tag = card.find("div", class_="mf-product-thumbnail").find("img")
    #         img_url = img_tag.get("data-lazy-src") or img_tag.get("src") if img_tag else "No Image"

    #         if "data:image/svg+xml" in img_url:
    #             img_url = "No Image"


    #         cached_price = self.redis_client.get(title)
    #         if cached_price and cached_price == price:
    #             print(f"Skipping {title} - Price Unchanged ({price})")
    #             continue

    #         self.redis_client.set(title, price)
    #         img_path = self.download_image(img_url, title) if "http" in img_url else "No Image"

    #         self.products.append({
    #             "product_title": title,
    #             "product_price": price,
    #             "path_to_image": img_path,
    #         })

    def parse_page_with_full_text(self, html):
        """Extracts full product details by visiting each product page."""
        soup = BeautifulSoup(html, "html.parser")
        product_cards = soup.find_all("div", class_="product-inner")

        print(f"Found {len(product_cards)} products on the page")

        # Find all product links using Selenium
        selenium_product_links = self.driver.find_elements(By.CSS_SELECTOR, "h2.woo-loop-product__title a")

        for index, _ in enumerate(product_cards):
            try:
                product_link = selenium_product_links[index]  # Get the product link element
                product_url = product_link.get_attribute("href")  # Extract the URL

                print(f" Visiting product page: {product_url}")

                # Open product page
                self.driver.get(product_url)
                time.sleep(3)  # Allow the page to load fully

                # Extract full product title from the product details page
                try:
                    full_title_element = self.driver.find_element(By.CSS_SELECTOR, "h1.product_title")
                    full_title = full_title_element.text.strip()
                except Exception as e:
                    print(f"Could not extract full product title: {e}")
                    full_title = "No Title"

                print(f"Full Product Title: {full_title}")

                # Extract price from product page
                try:
                    price_element = self.driver.find_element(By.CSS_SELECTOR, "p.price span.woocommerce-Price-amount")
                    price = price_element.text.strip()
                except:
                    price = "No Price"

                # Extract image from product page
                try:
                    img_element = self.driver.find_element(By.CSS_SELECTOR, "div.woocommerce-product-gallery img")
                    img_url = img_element.get_attribute("src")
                except:
                    img_url = "No Image"

                # Go back to the main listing page
                self.driver.back()
                time.sleep(2)  # Wait for the page to reload

            except Exception as e:
                print(f"Error processing product {index + 1}: {e}")
                continue  # Skip to next product if there's an error

            # Check Redis cache for existing price
            cached_price = self.redis_client.get(full_title)

            if cached_price and cached_price == price:
                print(f"Skipping {full_title} - Price Unchanged ({price})")
                continue

            # Update Redis with new price
            self.redis_client.set(full_title, price)

            # Download image
            img_path = self.download_image(img_url, full_title) if "http" in img_url else "No Image"

            self.products.append({
                "product_title": full_title,
                "product_price": price,
                "path_to_image": img_path,
            })

    def download_image(self, url, title):
        """Downloads images only if they are valid URLs."""
        if url == "No Image":
            return "No Image"

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            filename = f"images/{title.replace(' ', '_')[:40]}.jpg"
            os.makedirs("images", exist_ok=True)

            with open(filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            print(f"Image saved: {filename}")
            return filename
        except requests.RequestException as e:
            print(f"Error downloading image {url}: {e}")
            return "No Image"

    def scrape(self):
        """Runs the scraping process."""
        for page in range(1, self.page_limit + 1):
            html = self.fetch_page(page)
            if html:
                self.parse_page_with_full_text(html)
            else:
                print(f"Skipping page {page} due to repeated failures.")
            time.sleep(2)

        self.save_to_json()
        print(f"Scraped {len(self.products)} new products.")

    def save_to_json(self):
        """ Saved scraped data to a JSON file."""
        with open("database.json", "w") as file:
            json.dump(self.products, file, indent=4)

    def close(self):
        """Closes the Selenium driver."""
        self.driver.quit()