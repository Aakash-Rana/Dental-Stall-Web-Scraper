# Dental-Stall-Web-Scraper

This project is a FastAPI-powered web scraper designed to extract product information (name, price, and images) from Dental Stall (https://dentalstall.com/shop/).

It leverages:
- Selenium for JavaScript-rendered pages
- BeautifulSoup for HTML parsing
- Redis for caching results
- JSON storage for local database

### STEPS

1. Clone the Repository
```
git clone https://github.com/yourusername/dental-scraper.git
cd dental-scraper
```

2. Install Dependencies
```
pip install -r requirements.txt
```
3. Install and Start Redis (Required for Caching)
```
brew install redis        # macOS (Homebrew)
sudo apt install redis    # Ubuntu

redis-server #redis-server
```
4. Run the FastAPI Server
```
uvicorn main:app --reload
```


Make a GET request to start scraping:
```
http://127.0.0.1:8000/scrape?token=your_secret_token&pages=3
```

Retrieve Stored Data

```
http://127.0.0.1:8000/products?token=your_secret_token
```
