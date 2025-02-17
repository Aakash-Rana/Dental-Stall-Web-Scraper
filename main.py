from fastapi import FastAPI, HTTPException
import json
from scraper import Scraper

app = FastAPI()

TOKEN = "your_secret_token"

def authenticate(token: str):
    ## Ensures API is protected.
    if token != TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/scrape")
def run_scraper(token: str, pages: int = 5):
    authenticate(token)

    scraper = Scraper(page_limit=pages)
    scraper.scrape()
    scraper.close()

    return {"message": f"Scraped {len(scraper.products)} products."}

@app.get("/products")
def get_products(token: str):
    authenticate(token)

    try:
        with open("database.json", "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"message": "No products found, run /scrape first"}