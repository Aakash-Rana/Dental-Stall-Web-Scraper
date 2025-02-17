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
git clone https://github.com/Aakash-Rana/Dental-Stall-Web-Scraper.git
cd ./Dental-Stall-Web-Scraper
```
2. Create environment (use python3 instead of python depending upon your version)
```
python -m venv venv
source venv/bin/activate #macOs/Linux
```
3. Install Dependencies
```
pip install -r requirements.txt
```
4. Install and Start Redis (Required for Caching)
```
brew install redis        # macOS (Homebrew)
sudo apt install redis    # Ubuntu

redis-server # Start redis-server
```
5. Run the FastAPI Server
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
